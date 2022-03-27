from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Optional

from ..colors import FMT_MEM, FMT_NONE, FMT_UNDERLINE, FMT_ORANGE
from ..helpers import format_bytes
from . import MemoryFlags, T_AbsoluteAddress, InstructionContext, T_RelativeAddress, Instruction


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
