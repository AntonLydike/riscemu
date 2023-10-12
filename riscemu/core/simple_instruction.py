import re
from typing import Union, Tuple
from functools import lru_cache

from . import (
    Instruction,
    T_RelativeAddress,
    InstructionContext,
    Immediate,
    NumberFormatException,
)
from ..helpers import parse_numeric_argument

_NUM_LABEL_RE = re.compile(r"[0-9][fb]")
_INT_IMM_RE = re.compile(r"[+-]?([0-9]+|0x[A-Fa-f0-9]+)")


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
        self._addr = addr

    @property
    def addr(self) -> int:
        return self._addr + self.context.base_address

    @lru_cache(maxsize=None)
    def get_imm(self, num: int) -> Immediate:
        token = self.args[num]

        if _INT_IMM_RE.fullmatch(token):
            value = parse_numeric_argument(token)
            return Immediate(abs_value=value, pcrel_value=value - self.addr)

        # resolve label correctly
        if _NUM_LABEL_RE.fullmatch(token):
            value = self.context.resolve_numerical_label(token, self.addr)
        else:
            value = self.context.resolve_label(token)

        # TODO: make it raise a nice error instead
        if value is None:
            raise NumberFormatException(
                "{} is neither a number now a known symbol".format(token)
            )
        return Immediate(abs_value=value, pcrel_value=value - self.addr)

    def get_reg(self, num: int) -> str:
        return self.args[num]
