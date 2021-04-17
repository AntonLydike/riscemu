from dataclasses import dataclass, field
from typing import Dict, List, Tuple, Union, Optional
from .Exceptions import *
from .helpers import parse_numeric_argument, align_addr

import typing
if typing.TYPE_CHECKING:
    from .Tokenizer import RiscVInstructionToken



@dataclass(frozen=True)
class MemoryFlags:
    read_only: bool
    executable: bool


@dataclass
class MemorySection:
    name: str
    flags: MemoryFlags
    size: int = 0
    content: List[bytearray] = field(default_factory=list)

    def add(self, data: bytearray):
        self.content.append(data)
        self.size += len(data)

    def continuous_content(self, parent: 'LoadedExecutable'):
        """
        converts the content into one continuous bytearray
        """
        if self.size == 0:
            return bytearray(0)
        content = self.content[0]
        for b in self.content[1:]:
            content += b
        return content


@dataclass
class InstructionMemorySection(MemorySection):
    content: List['RiscVInstructionToken'] = field(default_factory=list)

    def add_insn(self, insn: 'RiscVInstructionToken'):
        self.content.append(insn)
        self.size += 1

    def continuous_content(self, parent: 'LoadedExecutable'):
        return [
            LoadedInstruction(ins.instruction, ins.args, parent)
            for ins in self.content
        ]


@dataclass(frozen=True)
class Executable:
    run_ptr: Tuple[str, int]
    sections: Dict[str, MemorySection]
    symbols: Dict[str, Tuple[str, int]]
    stack_pref: Optional[int]


### LOADING CODE


@dataclass(frozen=True)
class LoadedInstruction:
    """
    An instruction which is loaded into memory. It knows the binary it belongs to to resolve symbols
    """
    name: str
    args: List[str]
    bin: 'LoadedExecutable'

    def get_imm(self, num: int):
        """
        parse and get immediate argument
        """
        if len(self.args) <= num:
            raise ParseException("Instruction {} expected argument at {} (args: {})".format(self.name, num, self.args))
        arg = self.args[num]
        # look up symbols
        if arg in self.bin.symbols:
            return self.bin.symbols[arg]
        return parse_numeric_argument(arg)

    def get_imm_reg(self, num: int):
        """
        parse and get an argument imm(reg)
        """
        if len(self.args) <= num:
            raise ParseException("Instruction {} expected argument at {} (args: {})".format(self.name, num, self.args))
        arg = self.args[num]
        ASSERT_IN("(", arg)
        imm, reg = arg[:-1].split("(")
        if imm in self.bin.symbols:
            return self.bin.symbols[imm], reg
        return parse_numeric_argument(imm), reg

    def get_reg(self, num: int):
        """
        parse and get an register argument
        """
        if len(self.args) <= num:
            raise ParseException("Instruction {} expected argument at {} (args: {})".format(self.name, num, self.args))
        return self.args[num]

    def __repr__(self):
        return "{} {}".format(self.name, ", ".join(self.args))


@dataclass(frozen=True)
class LoadedMemorySection:
    """
    A section which is loaded into memory
    """
    name: str
    base: int
    size: int
    content: Union[List[LoadedInstruction], bytearray]
    flags: MemoryFlags

    def read(self, offset: int, size: int):
        if offset < 0:
            raise MemoryAccessException('Invalid offset {}'.format(offset), self.base + offset, size, 'read')
        if offset + size >= self.size:
            raise MemoryAccessException('Outside section boundary of section {}'.format(self.name), self.base + offset,
                                        size, 'read')
        return self.content[offset: offset + size]

    def read_instruction(self, offset):
        if not self.flags.executable:
            raise MemoryAccessException('Section not executable!', self.base + offset, 1, 'read exec')

        if offset < 0:
            raise MemoryAccessException('Invalid offset {}'.format(offset), self.base + offset, 1, 'read exec')
        if offset >= self.size:
            raise MemoryAccessException('Outside section boundary of section {}'.format(self.name), self.base + offset,
                                        1, 'read exec')
        return self.content[offset]

    def write(self, offset, size, data):
        if self.flags.read_only:
            raise MemoryAccessException('Section not writeable {}'.format(self.name), self.base + offset, size, 'write')

        if offset < 0:
            raise MemoryAccessException('Invalid offset {}'.format(offset), self.base + offset, 1, 'write')
        if offset >= self.size:
            raise MemoryAccessException('Outside section boundary of section {}'.format(self.name), self.base + offset,
                                        size, 'write')

        for i in range(size):
            self.content[offset + i] = data[i]


class LoadedExecutable:
    """
    This represents an executable which is loaded into memory at address base_addr

    This is basicalle the "loader" in normal system environments
    It initializes the stack and heap

    It still holds a symbol table, that is not accessible memory since I don't want to deal with
    binary strings in memory etc.
    """
    base_addr: int
    sections_by_name: Dict[str, LoadedMemorySection]
    sections: List[LoadedMemorySection]
    symbols: Dict[str, int]
    run_ptr: int
    stack_heap: Tuple[int, int]  # pointers to stack and heap, are nullptr if no stack/heap is available

    def __init__(self, exe: Executable, base_addr: int):
        self.base_addr = base_addr
        self.sections = list()
        self.sections_by_name = dict()
        self.symbols = dict()

        # stack/heap if wanted
        if exe.stack_pref is not None:
            self.sections.append(LoadedMemorySection(
                'stack',
                base_addr,
                exe.stack_pref,
                bytearray(exe.stack_pref),
                MemoryFlags(read_only=False, executable=False)
            ))
            self.stack_heap = (self.base_addr, self.base_addr + exe.stack_pref)
        else:
            self.stack_heap = (0, 0)

        curr = base_addr
        for sec in exe.sections.values():
            loaded_sec = LoadedMemorySection(
                sec.name,
                curr,
                sec.size,
                sec.continuous_content(self),
                sec.flags
            )
            self.sections.append(loaded_sec)
            self.sections_by_name[loaded_sec.name] = loaded_sec
            curr = align_addr(loaded_sec.size + curr)

        for name, (sec_name, offset) in exe.symbols.items():
            ASSERT_IN(sec_name, self.sections_by_name)
            self.symbols[name] = self.sections_by_name[sec_name].base + offset

        self.size = curr - base_addr

        # translate run_ptr from executable
        run_ptr_sec, run_ptr_off = exe.run_ptr
        self.run_ptr = self.sections_by_name[run_ptr_sec].base + run_ptr_off

        print("successfully loaded binary\n\tsize: {}\n\tsections: {}\n\trun_ptr: 0x{:08x}".format(
            self.size,
            " ".join(self.sections_by_name.keys()),
            self.run_ptr
        ))
