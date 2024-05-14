"""
RiscEmu (c) 2023 Anton Lydike

SPDX-License-Identifier: MIT

This file contains copious amounts of docstrings that were all taken
from https://msyksphinz-self.github.io/riscv-isadoc/html/rvfd.html
(all the docstrings on the instruction methods documenting the opcodes
and their function)
"""
from typing import Tuple

from .instruction_set import InstructionSet, Instruction
from .float_base import FloatArithBase
from riscemu.core import INS_NOT_IMPLEMENTED, Float32, Int32, UInt32, Float64


class RV32D(FloatArithBase[Float64]):
    flen = 64
    _float_cls = Float64

    def instruction_fcvt_d_w(self, ins: Instruction):
        """
        +-----+-----+-----+-----+-----+-----+-----+---+
        |31-27|26-25|24-20|19-15|14-12|11-7 |6-2  |1-0|
        +-----+-----+-----+-----+-----+-----+-----+---+
        |11010|01   |00000|rs1  |rm   |rd   |10100|11 |
        +-----+-----+-----+-----+-----+-----+-----+---+

        :Format:
          | fcvt.d.w   rd,rs1

        :Description:
          | Converts a 32-bit signed integer, in integer register rs1 into a double-precision floating-point number in floating-point register rd.

        :Implementation:
          | x[rd] = sext(s32_{f64}(f[rs1]))
        """
        rd, rs = self.parse_rd_rs(ins)
        self.regs.set_f(rd, Float64(self.regs.get(rs).value))

    def instruction_fcvt_d_wu(self, ins: Instruction):
        """
        +-----+-----+-----+-----+-----+-----+-----+---+
        |31-27|26-25|24-20|19-15|14-12|11-7 |6-2  |1-0|
        +-----+-----+-----+-----+-----+-----+-----+---+
        |11010|01   |00001|rs1  |rm   |rd   |10100|11 |
        +-----+-----+-----+-----+-----+-----+-----+---+

        :Format:
          | fcvt.d.wu  rd,rs1

        :Description:
          | Converts a 32-bit unsigned integer, in integer register rs1 into a double-precision floating-point number in floating-point register rd.

        :Implementation:
          | f[rd] = f64_{u32}(x[rs1])
        """
        rd, rs = self.parse_rd_rs(ins)
        self.regs.set_f(rd, Float64(self.regs.get(rs).unsigned_value))

    def instruction_fcvt_w_d(self, ins: Instruction):
        """
        +-----+-----+-----+-----+-----+-----+-----+---+
        |31-27|26-25|24-20|19-15|14-12|11-7 |6-2  |1-0|
        +-----+-----+-----+-----+-----+-----+-----+---+
        |11000|01   |00000|rs1  |rm   |rd   |10100|11 |
        +-----+-----+-----+-----+-----+-----+-----+---+

        :Format:
          | fcvt.w.d   rd,rs1

        :Description:
          | Converts a double-precision floating-point number in floating-point register rs1 to a signed 32-bit integer, in integer register rd.

        :Implementation:
          | x[rd] = sext(s32_{f64}(f[rs1]))
        """
        rd, rs = self.parse_rd_rs(ins)
        self.regs.set(rd, Int32.from_float(self.regs.get_f(rs).value))

    def instruction_fcvt_wu_d(self, ins: Instruction):
        """
        +-----+-----+-----+-----+-----+-----+-----+---+
        |31-27|26-25|24-20|19-15|14-12|11-7 |6-2  |1-0|
        +-----+-----+-----+-----+-----+-----+-----+---+
        |11000|01   |00001|rs1  |rm   |rd   |10100|11 |
        +-----+-----+-----+-----+-----+-----+-----+---+

        :Format:
          | fcvt.wu.d  rd,rs1

        :Description:
          | Converts a double-precision floating-point number in floating-point register rs1 to a unsigned 32-bit integer, in integer register rd.

        :Implementation:
          | x[rd] = sext(u32f64(f[rs1]))
        """
        rd, rs = self.parse_rd_rs(ins)
        self.regs.set(rd, UInt32.from_float(self.regs.get_f(rs).value))
