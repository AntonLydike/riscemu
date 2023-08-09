from typing import Union, Tuple

from riscemu.types.immediate import Immediate

from . import Instruction, T_RelativeAddress, InstructionContext
from ..helpers import parse_numeric_argument, parse_numeric_argument_alt


class SimpleInstruction(Instruction):
    def __init__(
        self,
        name: str,
        args: Union[Tuple[()], Tuple[str], Tuple[str, str], Tuple[str, str, str]],
        context: InstructionContext,
        addr: T_RelativeAddress,
    ):
        self.context = context
        self.name = name
        self.args = args
        self.addr = addr

    def get_imm(self, num: int) -> int:
        resolved_label = self.context.resolve_label(self.args[num], self.addr)
        if resolved_label is None:
            return parse_numeric_argument(self.args[num])
        return resolved_label
    
    def get_imm_alt(self, num: int) -> Immediate:
        resolved_label = Immediate(self.context.resolve_label(self.args[num], self.addr), 1)
        if resolved_label.value is None:
            return parse_numeric_argument_alt(self.args[num])
        return resolved_label

    def get_imm_reg(self, num: int) -> Tuple[int, str]:
        return self.get_imm(num + 1), self.get_reg(num)

    def get_reg(self, num: int) -> str:
        return self.args[num]
