from riscemu.core import CPU, Int32, InstructionContext, Registers, SimpleInstruction
from riscemu.core.exceptions import ParseException
from riscemu.instructions.RV32I import RV32I
from riscemu.parser import canonicalize_register_names
from riscemu.tokenizer import tokenize

import pytest


class MockInstruction(SimpleInstruction):
    ...


class MockRegisters(Registers):
    ...


class MockCPU(CPU):
    def __init__(self):
        self.regs = MockRegisters()

    def run(self, verbose: bool = False):
        assert False

    def step(self, verbose: bool = False):
        assert False


def test_memory_operand_stays_single_argument():
    args = [t.value for t in tokenize(["lw a0, 4(t0)"]) if t.type.name == "ARGUMENT"]
    assert args == ["a0", "4(t0)"]


def test_canonicalize_register_inside_memory_operand():
    assert list(canonicalize_register_names(("a0", "4(x5)"))) == ["a0", "4(t0)"]
    assert list(canonicalize_register_names(("a0", "0(x31)"))) == ["a0", "0(t6)"]


def test_canonicalize_plain_register_names_unchanged():
    assert list(canonicalize_register_names(("a0", "t0", "4"))) == ["a0", "t0", "4"]


def test_load_store_accept_proper_syntax():
    cpu = MockCPU()
    cpu.regs.set("t0", Int32(0x1000))

    rd, addr = RV32I(cpu).parse_mem_ins(
        MockInstruction("lw", ("a0", "4(t0)"), InstructionContext(), 0)
    )
    assert rd == "a0"
    assert addr.unsigned_value == 0x1004

    cpu.regs.set("ra", Int32(0x2000))
    rd, addr = RV32I(cpu).parse_mem_ins(
        MockInstruction("sw", ("a1", "0(ra)"), InstructionContext(), 0)
    )
    assert rd == "a1"
    assert addr.unsigned_value == 0x2000


def test_load_rejects_improper_three_argument_syntax():
    # the improper `lw a0, t0, 0` form must be rejected,
    # see https://github.com/AntonLydike/riscemu/issues/54
    cpu = MockCPU()

    with pytest.raises(ParseException, match="offset\\(base_register\\)"):
        RV32I(cpu).parse_mem_ins(
            MockInstruction("lw", ("a0", "t0", "0"), InstructionContext(), 0)
        )

    with pytest.raises(ParseException, match="offset\\(base_register\\)"):
        RV32I(cpu).parse_mem_ins(
            MockInstruction("sw", ("a1", "t0", "4"), InstructionContext(), 0)
        )


def test_load_rejects_memory_operand_without_parens():
    cpu = MockCPU()

    with pytest.raises(ParseException, match="not a valid memory operand"):
        RV32I(cpu).parse_mem_ins(
            MockInstruction("lw", ("a0", "t0"), InstructionContext(), 0)
        )
