"""
This file contains a base implementation of Instruction, and MemorySection.

This aims to be a simple base, usable for everyone who needs the basic functionality, but doesn't
want to set up their own subtypes of Instruction and MemorySection
"""

from typing import List, Tuple
from .exceptions import MemoryAccessException
from .helpers import parse_numeric_argument
from .types import Instruction, MemorySection, MemoryFlags, InstructionContext, T_RelativeAddress, \
    T_AbsoluteAddress, Program


class SimpleInstruction(Instruction):
    def __init__(self, name: str, args: Tuple[str], context: InstructionContext, addr: T_RelativeAddress):
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


class InstructionMemorySection(MemorySection):
    def __init__(self, instructions: List[Instruction], name: str, context: InstructionContext, owner: str, base: int = 0):
        self.name = name
        self.base = base
        self.context = context
        self.size = len(instructions) * 4
        self.flags = MemoryFlags(True, True)
        self.instructions = instructions
        self.owner = owner

    def read(self, offset: T_RelativeAddress, size: int) -> bytearray:
        raise MemoryAccessException("Cannot read raw bytes from instruction section", self.base + offset, size, 'read')

    def write(self, offset: T_RelativeAddress, size: int, data: bytearray):
        raise MemoryAccessException("Cannot write raw bytes to instruction section", self.base + offset, size, 'write')

    def read_ins(self, offset: T_RelativeAddress) -> Instruction:
        if offset % 4 != 0:
            raise MemoryAccessException("Unaligned instruction fetch!", self.base + offset, 4, 'instruction fetch')
        return self.instructions[offset // 4]


class BinaryDataMemorySection(MemorySection):
    def __init__(self, data: bytearray, name: str, context: InstructionContext, owner: str, base: int = 0, flags: MemoryFlags = None):
        self.name = name
        self.base = base
        self.context = context
        self.size = len(data)
        self.flags = flags if flags is not None else MemoryFlags(False, False)
        self.data = data
        self.owner = owner

    def read(self, offset: T_RelativeAddress, size: int) -> bytearray:
        if offset + size > self.size:
            raise MemoryAccessException("Out of bounds access in {}".format(self), offset, size, 'read')
        return self.data[offset:offset + size]

    def write(self, offset: T_RelativeAddress, size: int, data: bytearray):
        if offset + size > self.size:
            raise MemoryAccessException("Out of bounds access in {}".format(self), offset, size, 'write')
        if len(data[0:size]) != size:
            raise MemoryAccessException("Invalid write parameter sizing", offset, size, 'write')
        self.data[offset:offset + size] = data[0:size]

    def read_ins(self, offset: T_RelativeAddress) -> Instruction:
        raise MemoryAccessException("Tried reading instruction on non-executable section {}".format(self),
                                    offset, 4, 'instruction fetch')
