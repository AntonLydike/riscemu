"""
RiscEmu (c) 2021 Anton Lydike

SPDX-License-Identifier: MIT
"""

from .Config import RunConfig
from .Executable import Executable, LoadedExecutable, LoadedMemorySection, LoadedInstruction, MemoryFlags
from .helpers import align_addr
from .Exceptions import OutOfMemoryException, InvalidAllocationException
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

    sections: List[LoadedMemorySection]
    """
    A list of all loaded memory sections
    """

    binaries: List[LoadedExecutable]
    """
    A list of all loaded executables
    """

    last_bin: Optional[LoadedExecutable] = None
    """
    The last loaded executable (the next executable is inserted directly after this one)
    """

    global_symbols: Dict[str, int]
    """
    The global symbol table
    """

    def __init__(self, conf: RunConfig):
        """
        Create a new MMU, respecting the active RunConfiguration

        :param conf: The config to respect
        """
        self.sections: List[LoadedMemorySection] = list()
        self.binaries: List[LoadedExecutable] = list()
        self.first_free_addr: int = 0x100
        self.conf: RunConfig = conf
        self.global_symbols: Dict[str, int] = dict()

    def load_bin(self, exe: Executable) -> LoadedExecutable:
        """
        Load an executable into memory

        :param exe: the executable to load
        :return: A LoadedExecutable
        :raises OutOfMemoryException: When all memory is used
        """

        # align to 8 byte word
        addr = align_addr(self.first_free_addr)

        loaded_bin = LoadedExecutable(exe, addr, self.global_symbols)

        if loaded_bin.size + addr > self.max_size:
            raise OutOfMemoryException('load of executable')

        self.binaries.append(loaded_bin)
        self.first_free_addr = loaded_bin.base_addr + loaded_bin.size

        # read sections into sec dict
        for sec in loaded_bin.sections:
            self.sections.append(sec)

        self.global_symbols.update(loaded_bin.exported_symbols)

        print(FMT_MEM + "[MMU] Successfully loaded{}: {}".format(FMT_NONE, loaded_bin))

        return loaded_bin

    def allocate_section(self, name: str, req_size: int, flag: MemoryFlags):
        """
        Used to allocate a memory region (data only). Use `load_bin` if you want to load a binary, this is used for
        stack and maybe malloc in the future.

        :param name: Name of the section to allocate
        :param req_size: The requested size
        :param flag: The flags protecting this memory section
        :return: The LoadedMemorySection
        """
        if flag.executable:
            raise InvalidAllocationException('cannot allocate executable section', name, req_size, flag)

        if req_size < 0:
            raise InvalidAllocationException('Invalid size request', name, req_size, flag)

        if req_size > self.max_alloc_size:
            raise InvalidAllocationException('Cannot allocate more than {} bytes at a time'.format(self.max_alloc_size), name, req_size, flag)

        base = align_addr(self.first_free_addr)
        size = align_addr(req_size)
        sec = LoadedMemorySection(name, base, size, bytearray(size), flag, "<runtime>")
        self.sections.append(sec)
        self.first_free_addr = base + size
        return sec

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

    def get_bin_containing(self, addr: int) -> Optional[LoadedExecutable]:
        for exe in self.binaries:
            if exe.base_addr <= addr < exe.base_addr + exe.size:
                return exe
        return None

    def read_ins(self, addr: int) -> LoadedInstruction:
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
            print(FMT_MEM + "[MMU] No section containing addr 0x{:08X}".format(addr) + FMT_NONE)
            return
        sec.dump(addr, *args, **kwargs)

    def symbol(self, symb: str):
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
