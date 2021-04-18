from .Config import RunConfig
from .Executable import Executable, LoadedExecutable, LoadedMemorySection
from .helpers import align_addr
from .Exceptions import OutOfMemoryEsception
from typing import Dict, List, Tuple, Optional


class MMU:
    max_size = 0xFFFFFFFF
    # make each block accessible by it's base addr
    sections: List[LoadedMemorySection]

    binaries: List[LoadedExecutable]
    last_bin: Optional[LoadedExecutable] = None

    def __init__(self, conf: RunConfig):
        self.sections = list()
        self.binaries = list()
        self.last_bin = None
        self.conf = conf

    def load_bin(self, bin: Executable):
        if self.last_bin is None:
            addr = 0x100  # start at 0x100 instead of 0x00
        else:
            addr = self.last_bin.size + self.last_bin.base_addr
        # align to 8 byte word
        addr = align_addr(addr)

        # apply preferred stack size from config
        if bin.stack_pref is None:
            bin.stack_pref = self.conf.preffered_stack_size

        loaded_bin = LoadedExecutable(bin, addr)

        if loaded_bin.size + addr > self.max_size:
            raise OutOfMemoryEsception('load of executable')

        self.binaries.append(loaded_bin)
        self.last_bin = loaded_bin

        # read sections into sec dict
        for sec in loaded_bin.sections:
            self.sections.append(sec)

        print("Successfully loaded {}".format(loaded_bin))

        return loaded_bin

    def get_sec_containing(self, addr: int):
        for sec in self.sections:
            if sec.base <= addr < sec.base + sec.size:
                return sec

    def read_ins(self, addr: int):
        sec = self.get_sec_containing(addr)
        return sec.read_instruction(addr - sec.base)

    def read(self, addr: int, size: int):
        sec = self.get_sec_containing(addr)
        return sec.read(addr - sec.base, size)

    def write(self, addr: int, size: int, data):
        sec = self.get_sec_containing(addr)
        return sec.write(addr - sec.base, size, data)

    # debugging interactions:
    def dump(self, addr, *args, **kwargs):
        self.get_sec_containing(addr).dump(addr, *args, **kwargs)