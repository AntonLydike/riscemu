"""
RiscEmu (c) 2021 Anton Lydike

SPDX-License-Identifier: MIT
"""
import time

from riscemu.CPU import *
from .CSR import CSR
from .ElfLoader import ElfExecutable
from .ImageLoader import MemoryImageMMU
from .Exceptions import *
from .PrivMMU import PrivMMU
from ..IO import TextIO
from .PrivRV32I import PrivRV32I
from .privmodes import PrivModes
from ..instructions import RV32A, RV32M
import json

if typing.TYPE_CHECKING:
    from riscemu import Executable, LoadedExecutable, LoadedInstruction
    from riscemu.instructions.InstructionSet import InstructionSet


class PrivCPU(CPU):
    """
    This is a CPU that has different modes, instruction sets and registers.

    It should support M and U Mode, but no U-Mode Traps.

    This allows us to
    """

    csr: CSR
    """
    Reference to the control and status registers
    """

    TIME_RESOLUTION_NS: int = 1000000
    """
    controls the resolution of the time csr register (in nanoseconds)
    """

    INS_XLEN = 4
    """
    Size of an instruction in memory. Should be 4, but since our loading code is shit, instruction take up 
    the equivalent of "1 byte" (this is actually impossible)
    """

    def __init__(self, conf, mmu: PrivMMU):
        super().__init__(conf, [PrivRV32I, RV32M, RV32A])
        self.mode: PrivModes = PrivModes.MACHINE

        mmu.set_cpu(self)
        self.pc = mmu.get_entrypoint()
        self.mmu = mmu

        if hasattr(self.mmu, 'add_io'):
            self.mmu.add_io(TextIO.TextIO(0xff0000, 64))

        self.syscall_int = None
        self.launch_debug = False
        self.pending_traps: List[CpuTrap] = list()

        self._time_start = 0
        self._time_timecmp = 0
        self._time_interrupt_enabled = False

        # performance counters
        self._perf_counters = list()

        # init csr
        self._init_csr()

    def _run(self, verbose=False):
        if self.pc <= 0:
            return False
        ins = None
        try:
            while not self.exit:
                self.step(verbose)
        except RiscemuBaseException as ex:
            if isinstance(ex, LaunchDebuggerException):
                self.launch_debug = True
                self.pc += self.INS_XLEN
            else:
                print(FMT_ERROR + "[CPU] exception caught at 0x{:08X}: {}:".format(self.pc - 1, ins) + FMT_NONE)
                print(ex.message())
                if self.conf.debug_on_exception:
                    self.launch_debug = True
        if self.exit:
            print()
            print(FMT_CPU + "Program exited with code {}".format(self.exit_code) + FMT_NONE)
            sys.exit(self.exit_code)
        elif self.launch_debug:
            self.launch_debug = False
            launch_debug_session(self, self.mmu, self.regs,
                                 "Launching debugger:")
            if not self.active_debug:
                self._run(verbose)
        else:
            print()
            print(FMT_CPU + "Program stopped without exiting - perhaps you stopped the debugger?" + FMT_NONE)

    def load(self, e: riscemu.Executable):
        raise NotImplementedError("Not supported!")

    def run_loaded(self, le: 'riscemu.LoadedExecutable'):
        raise NotImplementedError("Not supported!")

    def get_tokenizer(self, tokenizer_input):
        raise NotImplementedError("Not supported!")

    def run(self, verbose: bool = False):
        print(FMT_CPU + '[CPU] Started running from 0x{:08X} ({})'.format(self.pc, "kernel") + FMT_NONE)
        self._time_start = time.perf_counter_ns() // self.TIME_RESOLUTION_NS
        self._run(verbose)

    def _init_csr(self):
        # set up CSR
        self.csr = CSR()
        self.csr.set('mhartid', 0)  # core id
        # TODO: set correct value
        self.csr.set('mimpid', 0)  # implementation id
        # set mxl to 1 (32 bit) and set bits for i and m isa
        self.csr.set('misa', (1 << 30) + (1 << 8) + (1 << 12))  # available ISA

        # CSR write callbacks:

        @self.csr.callback('halt')
        def halt(old: int, new: int):
            if new != 0:
                self.exit = True
                self.exit_code = new

        @self.csr.callback('mstatus')
        def mstatus(old: int, new: int):
            pass

        @self.csr.callback('mtimecmp')
        def mtimecmp(old, new):
            self._time_timecmp = (self.csr.get('mtimecmph') << 32) + new
            self._time_interrupt_enabled = True

        @self.csr.callback('mtimecmph')
        def mtimecmph(old, new):
            self._time_timecmp = (new << 32) + self.csr.get('mtimecmp')
            self._time_interrupt_enabled = True

        # virtual CSR registers:

        @self.csr.virtual_register('time')
        def get_time():
            return (time.perf_counter_ns() // self.TIME_RESOLUTION_NS - self._time_start) & (2 ** 32 - 1)

        @self.csr.virtual_register('timeh')
        def get_timeh():
            return (time.perf_counter_ns() // self.TIME_RESOLUTION_NS - self._time_start) >> 32

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
            if verbose and self.mode == PrivModes.USER:
                print(FMT_CPU + "   Running 0x{:08X}:{} {}".format(self.pc, FMT_NONE, ins))
            self.run_instruction(ins)
            self.pc += self.INS_XLEN
        except CpuTrap as trap:
            self._handle_trap(trap)

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
        # TODO: actually select based on the official ranking
        trap = self.pending_traps.pop()  # use the most recent trap
        if not isinstance(trap, TimerInterrupt) or True:
            print(FMT_CPU + "[CPU] [{}] taking trap {}!".format(self.cycle, trap) + FMT_NONE)

        if trap.priv != PrivModes.MACHINE:
            print(FMT_CPU + "[CPU] Trap not targeting machine mode encountered! - undefined behaviour!" + FMT_NONE)
            raise Exception("Undefined behaviour!")

        if self.mode != PrivModes.USER:
            print(FMT_CPU + "[CPU] Trap triggered outside of user mode?!" + FMT_NONE)

        self.csr.set_mstatus('mpie', self.csr.get_mstatus('mie'))
        self.csr.set_mstatus('mpp', self.mode.value)
        self.csr.set_mstatus('mie', 0)
        self.csr.set('mcause', trap.mcause)
        self.csr.set('mepc', self.pc-self.INS_XLEN)
        self.csr.set('mtval', trap.mtval)
        self.mode = trap.priv
        mtvec = self.csr.get('mtvec')
        if mtvec & 0b11 == 0:
            self.pc = mtvec
        if mtvec & 0b11 == 1:
            self.pc = (mtvec & 0b11111111111111111111111111111100) + (trap.code * 4)
        self.record_perf_profile()
        if len(self._perf_counters) % 100 == 0:
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

            # print("    {:03d} cycles in {:08d}ns ({:.2f} cycles/s)".format(
            #    cycle - cycled,
            #    time_ns - timed,
            #    cps
            # ))
            cycled = cycle
            timed = time_ns
            cps_list.append(cps)
        print("    on average {:.0f} instructions/s".format(sum(cps_list) / len(cps_list)) + FMT_NONE)
        self._perf_counters = list()

    def record_perf_profile(self):
        self._perf_counters.append((time.perf_counter_ns(), self.cycle))
