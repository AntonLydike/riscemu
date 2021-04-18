import typing

from abc import ABC, abstractmethod
from ..CPU import *


class InstructionSet(ABC):
    """
    Represents a collection of instructions
    """
    def __init__(self, name):
        self.name = name
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

    @property
    def pc(self):
        return self.cpu.pc

    @pc.setter
    def pc(self, val):
        self.cpu.pc = val

    def __repr__(self):
        return "InstructionSet[{}] with {} instructions".format(
            self.name,
            len(list(self.get_instructions()))
        )