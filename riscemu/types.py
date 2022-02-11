"""
RiscEmu (c) 2021 Anton Lydike

SPDX-License-Identifier: MIT

This file contains abstract base classes and types, bundling only the absolute basic functionality

See base.py for some basic implementations of these classes
"""
import os
import re
import typing
from abc import ABC, abstractmethod
from collections import defaultdict
from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple, Set, Union, Iterator, Callable, Type

from .colors import FMT_MEM, FMT_NONE, FMT_UNDERLINE, FMT_ORANGE, FMT_RED, FMT_BOLD
from .exceptions import ParseException
from .helpers import format_bytes, get_section_base_name
from .registers import Registers

if typing.TYPE_CHECKING:
    from .MMU import MMU
    from .instructions.instruction_set import InstructionSet

# define some base type aliases so we can keep track of absolute and relative addresses
T_RelativeAddress = int
T_AbsoluteAddress = int

# parser options are just dictionaries with arbitrary values
T_ParserOpts = Dict[str, any]

NUMBER_SYMBOL_PATTERN = re.compile(r'^\d+[fb]$')


@dataclass(frozen=True)
class MemoryFlags:
    read_only: bool
    executable: bool

    def __repr__(self):
        return "r{}{}".format(
            '-' if self.read_only else 'w',
            'x' if self.executable else '-'
        )


class InstructionContext:
    base_address: T_AbsoluteAddress
    """
    The address where the instruction block is placed
    """

    labels: Dict[str, T_RelativeAddress]
    """
    This dictionary maps all labels to their relative position of the instruction block
    """

    numbered_labels: Dict[str, List[T_RelativeAddress]]
    """
    This dictionary maps numbered labels (which can occur multiple times) to a list of (block-relative) addresses where 
    the label was placed 
    """

    global_symbol_dict: Dict[str, T_AbsoluteAddress]
    """
    A reference to the MMU's global symbol dictionary for access to global symbols
    """

    def __init__(self):
        self.labels = dict()
        self.numbered_labels = defaultdict(list)
        self.base_address = 0
        self.global_symbol_dict = dict()

    def resolve_label(self, symbol: str, address_at: Optional[T_RelativeAddress] = None) -> Optional[T_AbsoluteAddress]:
        if NUMBER_SYMBOL_PATTERN.match(symbol):
            if address_at is None:
                raise ParseException("Cannot resolve relative symbol {} without an address!".format(symbol))

            direction = symbol[-1]
            if direction == 'b':
                return max([addr for addr in self.numbered_labels.get(symbol[:-1], []) if addr < address_at],
                           default=None)
            else:
                return min([addr for addr in self.numbered_labels.get(symbol[:-1], []) if addr > address_at],
                           default=None)
        else:
            if symbol not in self.labels:
                return self.global_symbol_dict.get(symbol, None)
            value = self.labels.get(symbol, None)
            if value is None:
                return value
            return value + self.base_address


class Instruction(ABC):
    name: str
    args: tuple

    @abstractmethod
    def get_imm(self, num: int) -> int:
        """
        parse and get immediate argument
        """
        pass

    @abstractmethod
    def get_imm_reg(self, num: int) -> Tuple[int, str]:
        """
        parse and get an argument imm(reg)
        """
        pass

    @abstractmethod
    def get_reg(self, num: int) -> str:
        """
        parse and get an register argument
        """
        pass

    def __repr__(self):
        return "{} {}".format(self.name, ", ".join(self.args))


@dataclass
class MemorySection(ABC):
    name: str
    flags: MemoryFlags
    size: int
    base: T_AbsoluteAddress
    owner: str
    context: InstructionContext

    @property
    def end(self):
        return self.base + self.size

    @abstractmethod
    def read(self, offset: T_RelativeAddress, size: int) -> bytearray:
        pass

    @abstractmethod
    def write(self, offset: T_RelativeAddress, size: int, data: bytearray):
        pass

    @abstractmethod
    def read_ins(self, offset: T_RelativeAddress) -> Instruction:
        pass

    def dump(self, start: T_RelativeAddress, end: Optional[T_RelativeAddress] = None, fmt: str = 'hex',
             bytes_per_row: int = 16, rows: int = 10, group: int = 4):
        if self.flags.executable:
            bytes_per_row = 4
        highlight = None
        if end is None:
            end = min(start + (bytes_per_row * (rows // 2)), self.size - 1)
            highlight = start
            start = max(0, start - (bytes_per_row * (rows // 2)))

        if self.flags.executable:
            print(FMT_MEM + "{}, viewing {} instructions:".format(
                self, (end - start) // 4
            ) + FMT_NONE)

            for addr in range(start, end, 4):
                if addr == highlight:
                    print(FMT_UNDERLINE + FMT_ORANGE, end='')
                print("0x{:04x}: {}{}".format(
                    self.base + addr, self.read_ins(addr), FMT_NONE
                ))
        else:
            print(FMT_MEM + "{}, viewing {} bytes:".format(
                self, (end - start)
            ) + FMT_NONE)

            aligned_end = end - (end % bytes_per_row) if end % bytes_per_row != 0 else end

            for addr in range(start, aligned_end, bytes_per_row):
                hi_ind = (highlight - addr) // group if highlight is not None else -1
                print("0x{:04x}: {}{}".format(
                    self.base + addr, format_bytes(self.read(addr, bytes_per_row), fmt, group, hi_ind), FMT_NONE
                ))

            if aligned_end != end:
                hi_ind = (highlight - aligned_end) // group if highlight is not None else -1
                print("0x{:04x}: {}{}".format(
                    self.base + aligned_end, format_bytes(
                        self.read(aligned_end, end % bytes_per_row), fmt, group, hi_ind
                    ), FMT_NONE
                ))

    def dump_all(self, *args, **kwargs):
        self.dump(0, self.size, *args, **kwargs)

    def __repr__(self):
        return "{}[{}] at 0x{:08X} (size={}bytes, flags={}, owner={})".format(
            self.__class__.__name__,
            self.name,
            self.base,
            self.size,
            self.flags,
            self.owner
        )


class Program:
    """
    This represents a collection of sections which together form an executable program

    When you want to create a program which can be located anywhere in memory, set base to None,
    this signals the other components, that this is relocatable. Set the base of each section to
    the offset in the program, and everything will be taken care of for you.

    """
    name: str
    context: InstructionContext
    global_labels: Set[str]
    sections: List[MemorySection]
    base: Optional[T_AbsoluteAddress]
    is_loaded: bool

    @property
    def size(self):
        if len(self.sections) == 0:
            return 0
        if self.base is None:
            return self.sections[-1].base + self.sections[-1].size
        return (self.sections[-1].base - self.base) + self.sections[-1].size

    def __init__(self, name: str, base: Optional[int] = None):
        self.name = name
        self.context = InstructionContext()
        self.sections = []
        self.global_labels = set()
        self.base = base
        self.is_loaded = False

    def add_section(self, sec: MemorySection):
        # print a warning when a section is located before the programs base
        if self.base is not None:
            if sec.base < self.base:
                print(FMT_RED + FMT_BOLD + "WARNING: memory section {} in {} is placed before program base (0x{:x})".format(
                    sec, self.name, self.base
                ) + FMT_NONE)

        self.sections.append(sec)
        # keep section list ordered
        self.sections.sort(key=lambda section: section.base)

    def __repr__(self):
        return "{}(name={},globals={},sections={},base={})".format(
            self.__class__.__name__, self.name, self.global_labels,
            [s.name for s in self.sections], self.base
        )

    @property
    def entrypoint(self):
        base = 0 if self.base is None else self.base
        if '_start' in self.context.labels:
            return base + self.context.labels.get('_start')
        if 'main' in self.context.labels:
            return base + self.context.labels.get('main')
        for sec in self.sections:
            if get_section_base_name(sec.name) == '.text' and sec.flags.executable:
                return sec.base

    def loaded_trigger(self, at_addr: T_AbsoluteAddress):
        """
        This trigger is called when the binary is loaded and its final address in memory is determined

        This will do a small sanity check to prevent programs loading twice, or at addresses they don't
        expect to be loaded.

        :param at_addr: the address where the program will be located
        """
        if self.is_loaded:
            if at_addr != self.base:
                raise RuntimeError("Program loaded twice at different addresses! This will probably break things!")
            return

        if self.base is not None and self.base != at_addr:
            print(FMT_MEM + 'WARNING: Program loaded at different address then expected! (loaded at {}, '
                            'but expects to be loaded at {})'.format(at_addr, self.base) + FMT_NONE)

        # if the program is not located anywhere explicitly in memory, add the program address
        # to the defined section bases
        if self.base is None:
            for sec in self.sections:
                sec.base += at_addr

        if self.base is not None and self.base != at_addr:
            # move sections so they are located where they want to be located
            offset = at_addr - self.base
            for sec in self.sections:
                sec.base += offset

        self.base = at_addr
        self.context.base_address = at_addr


class ProgramLoader(ABC):
    """
    A program loader is always specific to a given source file. It is a place to store all state
    concerning the parsing and loading of that specific source file, including options.
    """

    def __init__(self, source_path: str, options: T_ParserOpts):
        self.source_path = source_path
        self.options = options
        self.filename = os.path.split(self.source_path)[-1]

    @classmethod
    @abstractmethod
    def can_parse(cls, source_path: str) -> float:
        """
        Return confidence that the file located at source_path
        should be parsed and loaded by this loader
        :param source_path: the path of the source file
        :return: the confidence that this file belongs to this parser
        """
        pass

    @classmethod
    @abstractmethod
    def get_options(cls, argv: list[str]) -> [List[str], T_ParserOpts]:
        """
        parse command line args into an options dictionary

        :param argv: the command line args list
        :return: all remaining command line args and the parser options object
        """
        pass

    @classmethod
    def instantiate(cls, source_path: str, options: T_ParserOpts) -> 'ProgramLoader':
        """
        Instantiate a loader for the given source file with the required arguments

        :param source_path: the path to the source file
        :param options: the parsed options (guaranteed to come from this classes get_options method.
        :return: An instance of a ProgramLoader for the spcified source
        """
        return cls(source_path, options)

    @abstractmethod
    def parse(self) -> Union[Program, Iterator[Program]]:
        """

        :return:
        """
        pass


class CPU(ABC):
    # static cpu configuration
    INS_XLEN: int = 4

    # housekeeping variables
    regs: Registers
    mmu: 'MMU'
    pc: T_AbsoluteAddress
    cycle: int
    halted: bool

    # debugging context
    debugger_active: bool

    # instruction information
    instructions: Dict[str, Callable[[Instruction], None]]
    instruction_sets: Set['InstructionSet']

    def __init__(self, mmu: 'MMU', instruction_sets: List[Type['InstructionSet']]):
        self.mmu = mmu
        self.regs = Registers()

        self.instruction_sets = set()
        self.instructions = dict()

        for set_class in instruction_sets:
            ins_set = set_class(self)
            self.instructions.update(ins_set.load())
            self.instruction_sets.add(ins_set)

        self.halted = False
        self.cycle = 0
        self.pc = 0
        self.debugger_active = False

        self.sections = list()
        self.programs = list()

    def run_instruction(self, ins: Instruction):
        """
        Execute a single instruction

        :param ins: The instruction to execute
        """
        if ins.name in self.instructions:
            self.instructions[ins.name](ins)
        else:
            # this should never be reached, as unknown instructions are imparseable
            raise RuntimeError("Unknown instruction: {}".format(ins))

    def load_program(self, program: Program):
        self.mmu.load_program(program)

    def __repr__(self):
        """
        Returns a representation of the CPU and some of its state.
        """
        return "{}(pc=0x{:08X}, cycle={}, halted={} instructions={})".format(
            self.__class__.__name__,
            self.pc,
            self.cycle,
            self.halted,
            " ".join(s.name for s in self.instruction_sets)
        )

    @abstractmethod
    def step(self, verbose=False):
        pass

    @abstractmethod
    def run(self, verbose=False):
        pass

    def launch(self, program: Program, verbose: bool = False):
        if program not in self.mmu.programs:
            print(FMT_RED + '[CPU] Cannot launch program that\'s not loaded!' + FMT_NONE)
            return

        self.pc = program.entrypoint
        self.run(verbose)
