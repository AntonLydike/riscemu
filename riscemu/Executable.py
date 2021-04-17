from dataclasses import dataclass, field
from typing import Dict, List, Tuple
from . import MemoryFlags, RiscVInstructionToken, RiscVTokenizer, RiscVSymbolToken, RiscVPseudoOpToken
from .Exceptions import *


@dataclass
class MemorySection:
    name: str
    flags: MemoryFlags
    size: int = 0
    start: int = -1
    content: List[bytearray] = field(default_factory=list)

    def add(self, data: bytearray):
        self.content.append(data)
        self.size += len(data)


class InstructionMemorySection(MemorySection):
    insn: List[RiscVInstructionToken] = field(default_factory=list)

    def add_insn(self, insn: RiscVInstructionToken):
        self.insn.append(insn)
        self.size += 4


@dataclass
class Executable:
    run_ptr: Tuple[str, int]
    sections: Dict[str, MemorySection]
    symbols: Dict[str, Tuple[str, int]]

