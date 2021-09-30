"""
Laods a memory image with debug information into memory
"""

import json
from functools import lru_cache
from typing import Dict, List, Optional, TYPE_CHECKING

from .ElfLoader import ElfInstruction, ElfLoadedMemorySection, InstructionAccessFault, InstructionAddressMisalignedTrap
from .PrivMMU import PrivMMU
from ..Config import RunConfig
from ..Executable import LoadedMemorySection, MemoryFlags
from ..IO.IOModule import IOModule
from ..colors import FMT_ERROR, FMT_NONE, FMT_MEM
from ..decoder import decode

if TYPE_CHECKING:
    pass


class MemoryImageMMU(PrivMMU):
    io: List[IOModule]
    data: bytearray
    io_start: int
    debug_info: Dict[str, Dict[str, Dict[str, str]]]

    def __init__(self, file_name: str, io_start: int = 0xFF0000):
        super(MemoryImageMMU, self).__init__(conf=RunConfig())

        with open(file_name, 'rb') as memf:
            data = memf.read()
        with open(file_name + '.dbg', 'r') as dbgf:
            debug_info: Dict = json.load(dbgf)

        self.data = bytearray(data)
        # TODO: super wasteful memory allocation happening here
        if len(data) < io_start:
            self.data += bytearray(io_start - len(data))
        self.debug_info = debug_info
        self.io_start = io_start
        self.io = list()

    def get_entrypoint(self):
        try:
            start = self.debug_info['symbols']['kernel'].get('_start', None)
            if start is not None:
                return start
            return self.debug_info['symbols']['kernel'].get('_ftext')
        except KeyError:
            print(FMT_ERROR + '[MMU] cannot find kernel entry in debug information! Falling back to 0x100' + FMT_NONE)
            return 0x100

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
        return "MemoryImageMMU()"

    @lru_cache(maxsize=32)
    def get_sec_containing(self, addr: int) -> Optional[LoadedMemorySection]:
        next_sec = len(self.data)
        for sec_addr, name in reversed(self.debug_info['sections'].items()):
            if addr >= int(sec_addr):
                owner, name = name.split(':')
                base = int(sec_addr)
                size = next_sec - base
                flags = MemoryFlags('.text' in name, '.text' in name)
                return ElfLoadedMemorySection(name, base, size, self.data[base:next_sec], flags, owner)
            else:
                next_sec = int(sec_addr)

    def translate_address(self, addr: int):
        sec = self.get_sec_containing(addr)
        if sec.name == '.empty':
            return "<empty>"
        symbs = self.debug_info['symbols'][sec.owner]
        for sym, val in reversed(symbs.items()):
            if addr >= val:
                return "{}{:+x} ({}:{})".format(sym, addr - val, sec.owner, sec.name)
        return "{}:{}{:+x}".format(sec.owner, sec.name, addr - sec.base)

    def symbol(self, symb: str):
        print(FMT_MEM + "Looking up symbol {}".format(symb))
        for owner, symbs in self.debug_info['symbols'].items():
            if symb in symbs:
                print("  Hit in {}: {} = {}".format(owner, symb, symbs[symb]))
        print(FMT_NONE, end="")
