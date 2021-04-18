from .InstructionSet import *
from ..helpers import int_from_bytes, int_to_bytes, to_unsigned, to_signed


class RV32M(InstructionSet):
    def instruction_mul(self, ins: 'LoadedInstruction'):
        rd, rs1, rs2 = self.parse_rd_rs_rs(ins)
        self.regs.set(
            rd,
            rs1 * rs2
        )

    def instruction_mulh(self, ins: 'LoadedInstruction'):
        INS_NOT_IMPLEMENTED(ins)

    def instruction_mulhsu(self, ins: 'LoadedInstruction'):
        INS_NOT_IMPLEMENTED(ins)

    def instruction_mulhu(self, ins: 'LoadedInstruction'):
        INS_NOT_IMPLEMENTED(ins)

    def instruction_div(self, ins: 'LoadedInstruction'):
        rd, rs1, rs2 = self.parse_rd_rs_rs(ins)
        self.regs.set(
            rd,
            rs1 // rs2
        )

    def instruction_divu(self, ins: 'LoadedInstruction'):
        rd, rs1, rs2 = self.parse_rd_rs_rs(ins)
        rs1 = to_unsigned(rs1)
        rs2 = to_unsigned(rs2)
        self.regs.set(
            rd,
            rs1 // rs2
        )

    def instruction_rem(self, ins: 'LoadedInstruction'):
        rd, rs1, rs2 = self.parse_rd_rs_rs(ins)
        self.regs.set(
            rd,
            rs1 % rs2
        )

    def instruction_remu(self, ins: 'LoadedInstruction'):
        rd, rs1, rs2 = self.parse_rd_rs_rs(ins)
        rs1 = to_unsigned(rs1)
        rs2 = to_unsigned(rs2)
        self.regs.set(
            rd,
            rs1 % rs2
        )
