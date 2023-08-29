from abc import ABC, abstractmethod
from typing import Union
from .int32 import Int32


class Immediate:
    """
    This class solves a problem of ambiguity when interpreting assembly code.

    Let's look at the following four cases (assuming 1b is 16 bytes back):
     a) beq     a0, a1, 1b      // conditional jump 16 bytes back
     b) beq     a0, a1, -16     // conditional jump 16 bytes back
     c) addi    a0, a1, 1b      // subtract (pc - 16) from a1
     d) addi    a0, a1, -16     // subtract 16 from a1

    We want a and b to behave the same, but c and d not to.

    The Immediate class solves this problem, by giving each instruction two ways of
    interpreting a given immediate. It can either get the "absolute value" of the
    immediate, or it's relative value to the PC.

    In this case, the beq instruction would interpret both as PC relative values,
    while addi would treat them as absolute values.
    """

    abs_value: Int32
    pcrel_value: Int32

    __slots__ = ["abs_value", "pcrel_value"]

    def __init__(self, abs_value: Union[int, Int32], pcrel_value: Union[int, Int32]):
        self.abs_value = Int32(abs_value)
        self.pcrel_value = Int32(pcrel_value)


class Instruction(ABC):
    name: str
    args: tuple

    @abstractmethod
    def get_imm(self, num: int) -> Immediate:
        """
        parse and get immediate argument
        """
        pass

    @abstractmethod
    def get_reg(self, num: int) -> str:
        """
        parse and get an register argument
        """
        pass

    def __repr__(self):
        return "{} {}".format(self.name, ", ".join(self.args))


class InstructionWithEncoding(ABC):
    """
    Mixin for instructions that have encodings
    """

    @property
    @abstractmethod
    def encoding(self) -> int:
        raise NotImplementedError()
