from . import MemorySection, InstructionContext, MemoryFlags, T_RelativeAddress, Instruction
from ..types.exceptions import MemoryAccessException


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
