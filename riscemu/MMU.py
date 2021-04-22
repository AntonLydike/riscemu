"""
RiscEmu (c) 2021 Anton Lydike

SPDX-License-Identifier: BSD-2-Clause
"""

from .Config import RunConfig
from .Executable import Executable, LoadedExecutable, LoadedMemorySection, LoadedInstruction
from .helpers import align_addr
from .Exceptions import OutOfMemoryException
from .colors import *
from typing import Dict, List, Tuple, Optional


class MMU:
    """
    The MemoryManagementUnit (handles loading binaries, and reading/writing data)
    """

    """
    The maximum size of the memory in bytes
    """
    max_size = 0xFFFFFFFF

    """
    A list of all loaded memory sections
    """
    sections: List[LoadedMemorySection]

    """
    A list of all loaded executables
    """
    binaries: List[LoadedExecutable]

    """
    The last loaded executable (the next executable is inserted directly after this one)
    """
    last_bin: Optional[LoadedExecutable] = None

    """
    The global symbol table
    """
    global_symbols: Dict[str, int]

    def __init__(self, conf: RunConfig):
        self.sections = list()
        self.binaries = list()
        self.last_bin = None
        self.conf = conf
        self.global_symbols = dict()

    def load_bin(self, bin: Executable) -> LoadedExecutable:
        """
        Load an executable into memory
        :param bin: the executable to load
        :return: A LoadedExecutable
        :raises OutOfMemoryException: When all memory is used
        """
        if self.last_bin is None:
            addr = 0x100  # start at 0x100 instead of 0x00
        else:
            addr = self.last_bin.size + self.last_bin.base_addr
        # align to 8 byte word
        addr = align_addr(addr)

        # apply preferred stack size from config
        if bin.stack_pref is None:
            bin.stack_pref = self.conf.preffered_stack_size

        loaded_bin = LoadedExecutable(bin, addr, self.global_symbols)

        if loaded_bin.size + addr > self.max_size:
            raise OutOfMemoryException('load of executable')

        self.binaries.append(loaded_bin)
        self.last_bin = loaded_bin

        # read sections into sec dict
        for sec in loaded_bin.sections:
            self.sections.append(sec)

        self.global_symbols.update(loaded_bin.exported_symbols)

        print(FMT_MEM + "[MMU] Successfully loaded{}: {}".format(FMT_NONE, loaded_bin))

        return loaded_bin

    def get_sec_containing(self, addr: int) -> Optional[LoadedMemorySection]:
        """
        Returns the section that contains the address addr
        :param addr: the Address to look for
        :return: The LoadedMemorySection or None
        """
        for sec in self.sections:
            if sec.base <= addr < sec.base + sec.size:
                return sec
        return None

    def read_ins(self, addr: int) -> LoadedInstruction:
        """
        Read a single instruction located at addr
        :param addr: The location
        :return: The Instruction
        """
        sec = self.get_sec_containing(addr)
        return sec.read_instruction(addr - sec.base)

    def read(self, addr: int, size: int) -> bytearray:
        """
        Read size bytes of memory at addr
        :param addr: The addres at which to start reading
        :param size: The number of bytes to read
        :return: The bytearray at addr
        """
        sec = self.get_sec_containing(addr)
        return sec.read(addr - sec.base, size)

    def write(self, addr: int, size: int, data):
        """
        Write bytes into memory
        :param addr: The address at which to write
        :param size: The number of bytes to write
        :param data: The bytearray to write (only first size bytes are written)
        """
        sec = self.get_sec_containing(addr)
        return sec.write(addr - sec.base, size, data)

    def dump(self, addr, *args, **kwargs):
        """
        Dumpy the memory contents

        :param addr: The address at which to dump
        :param args: args for the dump function of the loaded memory section
        :param kwargs: kwargs for the dump function of the loaded memory section
        """
        sec = self.get_sec_containing(addr)
        if sec is None:
            return
        sec.dump(addr, *args, **kwargs)

    def symbol(self, symb:str):
        """
        Look up the symbol symb in all local symbol tables (and the global one)
        :param symb: The symbol name to look up
        """
        print(FMT_MEM + "[MMU] Lookup for symbol {}:".format(symb) + FMT_NONE)
        if symb in self.global_symbols:
            print("   Found global symbol {}: 0x{:X}".format(symb, self.global_symbols[symb]))
        for b in self.binaries:
            if symb in b.symbols:
                print("   Found local symbol {}: 0x{:X} in {}".format(symb, b.symbols[symb], b.name))

    def __repr__(self):
        return "MMU(\n\t{}\n)".format(
            "\n\t".join(repr(x) for x in self.sections)
        )