"""
Laods a memory image with debug information into memory
"""

from ..MMU import MMU
from ..Config import RunConfig
from ..Executable import Executable, LoadedExecutable, LoadedMemorySection, LoadedInstruction, MemoryFlags
from .ElfLoader import ElfInstruction, ElfLoadedMemorySection, InstructionAccessFault, InstructionAddressMisalignedTrap
from ..decoder import decode
from ..IO.IOModule import IOModule
from .privmodes import PrivModes
from ..colors import FMT_ERROR, FMT_NONE

from functools import lru_cache
from typing import Dict, List, Tuple, Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from .PrivCPU import PrivCPU


class ContinuousMMU(MMU):
    io: List[IOModule]
    data: bytearray
    io_start: int
    debug_info: Dict[str, Dict[str, str]]

    def __init__(self, data: bytes, debug_info: Dict, cpu, io_start: int = 0xFF0000):
        super(ContinuousMMU, self).__init__(conf=RunConfig())
        self.cpu: 'PrivCPU' = cpu
        self.data = bytearray(data)
        if len(data) < io_start:
            self.data += bytearray(io_start - len(data))
        self.debug_info = debug_info
        self.io_start = io_start
        self.io = list()
        self.kernel_end = 0
        for start, name in debug_info['sections'].items():
            if name.startswith('programs'):
                self.kernel_end = int(start)
                break

    @lru_cache(maxsize=2048)
    def read_ins(self, addr: int) -> ElfInstruction:
        if addr >= self.io_start:
            raise InstructionAccessFault(addr)
        if addr % 4 != 0:
            raise InstructionAddressMisalignedTrap(addr)

        return ElfInstruction(*decode(self.data[addr:addr + 4]))

    def read(self, addr: int, size: int) -> bytearray:
        if addr < 0x100:
            pc = self.cpu.pc
            text_sec = self.get_sec_containing(pc)
            print(FMT_ERROR + "[MMU] possible null dereference (read {:x}) from (pc={:x},sec={},rel={:x})".format(
                addr, pc, text_sec.owner + ':' + text_sec.name, pc - text_sec.base
            ) + FMT_NONE)
        if addr >= self.io_start:
            return self.io_at(addr).read(addr, size)
        return self.data[addr: addr + size]

    def write(self, addr: int, size: int, data):
        if addr < 0x100:
            pc = self.cpu.pc
            text_sec = self.get_sec_containing(pc)
            print(FMT_ERROR + "[MMU] possible null dereference (write {:x}) from (pc={:x},sec={},rel={:x})".format(
                addr, pc, text_sec.owner + ':' + text_sec.name, pc - text_sec.base
            ) + FMT_NONE)
        if addr < self.kernel_end:
            if self.cpu.mode != PrivModes.MACHINE:
                pc = self.cpu.pc
                text_sec = self.get_sec_containing(pc)
                print(FMT_ERROR + "[MMU] kernel access to {:x} from outside kernel mode! (pc={:x},sec={},rel={:x})".format(
                    addr, pc, text_sec.owner + ':' + text_sec.name, pc - text_sec.base
                ) + FMT_NONE)

        if addr >= self.io_start:
            return self.io_at(addr).write(addr, data, size)
        self.data[addr:addr + size] = data[0:size]

    def io_at(self, addr) -> IOModule:
        for mod in self.io:
            if mod.contains(addr):
                return mod
        raise InstructionAccessFault(addr)

    def add_io(self, io: IOModule):
        self.io.append(io)

    def __repr__(self):
        return "ImageMMU()"

    @lru_cache(maxsize=32)
    def get_sec_containing(self, addr: int) -> Optional[LoadedMemorySection]:
        next_sec = len(self.data)
        for sec_addr, name in sorted(self.debug_info['sections'].items(), key=lambda x: int(x[0]), reverse=True):
            if addr >= int(sec_addr):
                owner, name = name.split(':')
                base = int(sec_addr)
                size = next_sec - base
                flags = MemoryFlags('.text' in name, '.text' in name)
                return ElfLoadedMemorySection(name, base, size, self.data[base:next_sec], flags, owner)
            else:
                next_sec = int(sec_addr)
