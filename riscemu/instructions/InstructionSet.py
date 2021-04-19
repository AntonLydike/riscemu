import typing

from abc import ABC, abstractmethod
from ..CPU import *


class InstructionSet(ABC):
    """
    Represents a collection of instructions
    """

    def __init__(self, cpu: 'CPU'):
        self.cpu = cpu
        self.mmu = cpu.mmu
        self.regs = cpu.regs

    def load(self) -> typing.Dict[str, typing.Callable[['LoadedInstruction'], None]]:
        """
        This is called by the CPU once it instantiates this instruction set

        It returns a dictionary of all instructions in this instruction set,
        pointing to the correct handler for it
        """
        return {
            name: ins for name, ins in self.get_instructions()
        }

    def get_instructions(self):
        for member in dir(self):
            if member.startswith('instruction_'):
                yield member[12:].replace('_', '.'), getattr(self, member)

    def parse_mem_ins(self, ins: 'LoadedInstruction') -> Tuple[str, int]:
        """
        parses both rd, rs, imm and rd, imm(rs) arguments and returns (rd, imm+rs1)
        (so a register and address tuple for memory instructions)
        """
        if len(ins.args) == 3:
            # handle rd, rs1, imm
            rs = self.get_reg_content(ins, 1)
            imm = ins.get_imm(2)
        else:
            # handle rd, imm(rs1)
            ASSERT_LEN(ins.args, 2)
            ASSERT_IN("(", ins.args[1])
            imm, rs_name = ins.get_imm_reg(1)
            rs = self.regs.get(rs_name)
        rd = ins.get_reg(0)
        return rd, rs + imm

    def parse_rd_rs_rs(self, ins: 'LoadedInstruction') -> Tuple[str, int, int]:
        """
        Assumes the command is in <name> rd, rs1, rs2 format
        Returns the name of rd, and the values in rs1 and rs2
        """
        ASSERT_LEN(ins.args, 3)
        return ins.get_reg(0), self.get_reg_content(ins, 1), self.get_reg_content(ins, 2)

    def parse_rd_rs_imm(self, ins: 'LoadedInstruction') -> Tuple[str, int, int]:
        """
        Assumes the command is in <name> rd, rs, imm format
        Returns the name of rd, the value in rs and the immediate imm
        """
        ASSERT_LEN(ins.args, 3)
        return ins.get_reg(0), self.get_reg_content(ins, 1), ins.get_imm(2)

    def get_reg_content(self, ins: 'LoadedInstruction', ind: int) -> int:
        """
        get the register name from ins and then return the register contents
        """
        return self.regs.get(ins.get_reg(ind))

    @property
    def pc(self):
        return self.cpu.pc

    @pc.setter
    def pc(self, val):
        self.cpu.pc = val

    def __repr__(self):
        return "InstructionSet[{}] with {} instructions".format(
            self.__class__.__name__,
            len(list(self.get_instructions()))
        )
