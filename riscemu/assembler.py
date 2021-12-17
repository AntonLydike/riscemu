from typing import Optional, Tuple, Union
from enum import Enum, auto
from typing import Optional, Tuple, Union

from helpers import parse_numeric_argument
from .base_types import Program, T_RelativeAddress, InstructionContext
from .colors import FMT_PARSE, FMT_NONE
from .exceptions import ParseException
from .helpers import ASSERT_LEN
from .tokenizer import Token
from .types import BinaryDataMemorySection, InstructionMemorySection


INSTRUCTION_SECTION_NAMES = ('.text', '.init', '.fini')


class MemorySectionType(Enum):
    Data = auto()
    Instructions = auto()


class CurrentSection:
    name: str
    data: Union[list, bytearray]
    type: MemorySectionType

    def current_address(self) -> T_RelativeAddress:
        if self.type == MemorySectionType.Data:
            return len(self.data)
        return len(self.data) * 4

    def __repr__(self):
        return "{}(name={},data={},type={})".format(
            self.__class__.__name__, self.name,
            self.data, self.type.name
        )


class ParseContext:
    section: Optional[CurrentSection]
    context: InstructionContext
    program: Program

    def __init__(self, name: str):
        self.program = Program(name)
        self.context = self.program.context
        self.section = None

    def finalize(self) -> Program:
        self.finalize_section()
        return self.program

    def finalize_section(self):
        if self.section is None:
            return
        if self.section.type == MemorySectionType.Data:
            section = BinaryDataMemorySection(self.section.data, self.section.name, self.context)
            self.program.add_section(section)
        elif self.section.type == MemorySectionType.Instructions:
            section = InstructionMemorySection(self.section.data, self.section.name, self.context)
            self.program.add_section(section)

    def __repr__(self):
        return "{}(\n\tsetion={},\n\tprogram={}\n)".format(
            self.__class__.__name__, self.section, self.program
        )


def ASSERT_IN_SECTION_TYPE(context: ParseContext, type: MemorySectionType):
    if context.section is None:
        raise ParseException('Error, expected to be in {} section, but no section is present...'.format(type.name))
    if context.section.type != type:
        raise ParseException(
            'Error, expected to be in {} section, but currently in {}...'.format(type.name, context.section)
        )


def get_section_base_name(section_name: str) -> str:
    return '.' + section_name.split('.')[1]


class AssemblerDirectives:
    """
    This class represents a collection of all assembler directives as documented by
    https://github.com/riscv-non-isa/riscv-asm-manual/blob/master/riscv-asm.md#pseudo-ops

    All class methods prefixed with op_ are directly used as assembler directives.
    """

    @classmethod
    def op_align(cls, token: Token, args: Tuple[str], context: ParseContext):
        ASSERT_LEN(args, 1)
        ASSERT_IN_SECTION_TYPE(context, MemorySectionType.Data)
        align_to = parse_numeric_argument(args[0])
        current_mod = context.section.current_address() % align_to
        if current_mod == 0:
            return
        context.section.data += bytearray(align_to - current_mod)

    @classmethod
    def op_section(cls, token: Token, args: Tuple[str], context: ParseContext):
        ASSERT_LEN(args, 1)
        context.finalize_section()

        if get_section_base_name(args[0]) in INSTRUCTION_SECTION_NAMES:
            context.section.type = MemorySectionType.Instructions
            context.section.data = list()
        else:
            context.section.type = MemorySectionType.Data
            context.section.data = bytearray()
        context.section.name = args[0]

    @classmethod
    def op_globl(cls, token: Token, args: Tuple[str], context: ParseContext):
        ASSERT_LEN(args, 1)
        context.program.global_labels.add(args[0])

    @classmethod
    def op_equ(cls, token: Token, args: Tuple[str], context: ParseContext):
        ASSERT_LEN(args, 2)
        name = args[0]
        value = parse_numeric_argument(args[1])
        context.context.labels[name] = value

    @classmethod
    def op_zero(cls, token: Token, args: Tuple[str], context: ParseContext):
        ASSERT_LEN(args, 1)
        ASSERT_IN_SECTION_TYPE(context, MemorySectionType.Data)
        size = parse_numeric_argument(args[0])
        cls.add_bytes(size, bytearray(size), context)

    @classmethod
    def add_bytes(cls, size: int, content: Union[None, int, bytearray], context: ParseContext):
        ASSERT_IN_SECTION_TYPE(context, MemorySectionType.Data)

        if content is None:
            content = bytearray(size)

    @classmethod
    def add_text(cls, text: str, context: ParseContext, zero_terminate: bool = True):
        encoded_bytes = bytearray(text.encode('ascii'))
        if zero_terminate:
            encoded_bytes += bytearray(1)
        cls.add_bytes(len(encoded_bytes), encoded_bytes, context)

    @classmethod
    def handle_instruction(cls, token: Token, args: Tuple[str], context: ParseContext):
        op = token.value[1:]
        if hasattr(cls, 'op_' + op):
            getattr(cls, 'op_' + op)(token, args, context)
        elif op in ('text', 'data', 'rodata', 'bss', 'sbss'):
            cls.op_section(token, (token.value,), context)
        elif op in ('string', 'asciiz', 'asciz', 'ascii'):
            ASSERT_LEN(args, 1)
            cls.add_text(args[0], context, op == 'ascii')
        elif op in DATA_OP_SIZES:
            size = DATA_OP_SIZES[op]
            for arg in args:
                cls.add_bytes(size, parse_numeric_argument(arg), context)
        else:
            print(FMT_PARSE + "Unknown assembler directive: {} {} in {}".format(token, args, context) + FMT_NONE)


DATA_OP_SIZES = {
    'byte': 1,
    '2byte': 2, 'half': 2, 'short': 2,
    '4byte': 4, 'word': 4, 'long': 4,
    '8byte': 8, 'dword': 8, 'quad': 8,
}
