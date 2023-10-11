from typing import List, Type, Union, Set, Literal

from riscemu.colors import FMT_CPU, FMT_NONE
from riscemu.config import RunConfig
from riscemu.core import UserModeCPU
from riscemu.instructions import InstructionSet, Instruction, RV32F, RV32D

from dataclasses import dataclass

from snitch.regs import StreamingRegs


@dataclass(frozen=True)
class FrepState:
    rep_count: int
    ins_count: int
    mode: Literal["inner", "outer"]


class FrepEnabledCpu(UserModeCPU):
    repeat: Union[FrepState, None]
    allowed_ins: Set[str]

    def __init__(self, instruction_sets: List[Type["InstructionSet"]], conf: RunConfig):
        super().__init__(instruction_sets, conf)
        self.regs = StreamingRegs(self.mmu, infinite_regs=conf.unlimited_registers)
        self.repeats = None
        # only floating point instructions are allowed inside an frep!
        self.allowed_ins = set(x for x, y in RV32F(self).get_instructions())

    def step(self, verbose: bool = False):
        if self.repeats is None:
            super().step(verbose=verbose)
            return
        # get the spec
        spec: FrepState = self.repeats
        self.repeats = None

        instructions = [
            self.mmu.read_ins(self.pc + i * self.INS_XLEN)
            for i in range(spec.ins_count)
        ]

        for ins in instructions:
            if ins.name not in self.allowed_ins:
                # TODO: wrap in a nicer error type
                raise RuntimeError(
                    "Forbidden instruction inside frep loop: {}".format(ins)
                )

        if verbose:
            print(
                FMT_CPU
                + "┌────── floating point repetition ({}) {} times".format(
                    spec.mode, spec.rep_count + 1
                )
            )
            for i, ins in enumerate(instructions):
                print(
                    FMT_CPU
                    + "│  0x{:08X}:{} {}".format(
                        self.pc + i * self.INS_XLEN, FMT_NONE, ins
                    )
                )
            print(FMT_CPU + "└────── end of floating point repetition" + FMT_NONE)

        pc = self.pc
        if spec.mode == "outer":
            for _ in range(spec.rep_count + 1):
                for ins in instructions:
                    self.run_instruction(ins)
        elif spec.mode == "inner":
            for ins in instructions:
                for _ in range(spec.rep_count + 1):
                    self.run_instruction(ins)
        else:
            raise RuntimeError(f"Unknown frep mode: {spec.mode}")
        self.cycle += (spec.rep_count + 1) * spec.ins_count
        self.pc = pc + (spec.ins_count * self.INS_XLEN)


class Xfrep(InstructionSet):
    def instruction_frep_o(self, ins: Instruction):
        self.frep(ins, "outer")

    def instruction_frep_i(self, ins: Instruction):
        self.frep(ins, "inner")

    def frep(self, ins: Instruction, mode: Literal["inner", "outer"]):
        assert isinstance(self.cpu, FrepEnabledCpu)
        assert len(ins.args) == 4
        assert ins.get_imm(2).abs_value.value == 0, "staggering not supported yet"
        assert ins.get_imm(3).abs_value.value == 0, "staggering not supported yet"

        self.cpu.repeats = FrepState(
            rep_count=self.regs.get(ins.get_reg(0)).unsigned_value,
            ins_count=ins.get_imm(1).abs_value.value,
            mode=mode,
        )
