from ..Executable import Executable, MemorySection, MemoryFlags, LoadedExecutable, LoadedMemorySection
from ..Exceptions import RiscemuBaseException
from ..helpers import FMT_PARSE, FMT_NONE
from ..colors import FMT_GREEN, FMT_BOLD

FMT_ELF = FMT_GREEN + FMT_BOLD

from .Exceptions import *

from dataclasses import dataclass

from typing import List, Dict, Union

from elftools.elf.elffile import ELFFile
from elftools.elf.sections import Section, SymbolTableSection

from ..decoder import decode

# This requires pyelftools package!

INCLUDE_SEC = ('.text', '.stack', '.bss')


class ElfExecutable:
    sections: List['ElfLoadedMemorySection']
    sections_by_name: Dict[str, 'ElfLoadedMemorySection']
    symbols: Dict[str, int]
    run_ptr: int

    def __init__(self, name: str):
        self.sections = list()
        self.sections_by_name = dict()
        self.symbols = dict()

        with open(name, 'rb') as f:
            print(FMT_ELF + "[ElfLoader] Loading elf executable from: {}".format(name) + FMT_NONE)
            self._read_elf(ELFFile(f))

    def _read_elf(self, elf: ELFFile):
        if not elf.header.e_machine == 'EM_RISCV':
            raise InvalidElfException("Not a RISC-V elf file!")
        if not elf.header.e_ident.EI_CLASS == 'ELFCLASS32':
            raise InvalidElfException("Only 32bit executables are supported!")

        self.run_ptr = elf.header.e_entry;

        for sec in elf.iter_sections():
            if isinstance(sec, SymbolTableSection):
                self._parse_symtab(sec)
                continue

            if sec.name not in INCLUDE_SEC:
                continue

            sec_ = self._lms_from_elf_sec(sec, 'kernel')
            self.sections.append(sec_)
            self.sections_by_name[sec.name] = sec_

    def _lms_from_elf_sec(self, sec: Section, owner: str):
        is_code = sec.name in ('.text',)
        data = sec.data()
        flags = MemoryFlags(is_code, is_code)
        print(FMT_ELF + "[ElfLoader] Section {} at: {:X}".format(sec.name, sec.header.sh_addr) + FMT_NONE)
        return ElfLoadedMemorySection(
            sec.name,
            sec.header.sh_addr,
            sec.data_size,
            data,
            flags,
            owner
        )

    def _parse_symtab(self, symtab: SymbolTableSection):
        self.symbols = {
            sym.name: sym.entry.st_value for sym in symtab.iter_symbols() if sym.name
        }

    def load_user_elf(self, name: str):
        pass


class InvalidElfException(RiscemuBaseException):
    def __init__(self, msg: str):
        super().__init__()
        self.msg = msg

    def message(self):
        return FMT_PARSE + "{}(\"{}\")".format(self.__class__.__name__, self.msg) + FMT_NONE


@dataclass(frozen=True)
class ElfInstruction:
    name: str
    args: List[Union[int, str]]
    encoded: int

    def get_imm(self, num: int):
        return self.args[-1]

    def get_imm_reg(self, num: int):
        return self.args[-1], self.args[-2]

    def get_reg(self, num: int):
        return self.args[num]

    def __repr__(self):
        return "{:<8} {}".format(
            self.name,
            ", ".join(map(str, self.args))
        )

class ElfLoadedMemorySection(LoadedMemorySection):
    def read_instruction(self, offset):
        if not self.flags.executable:
            print(FMT_PARSE + "Reading instruction from non-executable memory!" + FMT_NONE)
            raise InstructionAccessFault(offset + self.base)
        if offset % 4 != 0:
            raise InstructionAddressMisalignedTrap(offset + self.base)
        return ElfInstruction(*decode(self.content[offset:offset + 4]))
