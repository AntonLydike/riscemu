"""
RiscEmu (c) 2021 Anton Lydike

SPDX-License-Identifier: MIT
"""

from .instruction_set import *
from riscemu.types.exceptions import INS_NOT_IMPLEMENTED


class RV32M(InstructionSet):
    """
    The RV32M Instruction set, containing multiplication and division instructions
    """
    def instruction_mul(self, ins: 'Instruction'):
        rd, rs1, rs2 = self.parse_rd_rs_rs(ins)
        self.regs.set(
            rd,
            rs1 * rs2
        )

    def instruction_mulh(self, ins: 'Instruction'):
        rd, rs1, rs2 = self.parse_rd_rs_rs(ins)
        self.regs.set(
            rd,
            (rs1 * rs2) >> 32
        )

    def instruction_mulhsu(self, ins: 'Instruction'):
        INS_NOT_IMPLEMENTED(ins)

    def instruction_mulhu(self, ins: 'Instruction'):
        INS_NOT_IMPLEMENTED(ins)

    def instruction_div(self, ins: 'Instruction'):
        rd, rs1, rs2 = self.parse_rd_rs_rs(ins)
        self.regs.set(
            rd,
            rs1 // rs2
        )

    def instruction_divu(self, ins: 'Instruction'):
        rd, rs1, rs2 = self.parse_rd_rs_rs(ins, signed=False)
        self.regs.set(
            rd,
            rs1 // rs2
        )

    def instruction_rem(self, ins: 'Instruction'):
        rd, rs1, rs2 = self.parse_rd_rs_rs(ins)
        self.regs.set(
            rd,
            rs1 % rs2
        )

    def instruction_remu(self, ins: 'Instruction'):
        rd, rs1, rs2 = self.parse_rd_rs_rs(ins, signed=False)
        self.regs.set(
            rd,
            rs1 % rs2
        )
