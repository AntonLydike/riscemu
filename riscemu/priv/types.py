import json
from collections import defaultdict
from dataclasses import dataclass
from functools import lru_cache
from typing import Tuple, Dict, Set

from riscemu.colors import FMT_NONE, FMT_PARSE
from riscemu.decoder import format_ins, RISCV_REGS, decode
from riscemu.priv.Exceptions import InstructionAccessFault, InstructionAddressMisalignedTrap, LoadAccessFault
from riscemu.types import Instruction, InstructionContext, T_RelativeAddress, MemoryFlags, T_AbsoluteAddress, \
    BinaryDataMemorySection


@dataclass(frozen=True)
class ElfInstruction(Instruction):
    name: str
    args: Tuple[int]
    encoded: int

    def get_imm(self, num: int) -> int:
        return self.args[num]

    def get_imm_reg(self, num: int) -> Tuple[int, int]:
        return self.args[-1], self.args[-2]

    def get_reg(self, num: int) -> str:
        return RISCV_REGS[self.args[num]]

    def __repr__(self) -> str:
        if self.name == 'jal' and self.args[0] == 0:
            return "j       {}".format(self.args[1])
        if self.name == 'addi' and self.args[2] == 0:
            return "mv      {}, {}".format(self.get_reg(0), self.get_reg(1))
        if self.name == 'addi' and self.args[1] == 0:
            return "li      {}, {}".format(self.get_reg(0), self.args[2])
        if self.name == 'ret' and len(self.args) == 0:
            return "ret"
        return format_ins(self.encoded, self.name)


class ElfMemorySection(BinaryDataMemorySection):
    def __init__(self, data: bytearray, name: str, context: InstructionContext, owner: str, base: int,
                 flags: MemoryFlags):
        super().__init__(data, name, context, owner, base=base, flags=flags)
        self.read_ins = lru_cache(maxsize=self.size // 4)(self.read_ins)

    def read_ins(self, offset):
        if not self.flags.executable:
            print(FMT_PARSE + "Reading instruction from non-executable memory!" + FMT_NONE)
            raise InstructionAccessFault(offset + self.base)
        if offset % 4 != 0:
            raise InstructionAddressMisalignedTrap(offset + self.base)
        return ElfInstruction(*decode(self.data[offset:offset + 4]))

    def write(self, offset: T_RelativeAddress, size: int, data: bytearray):
        if self.flags.read_only:
            raise LoadAccessFault('read-only section', offset + self.base, size, 'write')
        self.read_ins.cache_clear()
        return super(ElfMemorySection, self).write(offset, size, data)

    @property
    def end(self):
        return self.size + self.base


class MemoryImageDebugInfos:
    VERSION = '1.0.0'
    """
    Schema version
    """

    base: T_AbsoluteAddress = 0
    """
    The base address where the image starts. Defaults to zero.
    """

    sections: Dict[str, Dict[str, Tuple[int, int]]]
    """
    This dictionary maps a program and section to (start address, section length)
    """

    symbols: Dict[str, Dict[str, int]]
    """
    This dictionary maps a program and a symbol to a value
    """

    globals: Dict[str, Set[str]]
    """
    This dictionary contains the list of all global symbols of a given program
    """

    def __init__(self,
                 sections: Dict[str, Dict[str, Tuple[int, int]]],
                 symbols: Dict[str, Dict[str, int]],
                 globals: Dict[str, Set[str]],
                 base: int = 0
                 ):
        self.sections = sections
        self.symbols = symbols
        self.globals = globals
        for name in globals:
            globals[name] = set(globals[name])
        self.base = base

    def serialize(self) -> str:
        def serialize(obj: any) -> str:
            if isinstance(obj, defaultdict):
                return json.dumps(dict(obj), default=serialize)
            if isinstance(obj, (set, tuple)):
                return json.dumps(list(obj), default=serialize)
            return "<<unserializable {}>>".format(getattr(obj, '__qualname__', '{unknown}'))

        return json.dumps(
            dict(
                sections=self.sections,
                symbols=self.symbols,
                globals=self.globals,
                base=self.base,
                VERSION=self.VERSION
            ),
            default=serialize
        )

    @classmethod
    def load(cls, serialized_str: str) -> 'MemoryImageDebugInfos':
        json_obj: dict = json.loads(serialized_str)

        if 'VERSION' not in json_obj:
            raise RuntimeError("Unknown MemoryImageDebugInfo version!")

        version: str = json_obj.pop('VERSION')

        # compare major version
        if version != cls.VERSION and version.split('.')[0] != cls.VERSION.split('.')[0]:
            raise RuntimeError(
                "Unknown MemoryImageDebugInfo version! This emulator expects version {}, debug info version {}".format(
                    cls.VERSION, version
                )
            )

        return MemoryImageDebugInfos(**json_obj)

    @classmethod
    def builder(cls) -> 'MemoryImageDebugInfos':
        return MemoryImageDebugInfos(
            defaultdict(dict), defaultdict(dict), defaultdict(set)
        )
