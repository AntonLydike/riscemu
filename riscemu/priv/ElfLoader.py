from typing import List

from .Exceptions import *
from .types import ElfMemorySection
from ..helpers import FMT_PARSE, FMT_NONE, FMT_GREEN, FMT_BOLD
from ..types import MemoryFlags, Program, ProgramLoader, T_ParserOpts

FMT_ELF = FMT_GREEN + FMT_BOLD

if typing.TYPE_CHECKING:
    from elftools.elf.elffile import ELFFile
    from elftools.elf.sections import Section, SymbolTableSection

INCLUDE_SEC = ('.text', '.stack', '.bss', '.sdata', '.sbss')


class ElfBinaryFileLoader(ProgramLoader):
    """
    Loads compiled elf binaries (checks for the magic sequence 7f45 4c46)

    This loader respects local and global symbols.
    """
    program: Program

    def __init__(self, source_path: str, options: T_ParserOpts):
        super().__init__(source_path, options)
        self.program = Program(self.filename)

    @classmethod
    def can_parse(cls, source_path: str) -> float:
        with open(source_path, 'rb') as f:
            if f.read(4) == b'\x7f\x45\x4c\x46':
                return 1
        return 0

    @classmethod
    def get_options(cls, argv: list[str]) -> [List[str], T_ParserOpts]:
        return argv, {}

    def parse(self) -> Program:
        try:
            from elftools.elf.elffile import ELFFile
            from elftools.elf.sections import Section, SymbolTableSection

            with open(self.source_path, 'rb') as f:
                print(FMT_ELF + "[ElfLoader] Loading elf executable from: {}".format(self.source_path) + FMT_NONE)
                self._read_elf(ELFFile(f))
        except ImportError as e:
            print(FMT_PARSE + "[ElfLoader] Cannot load elf files without PyElfTools package! You can install them "
                              "using pip install pyelftools!" + FMT_NONE)
            raise e

        return self.program

    def _read_elf(self, elf: 'ELFFile'):
        if not elf.header.e_machine == 'EM_RISCV':
            raise InvalidElfException("Not a RISC-V elf file!")
        if not elf.header.e_ident.EI_CLASS == 'ELFCLASS32':
            raise InvalidElfException("Only 32bit executables are supported!")

        from elftools.elf.sections import SymbolTableSection
        for sec in elf.iter_sections():
            if isinstance(sec, SymbolTableSection):
                self._parse_symtab(sec)
                continue

            if sec.name not in INCLUDE_SEC:
                continue

            self._add_sec(self._lms_from_elf_sec(sec, self.filename))

    def _lms_from_elf_sec(self, sec: 'Section', owner: str):
        is_code = sec.name in ('.text',)
        data = bytearray(sec.data())
        if len(data) < sec.data_size:
            data += bytearray(len(data) - sec.data_size)
        flags = MemoryFlags(is_code, is_code)
        print(FMT_ELF + "[ElfLoader] Section {} at: {:X}".format(sec.name, sec.header.sh_addr) + FMT_NONE)
        return ElfMemorySection(
            data, sec.name, self.program.context, owner, sec.header.sh_addr, flags
        )

    def _parse_symtab(self, symtab: 'SymbolTableSection'):
        from elftools.elf.enums import ENUM_ST_VISIBILITY

        for sym in symtab.iter_symbols():
            if not sym.name:
                continue
            self.program.context.labels[sym.name] = sym.entry.st_value
            # check if it has st_visibility bit set
            if sym.entry.st_info.bind == 'STB_GLOBAL':
                self.program.global_labels.add(sym.name)
                print(FMT_PARSE + "LOADED GLOBAL SYMBOL {}: {}".format(sym.name, sym.entry.st_value) + FMT_NONE)

    def _add_sec(self, new_sec: 'ElfMemorySection'):
        for sec in self.program.sections:
            if sec.base < sec.end <= new_sec.base or sec.end > sec.base >= new_sec.end:
                continue
            else:
                print(FMT_ELF + "[ElfLoader] Invalid elf layout: Two sections overlap: \n\t{}\n\t{}".format(
                    sec, new_sec
                ) + FMT_NONE)
                raise RuntimeError("Cannot load elf with overlapping sections!")

        self.program.add_section(new_sec)
