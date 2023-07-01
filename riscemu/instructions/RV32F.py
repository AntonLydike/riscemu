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
from riscemu.types import INS_NOT_IMPLEMENTED, Float32, Int32, UInt32


class RV32F(InstructionSet):
    def instruction_fmadd_s(self, ins: Instruction):
        """
        +-----+-----+-----+-----+-----+-----+-----+---+
        |31-27|26-25|24-20|19-15|14-12|11-7 |6-2  |1-0|
        +-----+-----+-----+-----+-----+-----+-----+---+
        |rs3  |00   |rs2  |rs1  |rm   |rd   |10000|11 |
        +-----+-----+-----+-----+-----+-----+-----+---+


        :Format:
        | fmadd.s    rd,rs1,rs2,rs3

        :Description:
        | Perform single-precision fused multiply addition.

        :Implementation:
        | f[rd] = f[rs1]×f[rs2]+f[rs3]

        """
        rd, rs1, rs2, rs3 = self.parse_rd_rs_rs_rs(ins)
        self.regs.set_f(rd, rs1 * rs2 + rs3)

    def instruction_fmsub_s(self, ins: Instruction):
        """
        +-----+-----+-----+-----+-----+-----+-----+---+
        |31-27|26-25|24-20|19-15|14-12|11-7 |6-2  |1-0|
        +-----+-----+-----+-----+-----+-----+-----+---+
        |rs3  |00   |rs2  |rs1  |rm   |rd   |10001|11 |
        +-----+-----+-----+-----+-----+-----+-----+---+


        :Format:
        | fmsub.s    rd,rs1,rs2,rs3

        :Description:
        | Perform single-precision fused multiply addition.

        :Implementation:
        | f[rd] = f[rs1]×f[rs2]-f[rs3]
        """
        rd, rs1, rs2, rs3 = self.parse_rd_rs_rs_rs(ins)
        self.regs.set_f(rd, rs1 * rs2 - rs3)

    def instruction_fnmsub_s(self, ins: Instruction):
        """
        +-----+-----+-----+-----+-----+-----+-----+---+
        |31-27|26-25|24-20|19-15|14-12|11-7 |6-2  |1-0|
        +-----+-----+-----+-----+-----+-----+-----+---+
        |rs3  |00   |rs2  |rs1  |rm   |rd   |10010|11 |
        +-----+-----+-----+-----+-----+-----+-----+---+


        :Format:
        | fnmsub.s   rd,rs1,rs2,rs3

        :Description:
        | Perform single-precision fused multiply addition.

        :Implementation:
        | f[rd] = -f[rs1]×f[rs2]+f[rs3]
        """
        rd, rs1, rs2, rs3 = self.parse_rd_rs_rs_rs(ins)
        self.regs.set_f(rd, -rs1 * rs2 + rs3)

    def instruction_fnmadd_s(self, ins: Instruction):
        """
        +-----+-----+-----+-----+-----+-----+-----+---+
        |31-27|26-25|24-20|19-15|14-12|11-7 |6-2  |1-0|
        +-----+-----+-----+-----+-----+-----+-----+---+
        |rs3  |00   |rs2  |rs1  |rm   |rd   |10011|11 |
        +-----+-----+-----+-----+-----+-----+-----+---+


        :Format:
        | fnmadd.s   rd,rs1,rs2,rs3

        :Description:
        | Perform single-precision fused multiply addition.

        :Implementation:
        | f[rd] = -f[rs1]×f[rs2]-f[rs3]
        """
        rd, rs1, rs2, rs3 = self.parse_rd_rs_rs_rs(ins)
        self.regs.set_f(rd, -rs1 * rs2 - rs3)

    def instruction_fadd_s(self, ins: Instruction):
        """
        +-----+-----+-----+-----+-----+-----+-----+---+
        |31-27|26-25|24-20|19-15|14-12|11-7 |6-2  |1-0|
        +-----+-----+-----+-----+-----+-----+-----+---+
        |00000|00   |rs2  |rs1  |rm   |rd   |10100|11 |
        +-----+-----+-----+-----+-----+-----+-----+---+


        :Format:
        | fadd.s     rd,rs1,rs2

        :Description:
        | Perform single-precision floating-point addition.

        :Implementation:
        | f[rd] = f[rs1] + f[rs2]
        """
        rd, rs1, rs2 = self.parse_rd_rs_rs(ins)
        self.regs.set_f(
            rd,
            self.regs.get_f(rs1) + self.regs.get_f(rs2),
        )

    def instruction_fsub_s(self, ins: Instruction):
        """
        +-----+-----+-----+-----+-----+-----+-----+---+
        |31-27|26-25|24-20|19-15|14-12|11-7 |6-2  |1-0|
        +-----+-----+-----+-----+-----+-----+-----+---+
        |00001|00   |rs2  |rs1  |rm   |rd   |10100|11 |
        +-----+-----+-----+-----+-----+-----+-----+---+


        :Format:
        | fsub.s     rd,rs1,rs2

        :Description:
        | Perform single-precision floating-point substraction.

        :Implementation:
        | f[rd] = f[rs1] - f[rs2]
        """
        rd, rs1, rs2 = self.parse_rd_rs_rs(ins)
        self.regs.set_f(
            rd,
            self.regs.get_f(rs1) - self.regs.get_f(rs2),
        )

    def instruction_fmul_s(self, ins: Instruction):
        """
        +-----+-----+-----+-----+-----+-----+-----+---+
        |31-27|26-25|24-20|19-15|14-12|11-7 |6-2  |1-0|
        +-----+-----+-----+-----+-----+-----+-----+---+
        |00010|00   |rs2  |rs1  |rm   |rd   |10100|11 |
        +-----+-----+-----+-----+-----+-----+-----+---+


        :Format:
        | fmul.s     rd,rs1,rs2

        :Description:
        | Perform single-precision floating-point multiplication.

        :Implementation:
        | f[rd] = f[rs1] × f[rs2]
        """
        rd, rs1, rs2 = self.parse_rd_rs_rs(ins)
        self.regs.set_f(
            rd,
            self.regs.get_f(rs1) * self.regs.get_f(rs2),
        )

    def instruction_fdiv_s(self, ins: Instruction):
        """
        +-----+-----+-----+-----+-----+-----+-----+---+
        |31-27|26-25|24-20|19-15|14-12|11-7 |6-2  |1-0|
        +-----+-----+-----+-----+-----+-----+-----+---+
        |00011|00   |rs2  |rs1  |rm   |rd   |10100|11 |
        +-----+-----+-----+-----+-----+-----+-----+---+


        :Format:
        | fdiv.s     rd,rs1,rs2

        :Description:
        | Perform single-precision floating-point division.

        :Implementation:
        | f[rd] = f[rs1] / f[rs2]
        """
        rd, rs1, rs2 = self.parse_rd_rs_rs(ins)
        self.regs.set_f(
            rd,
            self.regs.get_f(rs1) / self.regs.get_f(rs2),
        )

    def instruction_fsqrt_s(self, ins: Instruction):
        """
        +-----+-----+-----+-----+-----+-----+-----+---+
        |31-27|26-25|24-20|19-15|14-12|11-7 |6-2  |1-0|
        +-----+-----+-----+-----+-----+-----+-----+---+
        |01011|00   |00000|rs1  |rm   |rd   |10100|11 |
        +-----+-----+-----+-----+-----+-----+-----+---+


        :Format:
        | fsqrt.s    rd,rs1

        :Description:
        | Perform single-precision square root.

        :Implementation:
        | f[rd] = sqrt(f[rs1])
        """
        rd, rs = self.parse_rd_rs(ins)
        self.regs.set_f(self.regs.get_f(rs) ** 0.5)

    def instruction_fsgnj_s(self, ins: Instruction):
        """
        +-----+-----+-----+-----+-----+-----+-----+---+
        |31-27|26-25|24-20|19-15|14-12|11-7 |6-2  |1-0|
        +-----+-----+-----+-----+-----+-----+-----+---+
        |00100|00   |rs2  |rs1  |000  |rd   |10100|11 |
        +-----+-----+-----+-----+-----+-----+-----+---+

        :Format:
        | fsgnj.s    rd,rs1,rs2

        :Description:
        | Produce a result that takes all bits except the sign bit from rs1.
        | The result’s sign bit is rs2’s sign bit.

        :Implementation:
        | f[rd] = {f[rs2][31], f[rs1][30:0]}
        """
        INS_NOT_IMPLEMENTED(ins)

    def instruction_fsgnjn_s(self, ins: Instruction):
        """
        +-----+-----+-----+-----+-----+-----+-----+---+
        |31-27|26-25|24-20|19-15|14-12|11-7 |6-2  |1-0|
        +-----+-----+-----+-----+-----+-----+-----+---+
        |00100|00   |rs2  |rs1  |001  |rd   |10100|11 |
        +-----+-----+-----+-----+-----+-----+-----+---+


        :Format:
        | fsgnjn.s   rd,rs1,rs2

        :Description:
        | Produce a result that takes all bits except the sign bit from rs1.
        | The result’s sign bit is opposite of rs2’s sign bit.

        :Implementation:
        | f[rd] = {~f[rs2][31], f[rs1][30:0]}
        """
        INS_NOT_IMPLEMENTED(ins)

    def instruction_fsgnjx_s(self, ins: Instruction):
        """
        +-----+-----+-----+-----+-----+-----+-----+---+
        |31-27|26-25|24-20|19-15|14-12|11-7 |6-2  |1-0|
        +-----+-----+-----+-----+-----+-----+-----+---+
        |00100|00   |rs2  |rs1  |010  |rd   |10100|11 |
        +-----+-----+-----+-----+-----+-----+-----+---+

        :Format:
        | fsgnjx.s   rd,rs1,rs2

        :Description:
        | Produce a result that takes all bits except the sign bit from rs1.
        | The result’s sign bit is XOR of sign bit of rs1 and rs2.

        :Implementation:
        | f[rd] = {f[rs1][31] ^ f[rs2][31], f[rs1][30:0]}
        """
        INS_NOT_IMPLEMENTED(ins)

    def instruction_fmin_s(self, ins: Instruction):
        """
        +-----+-----+-----+-----+-----+-----+-----+---+
        |31-27|26-25|24-20|19-15|14-12|11-7 |6-2  |1-0|
        +-----+-----+-----+-----+-----+-----+-----+---+
        |00101|00   |rs2  |rs1  |000  |rd   |10100|11 |
        +-----+-----+-----+-----+-----+-----+-----+---+

        :Format:
        | fmin.s     rd,rs1,rs2

        :Description:
        | Write the smaller of single precision data in rs1 and rs2 to rd.

        :Implementation:
        | f[rd] = min(f[rs1], f[rs2])
        """
        rd, rs1, rs2 = self.parse_rd_rs_rs(ins)
        self.regs.set_f(
            rd,
            Float32(
                min(
                    self.regs.get_f(rs1).value,
                    self.regs.get_f(rs2).value,
                )
            ),
        )

    def instruction_fmax_s(self, ins: Instruction):
        """
        +-----+-----+-----+-----+-----+-----+-----+---+
        |31-27|26-25|24-20|19-15|14-12|11-7 |6-2  |1-0|
        +-----+-----+-----+-----+-----+-----+-----+---+
        |00101|00   |rs2  |rs1  |001  |rd   |10100|11 |
        +-----+-----+-----+-----+-----+-----+-----+---+

        :Format:
        | fmax.s     rd,rs1,rs2

        :Description:
        | Write the larger of single precision data in rs1 and rs2 to rd.

        :Implementation:
        | f[rd] = max(f[rs1], f[rs2])
        """
        rd, rs1, rs2 = self.parse_rd_rs_rs(ins)
        self.regs.set_f(
            rd,
            Float32(
                max(
                    self.regs.get_f(rs1).value,
                    self.regs.get_f(rs2).value,
                )
            ),
        )

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
        self.regs.set(rd, Int32(self.regs.get_f(rs).value))

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
        self.regs.set(rd, UInt32(self.regs.get_f(rs).value))

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
        self.regs.set(rd, UInt32(self.regs.get_f(rs).bits))

    def instruction_feq_s(self, ins: Instruction):
        """
        +-----+-----+-----+-----+-----+-----+-----+---+
        |31-27|26-25|24-20|19-15|14-12|11-7 |6-2  |1-0|
        +-----+-----+-----+-----+-----+-----+-----+---+
        |10100|00   |rs2  |rs1  |010  |rd   |10100|11 |
        +-----+-----+-----+-----+-----+-----+-----+---+

        :Format:
        | feq.s      rd,rs1,rs2

        :Description:
        | Performs a quiet equal comparison between floating-point registers rs1 and rs2 and record the Boolean result in integer register rd.
        | Only signaling NaN inputs cause an Invalid Operation exception.
        | The result is 0 if either operand is NaN.

        :Implementation:
        | x[rd] = f[rs1] == f[rs2]
        """
        rd, rs1, rs2 = self.parse_rd_rs_rs(ins)
        self.regs.set(rd, Int32(rs1 == rs2))

    def instruction_flt_s(self, ins: Instruction):
        """
        +-----+-----+-----+-----+-----+-----+-----+---+
        |31-27|26-25|24-20|19-15|14-12|11-7 |6-2  |1-0|
        +-----+-----+-----+-----+-----+-----+-----+---+
        |10100|00   |rs2  |rs1  |001  |rd   |10100|11 |
        +-----+-----+-----+-----+-----+-----+-----+---+

        :Format:
        | flt.s      rd,rs1,rs2

        :Description:
        | Performs a quiet less comparison between floating-point registers rs1 and rs2 and record the Boolean result in integer register rd.
        | Only signaling NaN inputs cause an Invalid Operation exception.
        | The result is 0 if either operand is NaN.

        :Implementation:
        | x[rd] = f[rs1] < f[rs2]
        """
        rd, rs1, rs2 = self.parse_rd_rs_rs(ins)
        self.regs.set(rd, Int32(rs1 < rs2))

    def instruction_fle_s(self, ins: Instruction):
        """
        +-----+-----+-----+-----+-----+-----+-----+---+
        |31-27|26-25|24-20|19-15|14-12|11-7 |6-2  |1-0|
        +-----+-----+-----+-----+-----+-----+-----+---+
        |10100|00   |rs2  |rs1  |000  |rd   |10100|11 |
        +-----+-----+-----+-----+-----+-----+-----+---+

        :Format:
        | fle.s      rd,rs1,rs2

        :Description:
        | Performs a quiet less or equal comparison between floating-point registers rs1 and rs2 and record the Boolean result in integer register rd.
        | Only signaling NaN inputs cause an Invalid Operation exception.
        | The result is 0 if either operand is NaN.

        :Implementation:
        | x[rd] = f[rs1] <= f[rs2]
        """
        rd, rs1, rs2 = self.parse_rd_rs_rs(ins)
        self.regs.set(rd, Int32(rs1 <= rs2))

    def instruction_fclass_s(self, ins: Instruction):
        """
        +-----+-----+-----+-----+-----+-----+-----+---+
        |31-27|26-25|24-20|19-15|14-12|11-7 |6-2  |1-0|
        +-----+-----+-----+-----+-----+-----+-----+---+
        |11100|00   |00000|rs1  |001  |rd   |10100|11 |
        +-----+-----+-----+-----+-----+-----+-----+---+

        :Format:
        | fclass.s   rd,rs1

        :Description:
        | Examines the value in floating-point register rs1 and writes to integer register rd a 10-bit mask that indicates the class of the floating-point number.
        | The format of the mask is described in [classify table]_.
        | The corresponding bit in rd will be set if the property is true and clear otherwise.
        | All other bits in rd are cleared. Note that exactly one bit in rd will be set.

        :Implementation:
        | x[rd] = classifys(f[rs1])
        """
        INS_NOT_IMPLEMENTED(ins)

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
        self.regs.set_f(rd, Float32.from_bytes(self.regs.get(rs).unsigned_value))

    def instruction_flw(self, ins: Instruction):
        """
        +-----+-----+-----+-----+-----+-----+-----+---+
        |31-27|26-25|24-20|19-15|14-12|11-7 |6-2  |1-0|
        +-----+-----+-----+-----+-----+-----+-----+---+
        |imm[11:0]        |rs1  |010  |rd   |00001|11 |
        +-----+-----+-----+-----+-----+-----+-----+---+

        :Format:
          | flw        rd,offset(rs1)

        :Description:
          | Load a single-precision floating-point value from memory into floating-point register rd.

        :Implementation:
          | f[rd] = M[x[rs1] + sext(offset)][31:0]
        """
        rd, addr = self.parse_rd_rs_mem_ins(ins)
        self.regs.set_f(rd, self.mmu.read_float(addr))

    def instruction_fsw(self, ins: Instruction):
        """
        +-----+-----+-----+-----+-----+--------+-----+---+
        |31-27|26-25|24-20|19-15|14-12|11-7    |6-2  |1-0|
        +-----+-----+-----+-----+-----+--------+-----+---+
        |imm[11:5]  |rs2  |rs1  |010  |imm[4:0]|01001|11 |
        +-----+-----+-----+-----+-----+--------+-----+---+

        :Format:
          | fsw        rs2,offset(rs1)

        :Description:
          | Store a single-precision value from floating-point register rs2 to memory.

        :Implementation:
          | M[x[rs1] + sext(offset)] = f[rs2][31:0]
        """
        rs, addr = self.parse_rs_rs_mem_ins(ins)
        val = self.regs.get_f(rs)
        self.mmu.write(addr, 4, bytearray(val.bytes))

    def parse_rd_rs(self, ins: Instruction) -> Tuple[str, str]:
        assert len(ins.args) == 2
        return ins.get_reg(0), ins.get_reg(1)

    def parse_rd_rs_rs(self, ins: Instruction) -> Tuple[str, Float32, Float32]:
        assert len(ins.args) == 3
        return (
            ins.get_reg(0),
            self.regs.get_f(ins.get_reg(1)),
            self.regs.get_f(ins.get_reg(2)),
        )

    def parse_rd_rs_rs_rs(
        self, ins: Instruction
    ) -> Tuple[str, Float32, Float32, Float32]:
        assert len(ins.args) == 4
        return (
            ins.get_reg(0),
            self.regs.get_f(ins.get_reg(1)),
            self.regs.get_f(ins.get_reg(2)),
            self.regs.get_f(ins.get_reg(3)),
        )
