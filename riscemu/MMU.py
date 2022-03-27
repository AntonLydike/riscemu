"""
RiscEmu (c) 2021 Anton Lydike

SPDX-License-Identifier: MIT
"""

from typing import Dict, List, Optional, Union

from .colors import *
from .helpers import align_addr
from .types import Instruction, MemorySection, MemoryFlags, T_AbsoluteAddress, \
    Program, InstructionContext, Int32
from .types.exceptions import InvalidAllocationException, MemoryAccessException


class MMU:
    """
    The MemoryManagementUnit. This provides a unified interface for reading/writing data from/to memory.

    It also provides various translations for addresses.
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
        self.programs = list()
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
        for program in self.programs:
            if program.base <= addr < program.base + program.size:
                return program
        return None

    def read_ins(self, addr: T_AbsoluteAddress) -> Instruction:
        """
        Read a single instruction located at addr

        :param addr: The location
        :return: The Instruction
        """
        sec = self.get_sec_containing(addr)
        if sec is None:
            print(FMT_MEM + "[MMU] Trying to read instruction form invalid region! (read at {}) ".format(addr)
                  + "Have you forgotten an exit syscall or ret statement?" + FMT_NONE)
            raise RuntimeError("No next instruction available!")
        return sec.read_ins(addr - sec.base)

    def read(self, addr: Union[int, Int32], size: int) -> bytearray:
        """
        Read size bytes of memory at addr

        :param addr: The addres at which to start reading
        :param size: The number of bytes to read
        :return: The bytearray at addr
        """
        if isinstance(addr, Int32):
            breakpoint()
            addr = addr.unsigned_value
        sec = self.get_sec_containing(addr)
        if sec is None:
            print(FMT_MEM + "[MMU] Trying to read data form invalid region at 0x{:x}! ".format(addr) + FMT_NONE)
            raise MemoryAccessException("region is non-initialized!", addr, size, 'read')
        return sec.read(addr - sec.base, size)

    def write(self, addr: int, size: int, data: bytearray):
        """
        Write bytes into memory

        :param addr: The address at which to write
        :param size: The number of bytes to write
        :param data: The bytearray to write (only first size bytes are written)
        """
        sec = self.get_sec_containing(addr)
        if sec is None:
            print(FMT_MEM + '[MMU] Invalid write into non-initialized region at 0x{:08X}'.format(addr) + FMT_NONE)
            raise MemoryAccessException("region is non-initialized!", addr, size, 'write')

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
        for bin in self.programs:
            if symb in bin.context.labels:
                print("   Found local labels {}: 0x{:X} in {}".format(symb, bin.context.labels[symb], bin.name))

    def read_int(self, addr: int) -> Int32:
        return Int32(self.read(addr, 4))

    def translate_address(self, address: T_AbsoluteAddress) -> str:
        sec = self.get_sec_containing(address)
        if not sec:
            return "unknown at 0x{:0x}".format(address)

        bin = self.get_bin_containing(address)
        secs = set(sec.name for sec in bin.sections) if bin else []
        elf_markers = {
            '__global_pointer$', '_fdata', '_etext', '_gp',
            '_bss_start', '_bss_end', '_ftext', '_edata', '_end', '_fbss'
        }

        def key(x):
            name, val = x
            return address - val

        best_fit = iter(sorted(filter(lambda x: x[1] <= address, sec.context.labels.items()), key=key))

        best = ('', float('inf'))
        for name, val in best_fit:
            if address - val < best[1]:
                best = (name, val)
            if address - val == best[1]:
                if best[0] in elf_markers:
                    best = (name, val)
                elif best[0] in secs and name not in elf_markers:
                    best = (name, val)

        name, val = best

        if not name:
            return "unknown at 0x{:0x}".format(address)

        return str('{}:{} at {} (0x{:0x}) + 0x{:0x}'.format(
            sec.owner, sec.name, name, val, address - val
        ))

    def has_continous_free_region(self, start: int, end: int) -> bool:
        # if we have no sections we are all good
        if len(self.sections) == 0:
            return True
        # if the last section is located before the start we are also good
        if start >= self.sections[-1].base + self.sections[-1].size:
            return True

        for sec in self.sections:
            # skip all sections that end before the required start point
            if sec.base + sec.size <= start:
                continue
            # we now have the first section that doesn't end **before** the start point
            # if this section starts after the specified end, we are good
            if sec.base >= end:
                return True
            # otherwise we can't continue
            return False
        # if all sections end before the requested start we are good
        # technically we shouldn't ever reach this point, but better safe than sorry
        return True

    def load_program(self, program: Program, align_to: int = 4):
        if program.base is not None:
            if not self.has_continous_free_region(program.base, program.base + program.size):
                print(FMT_MEM + "Cannot load program {} into desired space (0x{:0x}-0x{:0x}), area occupied.".format(
                    program.name, program.base, program.base + program.size
                ) + FMT_NONE)
                raise InvalidAllocationException("Area occupied".format(
                    program.name, program.base, program.base + program.size
                ), program.name, program.size, MemoryFlags(False, True))

            at_addr = program.base
        else:
            at_addr = align_addr(self.get_guaranteed_free_address(), align_to)

        # trigger the load event to set all addresses in the binary
        program.loaded_trigger(at_addr)

        # add program and sections to internal state
        self.programs.append(program)
        self.sections += program.sections
        self._update_state()

        # load all global symbols from program
        self.global_symbols.update(
            {key: program.context.labels[key] for key in program.global_labels}
        )
        # inject reference to global symbol table into program context
        # FIXME: this is pretty unclean and should probably be solved in a better way in the future
        program.context.global_symbol_dict = self.global_symbols

    def load_section(self, sec: MemorySection, fixed_position: bool = False) -> bool:
        if fixed_position:
            if self.has_continous_free_region(sec.base, sec.base + sec.size):
                self.sections.append(sec)
                self._update_state()
            else:
                print(FMT_MEM + '[MMU] Cannot place section {} at {}, space is occupied!'.format(sec, sec.base))
                return False
        else:
            at_addr = align_addr(self.get_guaranteed_free_address(), 8)
            sec.base = at_addr
            self.sections.append(sec)
            self._update_state()
            return True

    def _update_state(self):
        """
        Called whenever a section or program is added to keep the list of programs and sections consistent
        :return:
        """
        self.programs.sort(key=lambda bin: bin.base)
        self.sections.sort(key=lambda sec: sec.base)

    def get_guaranteed_free_address(self) -> T_AbsoluteAddress:
        if len(self.sections) == 0:
            return 0x100
        else:
            return self.sections[-1].base + self.sections[-1].size

    def __repr__(self):
        return "{}(\n\t{}\n)".format(
            self.__class__.__name__,
            "\n\t".join(repr(x) for x in self.programs)
        )

    def context_for(self, addr: T_AbsoluteAddress) -> InstructionContext:
        sec = self.get_sec_containing(addr)

        if sec is not None:
            return sec.context

        return InstructionContext()

    def report_addr(self, addr: T_AbsoluteAddress):
        sec = self.get_sec_containing(addr)
        if not sec:
            print("addr is in no section!")
            return
        owner = [b for b in self.programs if b.name == sec.owner]
        if owner:
            print("owned by: {}".format(owner[0]))

        print("{}: 0x{:0x} + 0x{:0x}".format(name, val, addr - val))
