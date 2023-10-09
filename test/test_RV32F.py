from typing import Union

from riscemu.instructions.RV32F import RV32F
from riscemu.core import CPU, Float32, Int32, SimpleInstruction, Registers, BaseFloat


def is_close(a0: Union[float, int, BaseFloat], a1: Union[float, int, BaseFloat]):
    """
    Compares if two numbers are close to 7 digits.
    This should be close enough to catch any real erros but ignore
    floating point rounding issues.
    """
    diff = abs(float(a0 - a1))
    mag = max(abs(float(a0)), abs(float(a1)))
    return (mag / 1e7) > diff


class MockInstruction(SimpleInstruction):
    ...


class MockRegisters(Registers):
    ...


class MockCPU(CPU):
    def __init__(self, flen: int = 32):
        self.regs = MockRegisters(True, flen)

    def run(self, verbose: bool = False):
        assert False

    def step(self, verbose: bool = False):
        assert False


def test_fcvt_instructions():
    cpu = MockCPU()

    ins = MockInstruction("fcvt.s.w", ("fa0", "a0"), None, None)
    cpu.regs.set("a0", Int32(42))
    RV32F(cpu).instruction_fcvt_s_w(ins)
    assert 42.0 == cpu.regs.get_f("fa0")

    ins = MockInstruction("fcvt.w.s", ("a1", "fa1"), None, None)
    cpu.regs.set_f("fa1", Float32(42.0))
    RV32F(cpu).instruction_fcvt_w_s(ins)
    assert Int32(42) == cpu.regs.get("a1")


def test_single_precision_on_flen64():
    cpu = MockCPU(flen=64)

    cpu.regs.set_f("ft0", Float32(100))
    cpu.regs.set_f("ft1", Float32(3))
    # instruction doing ft2 <- ft1 <op> ft2

    ins = MockInstruction("<noname>", ("ft2", "ft0", "ft1"), None, None)

    # div
    RV32F(cpu).base_fdiv(ins)
    assert is_close(Float32.bitcast(cpu.regs.get_f("ft2")), (100.0 / 3))

    # multiplication
    RV32F(cpu).base_fmul(ins)
    assert is_close(Float32.bitcast(cpu.regs.get_f("ft2")), (100.0 * 3))

    # fadd
    RV32F(cpu).base_fadd(ins)
    assert is_close(Float32.bitcast(cpu.regs.get_f("ft2")), (100.0 + 3))

    # fsub
    RV32F(cpu).base_fsub(ins)
    assert is_close(Float32.bitcast(cpu.regs.get_f("ft2")), (100.0 - 3))

    # fmin
    RV32F(cpu).base_fmin(ins)
    assert is_close(Float32.bitcast(cpu.regs.get_f("ft2")), min(100.0, 3))

    # fmax
    RV32F(cpu).base_fmax(ins)
    assert is_close(Float32.bitcast(cpu.regs.get_f("ft2")), max(100.0, 3))


def test_single_precision_on_flen32():
    cpu = MockCPU(flen=32)

    cpu.regs.set_f("ft0", Float32(100))
    cpu.regs.set_f("ft1", Float32(3))
    # instruction doing ft2 <- ft1 <op> ft2

    ins = MockInstruction("<noname>", ("ft2", "ft0", "ft1"), None, None)

    # div
    RV32F(cpu).base_fdiv(ins)
    assert is_close(Float32.bitcast(cpu.regs.get_f("ft2")), (100.0 / 3))

    # multiplication
    RV32F(cpu).base_fmul(ins)
    assert is_close(Float32.bitcast(cpu.regs.get_f("ft2")), (100.0 * 3))

    # fadd
    RV32F(cpu).base_fadd(ins)
    assert is_close(Float32.bitcast(cpu.regs.get_f("ft2")), (100.0 + 3))

    # fsub
    RV32F(cpu).base_fsub(ins)
    assert is_close(Float32.bitcast(cpu.regs.get_f("ft2")), (100.0 - 3))

    # fmin
    RV32F(cpu).base_fmin(ins)
    assert is_close(Float32.bitcast(cpu.regs.get_f("ft2")), min(100.0, 3))

    # fmax
    RV32F(cpu).base_fmax(ins)
    assert is_close(Float32.bitcast(cpu.regs.get_f("ft2")), max(100.0, 3))
