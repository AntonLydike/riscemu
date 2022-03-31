"""
RiscEmu (c) 2021 Anton Lydike

SPDX-License-Identifier: MIT
"""
import sys
import time

from riscemu.CPU import *
from .CSR import CSR
from .ElfLoader import ElfBinaryFileLoader
from .Exceptions import *
from .ImageLoader import MemoryImageLoader
from .PrivMMU import PrivMMU
from .PrivRV32I import PrivRV32I
from .privmodes import PrivModes
from ..IO.TextIO import TextIO
from ..instructions import RV32A, RV32M
from ..types import Program, UInt32

if typing.TYPE_CHECKING:
    from riscemu.instructions.instruction_set import InstructionSet


class PrivCPU(CPU):
    """
    This is a CPU that has different modes, instruction sets and registers.

    It should support M and U Mode, but no U-Mode Traps.

    This is meant to emulate whole operating systems.
    """

    csr: CSR
    """
    Reference to the control and status registers
    """

    TIME_RESOLUTION_NS: int = 10000000
    """
    controls the resolution of the time csr register (in nanoseconds)
    """

    pending_traps: List[CpuTrap]
    """
    A list of traps which are pending to be handled
    """

    def __init__(self, conf):
        super().__init__(PrivMMU(), [PrivRV32I, RV32M, RV32A], conf)
        # start in machine mode
        self.mode: PrivModes = PrivModes.MACHINE

        self.pending_traps: List[CpuTrap] = list()

        self.exit_code = 0

        self._time_start = 0
        self._time_timecmp = UInt32(0)
        self._time_interrupt_enabled = False

        # performance counters
        self._perf_counters = list()

        # add TextIO
        io = TextIO(0xFF0000, 64)
        self.mmu.load_section(io, True)

        # init csr
        self._init_csr()

        self.TIME_RESOLUTION_NS = int(self.TIME_RESOLUTION_NS * conf.slowdown)

    def run(self, verbose=False):
        if self.pc <= 0:
            return False

        launch_debug = False

        try:
            while not self.halted:
                self.step(verbose)
        except RiscemuBaseException as ex:
            if isinstance(ex, LaunchDebuggerException):
                launch_debug = True
                self.pc += self.INS_XLEN

        if self.halted:
            print()
            print(FMT_CPU + "[CPU] System halted with code {}".format(self.exit_code) + FMT_NONE)
            sys.exit(self.exit_code)

        elif launch_debug:
            launch_debug_session(self)
            if not self.debugger_active:
                self.run(verbose)
        else:
            print()
            print(FMT_CPU + "[CPU] System stopped without halting - perhaps you stopped the debugger?" + FMT_NONE)

    def launch(self, program: Optional[Program] = None, verbose: bool = False):
        print(FMT_CPU + '[CPU] Started running from 0x{:08X} ({})'.format(self.pc, "kernel") + FMT_NONE)
        self._time_start = time.perf_counter_ns() // self.TIME_RESOLUTION_NS

        self.run(self.conf.verbosity > 1 or verbose)

    def load_program(self, program: Program):
        if program.name == 'kernel':
            self.pc = program.entrypoint
        super().load_program(program)

    def _init_csr(self):
        # set up CSR
        self.csr = CSR()
        self.csr.set('mhartid', UInt32(0))  # core id
        # TODO: set correct value
        self.csr.set('mimpid', UInt32(0))  # implementation id
        # set mxl to 1 (32 bit) and set bits for i and m isa
        self.csr.set('misa', UInt32((1 << 30) + (1 << 8) + (1 << 12)))  # available ISA

        # CSR write callbacks:

        @self.csr.callback('halt')
        def halt(old: UInt32, new: UInt32):
            if new != 0:
                self.halted = True
                self.exit_code = new.value

        @self.csr.callback('mtimecmp')
        def mtimecmp(old: UInt32, new: UInt32):
            self._time_timecmp = (self.csr.get('mtimecmph') << 32) + new
            self._time_interrupt_enabled = True

        @self.csr.callback('mtimecmph')
        def mtimecmph(old: UInt32, new: UInt32):
            self._time_timecmp = (new << 32) + self.csr.get('mtimecmp')
            self._time_interrupt_enabled = True

        # virtual CSR registers:

        @self.csr.virtual_register('time')
        def get_time():
            return UInt32(time.perf_counter_ns() // self.TIME_RESOLUTION_NS - self._time_start)

        @self.csr.virtual_register('timeh')
        def get_timeh():
            return UInt32((time.perf_counter_ns() // self.TIME_RESOLUTION_NS - self._time_start) >> 32)

        # add minstret and mcycle counters

    def _handle_trap(self, trap: CpuTrap):
        # implement trap handling!
        self.pending_traps.append(trap)

    def step(self, verbose=True):
        try:
            self.cycle += 1
            if self.cycle % 20 == 0:
                self._timer_step()
            self._check_interrupt()
            ins = self.mmu.read_ins(self.pc)
            if verbose and (self.mode == PrivModes.USER or self.conf.verbosity > 4):
                print(FMT_CPU + "   Running 0x{:08X}:{} {}".format(self.pc, FMT_NONE, ins))
            self.run_instruction(ins)
            self.pc += self.INS_XLEN
        except CpuTrap as trap:
            self._handle_trap(trap)
            if trap.interrupt == 0 and not isinstance(trap, EcallTrap):
                print(FMT_CPU + "[CPU] Trap {} encountered at {} (0x{:x})".format(
                    trap,
                    self.mmu.translate_address(self.pc),
                    self.pc
                ) + FMT_NONE)
                breakpoint()
                if self.conf.debug_on_exception:
                    raise LaunchDebuggerException()
            self.pc += self.INS_XLEN

    def _timer_step(self):
        if not self._time_interrupt_enabled:
            return
        if self._time_timecmp <= (time.perf_counter_ns() // self.TIME_RESOLUTION_NS) - self._time_start:
            self.pending_traps.append(TimerInterrupt())
            self._time_interrupt_enabled = False

    def _check_interrupt(self):
        if not (len(self.pending_traps) > 0 and self.csr.get_mstatus('mie')):
            return
        # select best interrupt
        # FIXME: actually select based on the official ranking
        trap = self.pending_traps.pop()  # use the most recent trap
        if self.conf.verbosity > 0:
            print(FMT_CPU + "[CPU] taking trap {}!".format(trap) + FMT_NONE)
            self.regs.dump_reg_a()

        if trap.priv != PrivModes.MACHINE:
            print(FMT_CPU + "[CPU] Trap not targeting machine mode encountered! - undefined behaviour!" + FMT_NONE)
            raise Exception("Undefined behaviour!")

        if self.mode != PrivModes.USER:
            print(FMT_CPU + "[CPU] Trap triggered outside of user mode?!" + FMT_NONE)

        self.csr.set_mstatus('mpie', self.csr.get_mstatus('mie'))
        self.csr.set_mstatus('mpp', self.mode.value)
        self.csr.set_mstatus('mie', UInt32(0))
        self.csr.set('mcause', trap.mcause)
        self.csr.set('mepc', self.pc - self.INS_XLEN)
        self.csr.set('mtval', trap.mtval)
        self.mode = trap.priv
        mtvec = self.csr.get('mtvec')
        if mtvec & 0b11 == 0:
            self.pc = mtvec.value
        if mtvec & 0b11 == 1:
            self.pc = ((mtvec & 0b11111111111111111111111111111100) + (trap.code * 4)).value
        self.record_perf_profile()
        if len(self._perf_counters) > 100:
            self.show_perf()

    def show_perf(self):
        timed = 0
        cycled = 0
        cps_list = list()

        print(FMT_CPU + "[CPU] Performance overview:")
        for time_ns, cycle in self._perf_counters:
            if cycled == 0:
                cycled = cycle
                timed = time_ns
                continue
            cps = (cycle - cycled) / (time_ns - timed) * 1000000000

            cycled = cycle
            timed = time_ns
            cps_list.append(cps)
        print("    on average {:.0f} instructions/s".format(sum(cps_list) / len(cps_list)) + FMT_NONE)
        self._perf_counters = list()

    def record_perf_profile(self):
        self._perf_counters.append((time.perf_counter_ns(), self.cycle))

    @classmethod
    def get_loaders(cls) -> typing.Iterable[Type[ProgramLoader]]:
        return [
            AssemblyFileLoader, MemoryImageLoader, ElfBinaryFileLoader
        ]
