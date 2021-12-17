"""
RiscEmu (c) 2021 Anton Lydike

SPDX-License-Identifier: MIT

This file contains base classes which represent loaded programs
"""

import re
from abc import ABC
from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple, Set
from collections import defaultdict

from .helpers import *

T_RelativeAddress = int
T_AbsoluteAddress = int

NUMBER_SYMBOL_PATTERN = re.compile(r'^\d+[fb]$')


@dataclass(frozen=True)
class MemoryFlags:
    read_only: bool
    executable: bool

    def __repr__(self):
        return "{}({},{})".format(
            self.__class__.__name__,
            'ro' if self.read_only else 'rw',
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

    def __init__(self):
        self.labels = dict()
        self.numbered_labels = defaultdict(list)
        self.base_address = 0

    def resolve_label(self, symbol: str, address_at: Optional[T_RelativeAddress] = None) -> Optional[T_RelativeAddress]:
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
            return self.labels.get(symbol, None)


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

    @abstractmethod
    def read(self, offset: T_RelativeAddress, size: int) -> bytearray:
        pass

    @abstractmethod
    def write(self, offset: T_RelativeAddress, size: int, data: bytearray):
        pass

    @abstractmethod
    def read_ins(self, offset: T_RelativeAddress) -> Instruction:
        pass

    def dump(self, start: T_RelativeAddress, end: Optional[T_RelativeAddress], fmt: str = 'hex',
             bytes_per_row: int = 16, rows: int = 10, group: int = 4):
        if self.flags.executable:
            bytes_per_row = 4
        highlight = None
        if end is None:
            end = start + (bytes_per_row * (rows // 2))
            highlight = start
            start = start - (bytes_per_row * (rows // 2))
        if self.flags.executable:
            print(FMT_MEM + "{}, viewing {} instructions:".format(
                self, (end - start) // 4
            ) + FMT_NONE)

            for addr in range(start, end, 4):
                if addr == highlight:
                    print(FMT_UNDERLINE + FMT_ORANGE, end='')
                print("0x{:x}: {}{}".format(
                    self.base + addr, self.read_ins(addr), FMT_NONE
                ))
        else:
            print(FMT_MEM + "{}, viewing {} bytes:".format(
                self, (end - start)
            ) + FMT_NONE)

            for addr in range(start, end, bytes_per_row):
                hi_ind = (highlight - addr) // group
                print("0x{:x}: {}{}".format(
                    self.base + addr, format_bytes(self.read(addr, bytes_per_row), fmt, group, hi_ind), FMT_NONE
                ))

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
    name: str
    context: InstructionContext
    global_labels: Set[str]
    sections: List[MemorySection]
    base: T_AbsoluteAddress = 0

    def __init__(self, name: str, base: int = 0):
        self.name = name
        self.context = InstructionContext()
        self.sections = []
        self.base = base
        self.global_labels = set()

    def add_section(self, sec: MemorySection):
        self.sections.append(sec)

    def __repr__(self):
        return "{}(name={},context={},globals={},sections={},base={})".format(
            self.__class__.__name__, self.name, self.context, self.global_labels,
            [s.name for s in self.sections], self.base
        )
