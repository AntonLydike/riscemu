"""
RiscEmu (c) 2023 Anton Lydike

SPDX-License-Identifier: MIT

This file contains copious amounts of docstrings that were all taken
from https://msyksphinz-self.github.io/riscv-isadoc/html/rvfd.html
(all the docstrings on the instruction methods documenting the opcodes
and their function)
"""
from .instruction_set import Instruction
from .float_base import FloatArithBase
from riscemu.core import Float32, Int32, UInt32


class RV32F(FloatArithBase[Float32]):
    flen = 32
    _float_cls = Float32

    def instruction_fcvt_w_s(self, ins: Instruction):
        """
        +-----+-----+-----+-----+-----+-----+-----+---+
        |31-27|26-25|24-20|19-15|14-12|11-7 |6-2  |1-0|
        +-----+-----+-----+-----+-----+-----+-----+---+
        |11000|00   |00000|rs1  |rm   |rd   |10100|11 |
        +-----+-----+-----+-----+-----+-----+-----+---+

        :Format:
        | fcvt.w.s   rd,rs1

        :Description:
        | Convert a floating-point number in floating-point register rs1 to a signed 32-bit in integer register rd.

        :Implementation:
        | x[rd] = sext(s32_{f32}(f[rs1]))
        """
        rd, rs = self.parse_rd_rs(ins)
        self.regs.set(rd, Int32(int(self.regs.get_f(rs).value)))

    def instruction_fcvt_wu_s(self, ins: Instruction):
        """
        +-----+-----+-----+-----+-----+-----+-----+---+
        |31-27|26-25|24-20|19-15|14-12|11-7 |6-2  |1-0|
        +-----+-----+-----+-----+-----+-----+-----+---+
        |11000|00   |00001|rs1  |rm   |rd   |10100|11 |
        +-----+-----+-----+-----+-----+-----+-----+---+

        :Format:
        | fcvt.wu.s  rd,rs1

        :Description:
        | Convert a floating-point number in floating-point register rs1 to a signed 32-bit in unsigned integer register rd.

        :Implementation:
        | x[rd] = sext(u32_{f32}(f[rs1]))
        """
        rd, rs = self.parse_rd_rs(ins)
        self.regs.set(rd, UInt32(int(self.regs.get_f(rs).value)))

    def instruction_fmv_x_w(self, ins: Instruction):
        """
        +-----+-----+-----+-----+-----+-----+-----+---+
        |31-27|26-25|24-20|19-15|14-12|11-7 |6-2  |1-0|
        +-----+-----+-----+-----+-----+-----+-----+---+
        |11100|00   |00000|rs1  |000  |rd   |10100|11 |
        +-----+-----+-----+-----+-----+-----+-----+---+

        :Format:
        | fmv.x.w    rd,rs1

        :Description:
        | Move the single-precision value in floating-point register rs1 represented in IEEE 754-2008 encoding to the lower 32 bits of integer register rd.

        :Implementation:
        | x[rd] = sext(f[rs1][31:0])
        """
        rd, rs = self.parse_rd_rs(ins)
        self.regs.set(rd, UInt32(self.regs.get_f(rs).bytes[-4:]))

    def instruction_fcvt_s_w(self, ins: Instruction):
        """
        +-----+-----+-----+-----+-----+-----+-----+---+
        |31-27|26-25|24-20|19-15|14-12|11-7 |6-2  |1-0|
        +-----+-----+-----+-----+-----+-----+-----+---+
        |11010|00   |00000|rs1  |rm   |rd   |10100|11 |
        +-----+-----+-----+-----+-----+-----+-----+---+

        :Format:
        | fcvt.s.w   rd,rs1

        :Description:
        | Converts a 32-bit signed integer, in integer register rs1 into a floating-point number in floating-point register rd.

        :Implementation:
        | f[rd] = f32_{s32}(x[rs1])
        """
        rd, rs = self.parse_rd_rs(ins)
        self.regs.set_f(rd, Float32(self.regs.get(rs).signed().value))

    def instruction_fcvt_s_wu(self, ins: Instruction):
        """
        +-----+-----+-----+-----+-----+-----+-----+---+
        |31-27|26-25|24-20|19-15|14-12|11-7 |6-2  |1-0|
        +-----+-----+-----+-----+-----+-----+-----+---+
        |11010|00   |00001|rs1  |rm   |rd   |10100|11 |
        +-----+-----+-----+-----+-----+-----+-----+---+

        :Format:
        | fcvt.s.wu  rd,rs1

        :Description:
        | Converts a 32-bit unsigned integer, in integer register rs1 into a floating-point number in floating-point register rd.

        :Implementation:
        | f[rd] = f32_{u32}(x[rs1])
        """
        rd, rs = self.parse_rd_rs(ins)
        self.regs.set_f(rd, Float32(self.regs.get(rs).unsigned_value))

    def instruction_fmv_w_x(self, ins: Instruction):
        """
        +-----+-----+-----+-----+-----+-----+-----+---+
        |31-27|26-25|24-20|19-15|14-12|11-7 |6-2  |1-0|
        +-----+-----+-----+-----+-----+-----+-----+---+
        |11110|00   |00000|rs1  |000  |rd   |10100|11 |
        +-----+-----+-----+-----+-----+-----+-----+---+



        :Format:
        | fmv.w.x    rd,rs1

        :Description:
        | Move the single-precision value encoded in IEEE 754-2008 standard encoding from the lower 32 bits of integer register rs1 to the floating-point register rd.

        :Implementation:
        | f[rd] = x[rs1][31:0]
        """
        rd, rs = self.parse_rd_rs(ins)
        self.regs.set_f(rd, Float32.from_bytes(self.regs.get(rs).to_bytes()))
