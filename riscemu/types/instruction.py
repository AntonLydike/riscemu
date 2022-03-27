from abc import ABC, abstractmethod
from typing import Tuple


class Instruction(ABC):
    name: str
    args: tuple

    @abstractmethod
    def get_imm(self, num: int) -> int:
        """
        parse and get immediate argument
        """
        pass

    @abstractmethod
    def get_imm_reg(self, num: int) -> Tuple[int, str]:
        """
        parse and get an argument imm(reg)
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
