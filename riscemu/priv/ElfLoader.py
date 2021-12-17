from dataclasses import dataclass
from typing import List, Dict, Tuple

from .Exceptions import *
from ..exceptions import RiscemuBaseException
from ..base_types import MemoryFlags, LoadedMemorySection
from ..decoder import decode, RISCV_REGS, format_ins
from ..helpers import FMT_PARSE, FMT_NONE, FMT_GREEN, FMT_BOLD

FMT_ELF = FMT_GREEN + FMT_BOLD

if typing.TYPE_CHECKING:
    from elftools.elf.elffile import ELFFile
    from elftools.elf.sections import Section, SymbolTableSection

# This requires pyelftools package!

INCLUDE_SEC = ('.text', '.stack', '.bss', '.sdata', '.sbss')


class ElfExecutable:
    sections: List['ElfLoadedMemorySection']
    sections_by_name: Dict[str, 'ElfLoadedMemorySection']
    symbols: Dict[str, int]
    run_ptr: int

    def __init__(self, name: str):
        self.sections = list()
        self.sections_by_name = dict()
        self.symbols = dict()

        try:
            from elftools.elf.elffile import ELFFile
            from elftools.elf.sections import Section, SymbolTableSection

            with open(name, 'rb') as f:
                print(FMT_ELF + "[ElfLoader] Loading elf executable from: {}".format(name) + FMT_NONE)
                self._read_elf(ELFFile(f))
        except ImportError as e:
            print(FMT_PARSE + "[ElfLoader] Cannot load elf files without PyElfTools package! You can install them using pip install pyelftools!" + FMT_NONE)
            raise e

    def _read_elf(self, elf: 'ELFFile'):
        if not elf.header.e_machine == 'EM_RISCV':
            raise InvalidElfException("Not a RISC-V elf file!")
        if not elf.header.e_ident.EI_CLASS == 'ELFCLASS32':
            raise InvalidElfException("Only 32bit executables are supported!")

        self.run_ptr = elf.header.e_entry

        from elftools.elf.sections import SymbolTableSection
        for sec in elf.iter_sections():
            if isinstance(sec, SymbolTableSection):
                self._parse_symtab(sec)
                continue

            if sec.name not in INCLUDE_SEC:
                continue

            self.add_sec(self._lms_from_elf_sec(sec, 'kernel'))

    def _lms_from_elf_sec(self, sec: 'Section', owner: str):
        is_code = sec.name in ('.text',)
        data = bytearray(sec.data())
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

    def _parse_symtab(self, symtab: 'SymbolTableSection'):
        self.symbols = {
            sym.name: sym.entry.st_value for sym in symtab.iter_symbols() if sym.name
        }

    def add_sec(self, new_sec: 'ElfLoadedMemorySection'):
        for sec in self.sections:
            if sec.base < sec.end <= new_sec.base or sec.end > sec.base >= new_sec.end:
                continue
            else:
                print(FMT_ELF + "[ElfLoader] Invalid elf layout: Two sections overlap: \n\t{}\n\t{}".format(
                    sec, new_sec
                ) + FMT_NONE)
                raise RuntimeError("Cannot load elf with overlapping sections!")

        self.sections.append(new_sec)
        self.sections_by_name[new_sec.name] = new_sec


class InvalidElfException(RiscemuBaseException):
    def __init__(self, msg: str):
        super().__init__()
        self.msg = msg

    def message(self):
        return FMT_PARSE + "{}(\"{}\")".format(self.__class__.__name__, self.msg) + FMT_NONE


@dataclass(frozen=True)
class ElfInstruction:
    name: str
    args: List[int]
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
        # if self.name in ('lw', 'lh', 'lb', 'lbu', 'lhu', 'sw', 'sh', 'sb'):
        #     args = "{}, {}({})".format(
        #         RISCV_REGS[self.args[0]], self.args[2], RISCV_REGS[self.args[1]]
        #     )
        # else:
        #     args = ", ".join(map(str, self.args))
        # return "{:<8} {}".format(
        #     self.name,
        #     args
        # )


class ElfLoadedMemorySection(LoadedMemorySection):
    ins_cache: List[Optional[ElfInstruction]]
    """
    A fast cache for accessing pre-decoded instructions
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.__setattr__('ins_cache', [None] * (self.size // 4))

    def read_instruction(self, offset):
        if self.ins_cache[offset//4] is not None:
            return self.ins_cache[offset//4]
        if not self.flags.executable:
            print(FMT_PARSE + "Reading instruction from non-executable memory!" + FMT_NONE)
            raise InstructionAccessFault(offset + self.base)
        if offset % 4 != 0:
            raise InstructionAddressMisalignedTrap(offset + self.base)
        ins = ElfInstruction(*decode(self.content[offset:offset + 4]))
        self.ins_cache[offset // 4] = ins
        return ins

    @property
    def end(self):
        return self.size + self.base
