"""
RiscEmu (c) 2021 Anton Lydike

SPDX-License-Identifier: MIT
"""

from .base_types import InstructionContext, Instruction, MemorySection, MemoryFlags, T_RelativeAddress, T_AbsoluteAddress, \
    Program
from .helpers import align_addr, int_from_bytes
from .exceptions import OutOfMemoryException, InvalidAllocationException
from .colors import *
from typing import Dict, List, Tuple, Optional


class MMU:
    """
    The MemoryManagementUnit (handles loading binaries, and reading/writing data)
    """

    max_size = 0xFFFFFFFF
    """
    The maximum size of the memory in bytes
    """

    max_alloc_size = 8 * 1024 * 1024 * 64
    """
    No single allocation can be bigger than 64 MB
    """

    sections: List[MemorySection]
    """
    A list of all loaded memory sections
    """

    programs: List[Program]
    """
    A list of all loaded programs
    """

    global_symbols: Dict[str, int]
    """
    The global symbol table
    """

    def __init__(self):
        """
        Create a new MMU
        """
        self.sections = list()
        self.global_symbols = dict()

    def get_sec_containing(self, addr: T_AbsoluteAddress) -> Optional[MemorySection]:
        """
        Returns the section that contains the address addr

        :param addr: the Address to look for
        :return: The LoadedMemorySection or None
        """
        for sec in self.sections:
            if sec.base <= addr < sec.base + sec.size:
                return sec
        return None

    def get_bin_containing(self, addr: T_AbsoluteAddress) -> Optional[Program]:
        for exe in self.binaries:
            if exe.base_addr <= addr < exe.base_addr + exe.size:
                return exe
        return None

    def read_ins(self, addr: T_AbsoluteAddress) -> Instruction:
        """
        Read a single instruction located at addr

        :param addr: The location
        :return: The Instruction
        """
        sec = self.get_sec_containing(addr)
        if sec is None:
            print(FMT_MEM + "[MMU] Trying to read instruction form invalid region! "
                            "Have you forgotten an exit syscall or ret statement?" + FMT_NONE)
            raise RuntimeError("No next instruction available!")
        return sec.read_ins(addr - sec.base)

    def read(self, addr: int, size: int) -> bytearray:
        """
        Read size bytes of memory at addr

        :param addr: The addres at which to start reading
        :param size: The number of bytes to read
        :return: The bytearray at addr
        """
        sec = self.get_sec_containing(addr)
        if sec is None:
            print(FMT_MEM + "[MMU] Trying to read data form invalid region at 0x{:x}! ".format(addr) + FMT_NONE)
            raise RuntimeError("Reading from uninitialized memory region!")
        return sec.read(addr - sec.base, size)

    def write(self, addr: int, size: int, data):
        """
        Write bytes into memory

        :param addr: The address at which to write
        :param size: The number of bytes to write
        :param data: The bytearray to write (only first size bytes are written)
        """
        sec = self.get_sec_containing(addr)
        if sec is None:
            print(FMT_MEM + '[MMU] Invalid write into non-initialized region at 0x{:08X}'.format(addr) + FMT_NONE)
            raise RuntimeError("No write pls")

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
            print(FMT_MEM + "[MMU] No section containing addr 0x{:08X}".format(addr) + FMT_NONE)
            return
        sec.dump(addr, *args, **kwargs)

    def label(self, symb: str):
        """
        Look up the symbol symb in all local symbol tables (and the global one)

        :param symb: The symbol name to look up
        """
        print(FMT_MEM + "[MMU] Lookup for symbol {}:".format(symb) + FMT_NONE)
        if symb in self.global_symbols:
            print("   Found global symbol {}: 0x{:X}".format(symb, self.global_symbols[symb]))
        for section in self.sections:
            if symb in section.context.labels:
                print("   Found local labels {}: 0x{:X} in {}".format(symb, section.context.labels[symb], section.name))

    def read_int(self, addr: int) -> int:
        return int_from_bytes(self.read(addr, 4))

    def __repr__(self):
        return "MMU(\n\t{}\n)".format(
            "\n\t".join(repr(x) for x in self.sections)
        )
