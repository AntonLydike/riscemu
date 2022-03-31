from typing import Union, Tuple

from . import Instruction, T_RelativeAddress, InstructionContext
from ..helpers import parse_numeric_argument


class SimpleInstruction(Instruction):
    def __init__(self, name: str, args: Union[Tuple[()], Tuple[str], Tuple[str, str], Tuple[str, str, str]],
                 context: InstructionContext, addr: T_RelativeAddress):
        self.context = context
        self.name = name
        self.args = args
        self.addr = addr

    def get_imm(self, num: int) -> int:
        resolved_label = self.context.resolve_label(self.args[num], self.addr)
        if resolved_label is None:
            return parse_numeric_argument(self.args[num])
        return resolved_label

    def get_imm_reg(self, num: int) -> Tuple[int, str]:
        return self.get_imm(num + 1), self.get_reg(num)

    def get_reg(self, num: int) -> str:
        return self.args[num]

