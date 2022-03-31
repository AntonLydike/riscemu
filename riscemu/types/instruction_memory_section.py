from typing import List

from . import MemorySection, Instruction, InstructionContext, MemoryFlags, T_RelativeAddress
from .exceptions import MemoryAccessException


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

