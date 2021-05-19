"""
RiscEmu (c) 2021 Anton Lydike

SPDX-License-Identifier: MIT
"""

from riscemu.instructions.RV32I import *
from ..Exceptions import INS_NOT_IMPLEMENTED
from riscemu.priv.PrivCPU import PrivModes, PrivCPU
from .Exceptions import *


class PrivRV32I(RV32I):
    cpu: PrivCPU
    """
    This is an extension of RV32I, written for the PrivCPU class
    """

    def instruction_csrrw(self, ins: 'LoadedInstruction'):
        rd, off, rs = self.parse_crs_ins(ins)
        if rd != 'zero':
            old_val = int_from_bytes(self.cpu.csr.read(off, 4))
            self.regs.set(rd, old_val)
        self.cpu.csr.write(off, 4, int_to_bytes(rs))

    def instruction_csrrs(self, ins: 'LoadedInstruction'):
        INS_NOT_IMPLEMENTED(ins)

    def instruction_csrrc(self, ins: 'LoadedInstruction'):
        INS_NOT_IMPLEMENTED(ins)

    def instruction_csrrsi(self, ins: 'LoadedInstruction'):
        INS_NOT_IMPLEMENTED(ins)

    def instruction_csrrwi(self, ins: 'LoadedInstruction'):
        INS_NOT_IMPLEMENTED(ins)

    def instruction_csrrci(self, ins: 'LoadedInstruction'):
        INS_NOT_IMPLEMENTED(ins)

    def instruction_mret(self, ins: 'LoadedInstruction'):
        if self.cpu.mode != PrivModes.MACHINE:
            print("MRET not inside machine level code!")
            raise IllegalInstructionTrap()
        # retore mie
        mpie = self.cpu.csr.get_mstatus('mpie')
        self.cpu.csr.set_mstatus('mie', mpie)
        # restore priv
        mpp = self.cpu.csr.get_mstatus('mpp')
        self.cpu.mode = PrivModes(mpp)
        # restore pc
        mepc = self.cpu.csr.get('mepc')
        self.cpu.pc = mepc

    def instruction_uret(self, ins: 'LoadedInstruction'):
        raise IllegalInstructionTrap()

    def instruction_sret(self, ins: 'LoadedInstruction'):
        raise IllegalInstructionTrap()

    def instruction_scall(self, ins: 'LoadedInstruction'):
        """
        Overwrite the scall from userspace RV32I
        """
        if self.cpu.mode == PrivModes.USER:
            raise CpuTrap(0, 8)         # ecall from U mode
        elif self.cpu.mode == PrivModes.SUPER:
            raise CpuTrap(0, 9)         # ecall from S mode - should not happen
        elif self.cpu.mode == PrivModes.MACHINE:
            raise CpuTrap(0, 11)        # ecall from M mode






    def parse_crs_ins(self, ins: 'LoadedInstruction'):
        ASSERT_LEN(ins.args, 3)
        return ins.get_reg(0), ins.get_imm(1), self.get_reg_content(ins, 2)
