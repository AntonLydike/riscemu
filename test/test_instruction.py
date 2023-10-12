from riscemu.core import InstructionContext, SimpleInstruction, NumberFormatException
import pytest


def test_int_and_hex_immediates():
    ctx = InstructionContext()

    ins = SimpleInstruction("addi", ("a0", "a1", "100"), ctx, 0x100)
    ins_hex = SimpleInstruction("addi", ("a0", "a1", "0x10"), ctx, 0x100)

    assert ins.get_reg(0) == "a0"
    assert ins.get_reg(1) == "a1"
    assert ins.get_imm(2).abs_value == 100
    assert ins.get_imm(2).pcrel_value == 100 - 0x100

    assert ins_hex.get_imm(2).abs_value == 0x10
    assert ins_hex.get_imm(2).pcrel_value == 0x10 - 0x100


def test_label_immediates():
    ctx = InstructionContext()
    ctx.labels["test"] = 100

    ins = SimpleInstruction("addi", ("a0", "a1", "test"), ctx, 0x100)

    assert ins.get_reg(0) == "a0"
    assert ins.get_reg(1) == "a1"
    assert ins.get_imm(2).abs_value == 100
    assert ins.get_imm(2).pcrel_value == 100 - 0x100


def test_numerical_labels():
    ctx = InstructionContext()
    ctx.numbered_labels["1"] = [0x100 - 4, 0x100 + 16]

    ins = SimpleInstruction("addi", ("a0", "a1", "1b"), ctx, 0x100)

    assert ins.get_reg(0) == "a0"
    assert ins.get_reg(1) == "a1"
    assert ins.get_imm(2).abs_value == 0x100 - 4
    assert ins.get_imm(2).pcrel_value == -4


def test_invalid_immediate_val():
    ctx = InstructionContext()
    ctx.labels["test"] = 100

    ins = SimpleInstruction("addi", ("a0", "a1", "test2"), ctx, 0x100)

    with pytest.raises(
        NumberFormatException, match="test2 is neither a number now a known symbol"
    ):
        ins.get_imm(2)
