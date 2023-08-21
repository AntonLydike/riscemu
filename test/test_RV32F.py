from dataclasses import dataclass
from typing import Iterable, List, Type
from riscemu import CPU
from riscemu.MMU import MMU
from riscemu.config import RunConfig
from riscemu.instructions import InstructionSet
from riscemu.instructions.RV32F import RV32F
from riscemu.registers import Registers
from riscemu.types import ProgramLoader
from riscemu.types.float32 import Float32
from riscemu.types.int32 import Int32
from riscemu.types.simple_instruction import SimpleInstruction


class MockInstruction(SimpleInstruction):
    ...


class MockRegisters(Registers):
    ...


class MockCPU(CPU):
    def __init__(self):
        self.regs = MockRegisters(True)

    @classmethod
    def get_loaders(cls) -> Iterable[type[ProgramLoader]]:
        assert False

    def run(self, verbose: bool = False):
        assert False

    def step(self, verbose: bool = False):
        assert False


def test_cvt_instructions():
    cpu = MockCPU()

    ins = MockInstruction("fcvt.s.w", ("fa0", "a0"), None, None)
    cpu.regs.set("a0", Int32(42))
    RV32F(cpu).instruction_fcvt_s_w(ins)
    assert 42.0 == cpu.regs.get_f("fa0")

    ins = MockInstruction("fcvt.w.s", ("a1", "fa1"), None, None)
    cpu.regs.set_f("fa1", Float32(42.0))
    RV32F(cpu).instruction_fcvt_w_s(ins)
    assert Int32(42) == cpu.regs.get("a1")
