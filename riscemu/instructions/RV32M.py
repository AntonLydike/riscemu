"""
RiscEmu (c) 2021 Anton Lydike

SPDX-License-Identifier: MIT
"""

from .instruction_set import *


class RV32M(InstructionSet):
    """
    The RV32M Instruction set, containing multiplication and division instructions
    """

    def instruction_mul(self, ins: "Instruction"):
        rd, rs1, rs2 = self.parse_rd_rs_rs(ins)
        self.regs.set(rd, rs1 * rs2)

    def instruction_mulh(self, ins: "Instruction"):
        rd, rs1, rs2 = self.parse_rd_rs_rs(ins)
        self.regs.set(rd, Int32((rs1.signed().value * rs2.signed().value) >> 32))

    def instruction_mulhsu(self, ins: "Instruction"):
        rd, rs1, rs2 = self.parse_rd_rs_rs(ins)
        self.regs.set(rd, Int32((rs1.signed().value * rs2.unsigned_value) >> 32))

    def instruction_mulhu(self, ins: "Instruction"):
        rd, rs1, rs2 = self.parse_rd_rs_rs(ins)
        self.regs.set(rd, UInt32((rs1.unsigned_value * rs2.unsigned_value) >> 32))

    def instruction_div(self, ins: "Instruction"):
        rd, rs1, rs2 = self.parse_rd_rs_rs(ins)
        self.regs.set(rd, rs1 // rs2)

    def instruction_divu(self, ins: "Instruction"):
        rd, rs1, rs2 = self.parse_rd_rs_rs(ins, signed=False)
        self.regs.set(rd, rs1 // rs2)

    def instruction_rem(self, ins: "Instruction"):
        rd, rs1, rs2 = self.parse_rd_rs_rs(ins)
        self.regs.set(rd, rs1 % rs2)

    def instruction_remu(self, ins: "Instruction"):
        rd, rs1, rs2 = self.parse_rd_rs_rs(ins, signed=False)
        self.regs.set(rd, rs1 % rs2)
