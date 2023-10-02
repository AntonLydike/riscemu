from abc import ABC
from typing import Optional

from riscemu.core import MemorySection, MemoryFlags, T_RelativeAddress


class IOModule(MemorySection, ABC):
    def __init__(
        self,
        name: str,
        flags: MemoryFlags,
        size: int,
        owner: str = "system",
        base: int = 0,
    ):
        super(IOModule, self).__init__(name, flags, size, base, owner, None)

    def contains(self, addr, size: int = 0):
        return (
            self.base <= addr < self.base + self.size
            and self.base <= addr + size <= self.base + self.size
        )

    def dump(self, *args, **kwargs):
        print(self)

    def __repr__(self):
        return "{}[{}] at 0x{:0X} (size={}bytes, flags={})".format(
            self.__class__.__name__, self.name, self.base, self.size, self.flags
        )
