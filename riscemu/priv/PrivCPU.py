"""
RiscEmu (c) 2021 Anton Lydike

SPDX-License-Identifier: MIT
"""

from riscemu.CPU import *
from enum import IntEnum
from riscemu.Executable import LoadedMemorySection
from .Exceptions import *
from .CSR import CSR
from .PrivRV32I import PrivRV32I
from ..instructions.RV32M import RV32M
from .PrivMMU import PrivMMU
from .ElfLoader import ElfExecutable
from .privmodes import PrivModes

from collections import defaultdict

from typing import Union

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

    INS_XLEN = 4
    """
    Size of an instruction in memory. Should be 4, but since our loading code is shit, instruction take up 
    the equivalent of "1 byte" (this is actually impossible)
    """

    def __init__(self, conf):
        super().__init__(conf, [PrivRV32I, RV32M])
        self.mode: PrivModes = PrivModes.MACHINE

        exec = ElfExecutable('kernel')
        self.mmu = PrivMMU(exec)
        self.pc = exec.run_ptr
        self.syscall_int = None

        # set up CSR
        self.csr = CSR()
        # TODO: Actually populate the CSR with real data (vendorID, heartID, machine implementation etc)
        self.csr.set('mhartid', 0)  # core id
        self.csr.set('mimpid', 1)  # implementation id
        # TODO: set correct misa
        self.csr.set('misa', 1)  # available ISA

    def _run(self, verbose=False):
        if self.pc <= 0:
            return False
        ins = None
        try:
            while not self.exit:
                try:
                    self.cycle += 1
                    ins = self.mmu.read_ins(self.pc)
                    if verbose:
                        print(FMT_CPU + "   Running 0x{:08X}:{} {}".format(self.pc, FMT_NONE, ins))
                    self.run_instruction(ins)
                    self.pc += self.INS_XLEN
                except CpuTrap as trap:
                    mie = self.csr.get_mstatus('mie')
                    if not mie:
                        print("Caught trap while mie={}!".format(mie))
                        # TODO: handle this a lot better
                        continue
                        # raise trap

                    # caught a trap!
                    self.csr.set('mepc', self.pc)  # store MEPC
                    self.csr.set_mstatus('mpp', self.mode)  # save mpp
                    self.csr.set_mstatus('mpie', mie)  # save mie
                    self.csr.set_mstatus('mie', 0)  # disable further interrupts
                    self.csr.set('mcause', trap.mcause)  # store cause

                    # set mtval csr
                    self.csr.set('mtval', trap.mtval)

                    # set priv mode to machine
                    self.mode = PrivModes.MACHINE

                    # trap vector
                    mtvec = self.csr.get('mtvec')
                    if mtvec & 3 == 1:
                        # vectored mode!
                        self.pc = (mtvec >> 2) + (self.INS_XLEN * trap.code)
                    else:
                        # standard mode
                        self.pc = (mtvec >> 2)
        except RiscemuBaseException as ex:
            if not isinstance(ex, LaunchDebuggerException):
                print(FMT_ERROR + "[CPU] excpetion caught at 0x{:08X}: {}:".format(self.pc - 1, ins) + FMT_NONE)
                print(ex.message())
                self.pc -= 1

            if self.active_debug:
                print(FMT_CPU + "[CPU] Returning to debugger!" + FMT_NONE)
                return
            if self.conf.debug_on_exception:
                launch_debug_session(self, self.mmu, self.regs,
                                     "Exception encountered, launching debug:")

        if self.exit:
            print()
            print(FMT_CPU + "Program exited with code {}".format(self.exit_code) + FMT_NONE)
            sys.exit(self.exit_code)
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
        self._run(True)

