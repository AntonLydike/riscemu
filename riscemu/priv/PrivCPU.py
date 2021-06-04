"""
RiscEmu (c) 2021 Anton Lydike

SPDX-License-Identifier: MIT
"""
import time

from riscemu.CPU import *
from .CSR import CSR
from .ElfLoader import ElfExecutable
from .Exceptions import *
from .PrivMMU import PrivMMU
from .PrivRV32I import PrivRV32I
from .privmodes import PrivModes
from ..instructions.RV32M import RV32M

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

    def __init__(self, conf):
        super().__init__(conf, [PrivRV32I, RV32M])
        self.mode: PrivModes = PrivModes.MACHINE

        kernel = ElfExecutable('kernel')
        self.mmu = PrivMMU(kernel)
        self.pc = kernel.run_ptr
        self.syscall_int = None

        self.launch_debug = False

        self.pending_traps: List[CpuTrap] = list()

        self._time_start = 0
        self._time_timecmp = 0
        self._time_interrupt_enabled = False

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
                print(FMT_ERROR + "[CPU] excpetion caught at 0x{:08X}: {}:".format(self.pc - 1, ins) + FMT_NONE)
                print(ex.message())
                if self.conf.debug_on_exception:
                    self.launch_debug = True
        if self.exit:
            print()
            print(FMT_CPU + "Program exited with code {}".format(self.exit_code) + FMT_NONE)
            sys.exit(self.exit_code)
        elif self.launch_debug:
            launch_debug_session(self, self.mmu, self.regs,
                                 "Launching debugger:")
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

    def run(self):
        print(FMT_CPU + '[CPU] Started running from 0x{:08X} ({})'.format(self.pc, "kernel") + FMT_NONE)
        self._time_start = time.perf_counter_ns() // self.TIME_RESOLUTION_NS
        self._run(True)

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
        def mtimecmp(old, new):
            self._time_timecmp = (new << 32) + self.csr.get('mtimecmp')
            self._time_interrupt_enabled = True

        # virtual CSR registers:

        @self.csr.virtual_register('time')
        def get_time():
            return (time.perf_counter_ns() // self.TIME_RESOLUTION_NS) & (2 ** 32 - 1)

        @self.csr.virtual_register('timeh')
        def get_timeh():
            return (time.perf_counter_ns() // self.TIME_RESOLUTION_NS) >> 32

        # add minstret and mcycle counters

    def _handle_trap(self, trap: CpuTrap):
        # implement trap handling!
        self.pending_traps.append(trap)

    def step(self, verbose = True):
        try:
            self.cycle += 1
            self._timer_step()
            self._check_interrupt()
            ins = self.mmu.read_ins(self.pc)
            if verbose:
                print(FMT_CPU + "   Running 0x{:08X}:{} {}".format(self.pc, FMT_NONE, ins))
            self.run_instruction(ins)
            self.pc += self.INS_XLEN
        except CpuTrap as trap:
            self._handle_trap(trap)

    def _timer_step(self):
        if not self._time_interrupt_enabled:
            return
        if self._time_timecmp < (time.perf_counter_ns() // self.TIME_RESOLUTION_NS) - self._time_start:
            self.pending_traps.append(TimerInterrupt())
            self._time_interrupt_enabled = False

    def _check_interrupt(self):
        pass
