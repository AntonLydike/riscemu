"""
RiscEmu (c) 2021 Anton Lydike

SPDX-License-Identifier: MIT
"""

from typing import Tuple, Callable, Dict

from abc import ABC
from ..CPU import CPU
from riscemu.types.exceptions import ASSERT_LEN, ASSERT_IN
from ..types import Instruction, Int32, UInt32


class InstructionSet(ABC):
    """
    Represents a collection of instructions

    Each instruction set has to inherit from this class. Each instruction should be it's own method:

    instruction_<name>(self, ins: LoadedInstruction)

    instructions containing a dot '.' should replace it with an underscore.
    """

    def __init__(self, cpu: 'CPU'):
        """Create a new instance of the Instruction set. This requires access to a CPU, and grabs vertain things
        from it such as access to the MMU and registers.
        """
        self.name = self.__class__.__name__
        self.cpu = cpu

    def load(self) -> Dict[str, Callable[['Instruction'], None]]:
        """
        This is called by the CPU once it instantiates this instruction set

        It returns a dictionary of all instructions in this instruction set,
        pointing to the correct handler for it
        """
        return {
            name: ins for name, ins in self.get_instructions()
        }

    def get_instructions(self):
        """
        Returns a list of all valid instruction names included in this instruction set

        converts underscores in names to dots
        """
        for member in dir(self):
            if member.startswith('instruction_'):
                yield member[12:].replace('_', '.'), getattr(self, member)

    def parse_mem_ins(self, ins: 'Instruction') -> Tuple[str, Int32]:
        """
        parses both rd, rs, imm and rd, imm(rs) argument format and returns (rd, imm+rs1)
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

    def parse_rd_rs_rs(self, ins: 'Instruction', signed=True) -> Tuple[str, Int32, Int32]:
        """
        Assumes the command is in <name> rd, rs1, rs2 format
        Returns the name of rd, and the values in rs1 and rs2
        """
        ASSERT_LEN(ins.args, 3)
        if signed:
            return ins.get_reg(0), \
                   self.get_reg_content(ins, 1), \
                   self.get_reg_content(ins, 2)
        else:
            return ins.get_reg(0), \
                   UInt32(self.get_reg_content(ins, 1)), \
                   UInt32(self.get_reg_content(ins, 2))

    def parse_rd_rs_imm(self, ins: 'Instruction', signed=True) -> Tuple[str, Int32, Int32]:
        """
        Assumes the command is in <name> rd, rs, imm format
        Returns the name of rd, the value in rs and the immediate imm
        """
        ASSERT_LEN(ins.args, 3)
        if signed:
            return ins.get_reg(0), \
                   Int32(self.get_reg_content(ins, 1)), \
                   Int32(ins.get_imm(2))
        else:
            return ins.get_reg(0), \
                   UInt32(self.get_reg_content(ins, 1)), \
                   UInt32(ins.get_imm(2))

    def parse_rs_rs_imm(self, ins: 'Instruction', signed=True) -> Tuple[Int32, Int32, Int32]:
        """
        Assumes the command is in <name> rs1, rs2, imm format
        Returns the values in rs1, rs2 and the immediate imm
        """
        if signed:
            return Int32(self.get_reg_content(ins, 0)), \
                   Int32(self.get_reg_content(ins, 1)), \
                   Int32(ins.get_imm(2))
        else:
            return UInt32(self.get_reg_content(ins, 0)), \
                   UInt32(self.get_reg_content(ins, 1)), \
                   UInt32(ins.get_imm(2))

    def get_reg_content(self, ins: 'Instruction', ind: int) -> Int32:
        """
        get the register name from ins and then return the register contents
        """
        return self.regs.get(ins.get_reg(ind))

    @property
    def pc(self):
        """
        shorthand for self.cpu.pc
        """
        return self.cpu.pc

    @pc.setter
    def pc(self, val):
        self.cpu.pc = val

    @property
    def mmu(self):
        return self.cpu.mmu

    @property
    def regs(self):
        return self.cpu.regs

    def __repr__(self):
        return "InstructionSet[{}] with {} instructions".format(
            self.__class__.__name__,
            len(list(self.get_instructions()))
        )
