from ..MMU import *

import typing

from .ElfLoader import ElfExecutable

class PrivMMU(MMU):
    def __init__(self, elf: ElfExecutable):
        super(PrivMMU, self).__init__(conf=RunConfig())

        self.binaries.append(elf)
        for sec in elf.sections:
            self.sections.append(sec)

    def load_bin(self, exe: Executable) -> LoadedExecutable:
        raise NotImplementedError("This is a privMMU, it's initialized with a single ElfExecutable!")

    def allocate_section(self, name: str, req_size: int, flag: MemoryFlags):
        raise NotImplementedError("Not supported!")






