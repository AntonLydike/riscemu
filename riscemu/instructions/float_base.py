from typing import ClassVar, Generic, TypeVar, Tuple, Iterable, Callable, Type

from .instruction_set import InstructionSet, Instruction
from riscemu.core import BaseFloat, CPU, INS_NOT_IMPLEMENTED, UInt32

_FloatT = TypeVar("_FloatT", bound=BaseFloat)


class FloatArithBase(Generic[_FloatT], InstructionSet):
    flen: ClassVar[int]
    _float_cls: ClassVar[Type[BaseFloat]]

    def __init__(self, cpu: CPU):
        assert cpu.regs.flen >= self.flen, "{} implies cpu flen of at least {}".format(
            self.__class__.__name__, self.flen
        )
        super().__init__(cpu)

    def base_fmadd(self, ins: Instruction):
        """
        :Format:
        | fmadd.{s,d,q}    rd,rs1,rs2,rs3

        :Description:
        | Perform fused multiply addition.

        :Implementation:
        | f[rd] = f[rs1]×f[rs2]+f[rs3]

        """
        rd, rs1, rs2, rs3 = self.parse_rd_rs_rs_rs(ins)
        self.regs.set_f(rd, rs1 * rs2 + rs3)

    def base_fmsub(self, ins: Instruction):
        """
        :Format:
        | fmsub.{s,d,q}    rd,rs1,rs2,rs3

        :Description:
        | Perform fused multiply subtraction.

        :Implementation:
        | f[rd] = f[rs1]×f[rs2]-f[rs3]
        """
        rd, rs1, rs2, rs3 = self.parse_rd_rs_rs_rs(ins)
        self.regs.set_f(rd, rs1 * rs2 - rs3)

    def base_fnmsub(self, ins: Instruction):
        """
        :Format:
        | fnmsub.{s,d,q}   rd,rs1,rs2,rs3

        :Description:
        | Perform fused negated multiply addition.

        :Implementation:
        | f[rd] = -f[rs1]×f[rs2]+f[rs3]
        """
        rd, rs1, rs2, rs3 = self.parse_rd_rs_rs_rs(ins)
        self.regs.set_f(rd, -rs1 * rs2 + rs3)

    def base_fnmadd(self, ins: Instruction):
        """
        :Format:
        | fnmadd.{s,d,q}   rd,rs1,rs2,rs3

        :Description:
        | Perform single-precision fused negated multiply addition.

        :Implementation:
        | f[rd] = -f[rs1]×f[rs2]-f[rs3]
        """
        rd, rs1, rs2, rs3 = self.parse_rd_rs_rs_rs(ins)
        self.regs.set_f(rd, -rs1 * rs2 - rs3)

    def base_fadd(self, ins: Instruction):
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
            rs1 + rs2,
        )

    def base_fsub(self, ins: Instruction):
        """
        :Format:
        | fsub.{s,d,q}     rd,rs1,rs2

        :Description:
        | Perform single-precision floating-point subtraction.

        :Implementation:
        | f[rd] = f[rs1] - f[rs2]
        """
        rd, rs1, rs2 = self.parse_rd_rs_rs(ins)
        self.regs.set_f(
            rd,
            rs1 - rs2,
        )

    def base_fmul(self, ins: Instruction):
        """
        :Format:
        | fmul.{s,d,q}     rd,rs1,rs2

        :Description:
        | Perform floating-point multiplication.

        :Implementation:
        | f[rd] = f[rs1] × f[rs2]
        """
        rd, rs1, rs2 = self.parse_rd_rs_rs(ins)
        self.regs.set_f(
            rd,
            rs1 * rs2,
        )

    def base_fdiv(self, ins: Instruction):
        """
        :Format:
        | fdiv.{s,d,q}     rd,rs1,rs2

        :Description:
        | Perform floating-point division.

        :Implementation:
        | f[rd] = f[rs1] / f[rs2]
        """
        rd, rs1, rs2 = self.parse_rd_rs_rs(ins)
        self.regs.set_f(
            rd,
            rs1 / rs2,
        )

    def base_fsqrt(self, ins: Instruction):
        """
        :Format:
        | fsqrt.{s,d,q}    rd,rs1

        :Description:
        | Perform single-precision square root.

        :Implementation:
        | f[rd] = sqrt(f[rs1])
        """
        rd, rs = self.parse_rd_rs(ins)
        self.regs.set_f(rd, self._float_cls.bitcast(self.regs.get_f(rs)) ** 0.5)

    def base_fsgnj(self, ins: Instruction):
        """
        :Format:
        | fsgnj.{s,d,q}    rd,rs1,rs2

        :Description:
        | Produce a result that takes all bits except the sign bit from rs1.
        | The result’s sign bit is rs2’s sign bit.

        :Implementation:
        | f[rd] = {f[rs2][31], f[rs1][30:0]}
        """
        INS_NOT_IMPLEMENTED(ins)

    def base_fsgnjn(self, ins: Instruction):
        """
        :Format:
        | fsgnjn.{s,d,q}   rd,rs1,rs2

        :Description:
        | Produce a result that takes all bits except the sign bit from rs1.
        | The result’s sign bit is opposite of rs2’s sign bit.

        :Implementation:
        | f[rd] = {~f[rs2][31], f[rs1][30:0]}
        """
        INS_NOT_IMPLEMENTED(ins)

    def base_fsgnjx(self, ins: Instruction):
        """
        :Format:
        | fsgnjx.{s,d,q}   rd,rs1,rs2

        :Description:
        | Produce a result that takes all bits except the sign bit from rs1.
        | The result’s sign bit is XOR of sign bit of rs1 and rs2.

        :Implementation:
        | f[rd] = {f[rs1][31] ^ f[rs2][31], f[rs1][30:0]}
        """
        INS_NOT_IMPLEMENTED(ins)

    def base_fmin(self, ins: Instruction):
        """
        :Format:
        | fmin.{s,d,q}     rd,rs1,rs2

        :Description:
        | Write the smaller of rs1 and rs2 to rd.

        :Implementation:
        | f[rd] = min(f[rs1], f[rs2])
        """
        rd, rs1, rs2 = self.parse_rd_rs_rs(ins)
        self.regs.set_f(
            rd,
            min(
                rs1,
                rs2,
            ),
        )

    def base_fmax(self, ins: Instruction):
        """
        :Format:
        | fmax.{s,d,q}     rd,rs1,rs2

        :Description:
        | Write the larger of rs1 and rs2 to rd.

        :Implementation:
        | f[rd] = max(f[rs1], f[rs2])
        """
        rd, rs1, rs2 = self.parse_rd_rs_rs(ins)
        self.regs.set_f(
            rd,
            max(
                rs1,
                rs2,
            ),
        )

    def base_feq(self, ins: Instruction):
        """
        :Format:
        | feq.{s,d,q}      rd,rs1,rs2

        :Description:
        | Performs a quiet equal comparison between floating-point registers rs1 and rs2 and record the Boolean result in integer register rd.
        | Only signaling NaN inputs cause an Invalid Operation exception.
        | The result is 0 if either operand is NaN.

        :Implementation:
        | x[rd] = f[rs1] == f[rs2]
        """
        rd, rs1, rs2 = self.parse_rd_rs_rs(ins)
        self.regs.set(rd, UInt32(rs1 == rs2))

    def base_flt(self, ins: Instruction):
        """
        :Format:
        | flt.{s,d,q}      rd,rs1,rs2

        :Description:
        | Performs a quiet less comparison between floating-point registers rs1 and rs2 and record the Boolean result in integer register rd.
        | Only signaling NaN inputs cause an Invalid Operation exception.
        | The result is 0 if either operand is NaN.

        :Implementation:
        | x[rd] = f[rs1] < f[rs2]
        """
        rd, rs1, rs2 = self.parse_rd_rs_rs(ins)
        self.regs.set(rd, UInt32(rs1 < rs2))

    def base_fle(self, ins: Instruction):
        """
        :Format:
        | fle.{s,d,q}      rd,rs1,rs2

        :Description:
        | Performs a quiet less or equal comparison between floating-point registers rs1 and rs2 and record the Boolean result in integer register rd.
        | Only signaling NaN inputs cause an Invalid Operation exception.
        | The result is 0 if either operand is NaN.

        :Implementation:
        | x[rd] = f[rs1] <= f[rs2]
        """
        rd, rs1, rs2 = self.parse_rd_rs_rs(ins)
        self.regs.set(rd, UInt32(rs1 <= rs2))

    def base_fclass(self, ins: Instruction):
        """
        :Format:
        | fclass.{s,d,q}   rd,rs1

        :Description:
        | Examines the value in floating-point register rs1 and writes to integer register rd a 10-bit mask that indicates the class of the floating-point number.
        | The format of the mask is described in [classify table]_.
        | The corresponding bit in rd will be set if the property is true and clear otherwise.
        | All other bits in rd are cleared. Note that exactly one bit in rd will be set.

        :Implementation:
        | x[rd] = classifys(f[rs1])
        """
        INS_NOT_IMPLEMENTED(ins)

    def base_load(self, ins: Instruction):
        """
        :Format:
          | fl{w,d,q}        rd,offset(rs1)

        :Description:
          | Load a floating-point value from memory into floating-point register rd.

        :Implementation:
          | f[rd] = M[x[rs1] + sext(offset)][31:0]
        """
        rd, addr = self.parse_mem_ins(ins)
        bytes = self.mmu.read(addr.value, self.flen // 8)
        self.regs.set_f(rd, self._float_cls(bytes))

    def base_save(self, ins: Instruction):
        """:Format:
          | fs{w,d,q}        rs2,offset(rs1)

        :Description:
          | Store a value from floating-point register rs2 to memory.

        :Implementation:
          | M[x[rs1] + sext(offset)] = f[rs2][31:0]
        """
        rs, addr = self.parse_mem_ins(ins)
        val = self._float_cls.bitcast(self.regs.get_f(rs))
        self.mmu.write(addr.value, self.flen // 8, bytearray(val.bytes))

    def get_instructions(self) -> Iterable[Tuple[str, Callable[[Instruction], None]]]:
        yield from super().get_instructions()

        qual = {32: "s", 64: "d", 128: "q"}.get(self.flen)
        load_save_qual = {32: "w", 64: "d", 128: "q"}.get(self.flen)

        yield from (
            ("fmadd." + qual, self.base_fmadd),
            ("fmsub." + qual, self.base_fmsub),
            ("fnmsub." + qual, self.base_fnmsub),
            ("fnmadd." + qual, self.base_fnmadd),
            ("fadd." + qual, self.base_fadd),
            ("fsub." + qual, self.base_fnmadd),
            ("fmul." + qual, self.base_fmul),
            ("fdiv." + qual, self.base_fdiv),
            ("fsqrt." + qual, self.base_fsqrt),
            ("fsgnj." + qual, self.base_fsgnj),
            ("fsgnjn." + qual, self.base_fsgnjn),
            ("fsgnjx." + qual, self.base_fsgnjx),
            ("fmin." + qual, self.base_fmin),
            ("fmax." + qual, self.base_fmax),
            ("feq." + qual, self.base_feq),
            ("flt." + qual, self.base_flt),
            ("fle." + qual, self.base_fle),
            ("fl" + load_save_qual, self.base_load),
            ("fs" + load_save_qual, self.base_save),
        )

    def parse_rd_rs(self, ins: Instruction) -> Tuple[str, str]:
        assert len(ins.args) == 2
        return ins.get_reg(0), ins.get_reg(1)

    def parse_rd_rs_rs(self, ins: Instruction) -> Tuple[str, _FloatT, _FloatT]:
        assert len(ins.args) == 3
        return (
            ins.get_reg(0),
            self._float_cls.bitcast(self.regs.get_f(ins.get_reg(1))),
            self._float_cls.bitcast(self.regs.get_f(ins.get_reg(2))),
        )

    def parse_rd_rs_rs_rs(
        self, ins: Instruction
    ) -> Tuple[str, _FloatT, _FloatT, _FloatT]:
        assert len(ins.args) == 4
        return (
            ins.get_reg(0),
            self._float_cls.bitcast(self.regs.get_f(ins.get_reg(1))),
            self._float_cls.bitcast(self.regs.get_f(ins.get_reg(2))),
            self._float_cls.bitcast(self.regs.get_f(ins.get_reg(3))),
        )
