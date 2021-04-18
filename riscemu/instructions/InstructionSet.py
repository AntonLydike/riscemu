import typing

from abc import ABC, abstractmethod
from ..CPU import *


class InstructionSet(ABC):
    """
    Represents a collection of instructions
    """
    def __init__(self):
        self.cpu: typing.Optional['CPU'] = None
        self.mmu: typing.Optional['MMU'] = None
        self.regs: typing.Optional['Registers'] = None

    def load(self, cpu: 'CPU'):
        self.cpu = cpu
        self.mmu = cpu.mmu
        self.regs = cpu.regs

        return {
            name: ins for name, ins in self.get_instructions()
        }

    def get_instructions(self):
        for member in dir(self):
            if member.startswith('instruction_'):
                yield member[12:].replace('_', '.'), getattr(self, member)

    def parse_mem_ins(self, ins: 'LoadedInstruction'):
        return self.cpu.parse_mem_ins(ins)

    def parse_rd_rs_rs(self, ins: 'LoadedInstruction'):
        ASSERT_LEN(ins.args, 3)
        return ins.get_reg(0), self.get_reg_content(ins, 1), self.get_reg_content(ins, 2)

    def parse_rd_rs_imm(self, ins: 'LoadedInstruction'):
        ASSERT_LEN(ins.args, 3)
        return ins.get_reg(0), self.get_reg_content(ins, 1), ins.get_imm(2)

    def get_reg_content(self, ins: 'LoadedInstruction', ind: int):
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