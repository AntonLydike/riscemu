from ..MMU import *
from abc import abstractmethod

import typing

from .ElfLoader import ElfExecutable

if typing.TYPE_CHECKING:
    from .PrivCPU import PrivCPU


class PrivMMU(MMU):
    cpu: 'PrivCPU'

    @abstractmethod
    def get_entrypoint(self) -> int:
        raise

    def set_cpu(self, cpu: 'PrivCPU'):
        self.cpu = cpu


class LoadedElfMMU(PrivMMU):
    def __init__(self, elf: ElfExecutable):
        super().__init__(conf=RunConfig())
        self.entrypoint = elf.symbols['_start']

        self.binaries.append(elf)
        for sec in elf.sections:
            self.sections.append(sec)

    def load_bin(self, exe: Executable) -> LoadedExecutable:
        raise NotImplementedError("This is a privMMU, it's initialized with a single ElfExecutable!")

    def allocate_section(self, name: str, req_size: int, flag: MemoryFlags):
        raise NotImplementedError("Not supported!")

    def get_entrypoint(self):
        return self.entrypoint
