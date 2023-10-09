from typing import List, Type, Union, Set

from riscemu.config import RunConfig
from riscemu.core import UserModeCPU
from riscemu.instructions import InstructionSet, Instruction, RV32F

from dataclasses import dataclass


@dataclass(frozen=True)
class FrepState:
    rep_count: int
    ins_count: int

    stagger_max: int
    stagger_mask: int


class FrepEnabledCpu(UserModeCPU):
    repeat: Union[FrepState, None]
    allowed_ins: Set[str]

    def __init__(self, instruction_sets: List[Type["InstructionSet"]], conf: RunConfig):
        self.repeats = None

        self.allowed_ins = set(x for x, y in RV32F(self).get_instructions())
        self.allowed_ins.union(set(x for x, y in Xfrep(self).get_instructions()))

        super().__init__(instruction_sets, conf)

    def step(self, verbose: bool = False, depth: int = 0):
        if self.repeats is None:
            assert (
                self.mmu.read_ins(self.pc).name in self.allowed_ins
            ), "must be a float ins"
            super().step(verbose=verbose)
            return

        if depth > 1:
            raise RuntimeError("frep depth exceeded?")

        # get the spec
        spec: FrepState = self.repeats
        self.repeats = None

        pc = self.pc
        for _ in range(spec.rep_count + 1):
            self.pc = pc
            c0 = self.cycle
            while self.cycle < c0 + spec.ins_count:
                self.step(verbose=verbose, depth=depth + 1)


class Xfrep(InstructionSet):
    def instruction_frep_o(self, ins: Instruction):
        self.frep(ins)

    def instruction_frep_i(self, ins: Instruction):
        self.frep(ins)

    def frep(self, ins: Instruction):
        assert isinstance(self.cpu, FrepEnabledCpu)
        assert len(ins.args) == 4
        self.cpu.repeats = FrepState(
            rep_count=self.regs.get(ins.get_reg(0)).unsigned_value,
            ins_count=ins.get_imm(1).abs_value.value,
            stagger_max=ins.get_imm(2).abs_value.value,
            stagger_mask=ins.get_imm(3).abs_value.value,
        )
