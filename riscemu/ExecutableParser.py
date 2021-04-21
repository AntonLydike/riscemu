from .helpers import parse_numeric_argument, int_to_bytes
from .Executable import Executable, InstructionMemorySection, MemorySection, MemoryFlags
from .Exceptions import *

from .Tokenizer import RiscVTokenizer, RiscVInstructionToken, RiscVSymbolToken, RiscVPseudoOpToken

from typing import Dict, Tuple, List, Optional


class ExecutableParser:
    tokenizer: 'RiscVTokenizer'

    def __init__(self, tokenizer: 'RiscVTokenizer'):
        self.instructions: List[RiscVInstructionToken] = list()
        self.symbols: Dict[str, Tuple[str, int]] = dict()
        self.sections: Dict[str, MemorySection] = dict()
        self.tokenizer = tokenizer
        self.active_section: Optional[str] = None
        self.implicit_sections = False
        self.stack_pref: Optional[int] = None
        self.globals: List[str] = list()

    def parse(self):
        for token in self.tokenizer.tokens:
            if isinstance(token, RiscVInstructionToken):
                self.parse_instruction(token)
            elif isinstance(token, RiscVSymbolToken):
                self.handle_symbol(token)
            elif isinstance(token, RiscVPseudoOpToken):
                self.handle_pseudo_op(token)
        return self.get_execuable()

    def get_execuable(self):
        start_ptr = ('text', 0)
        if '_start' in self.symbols:
            start_ptr = self.symbols['_start']
        elif 'main' in self.symbols:
            start_ptr = self.symbols['main']
        return Executable(start_ptr, self.sections, self.symbols, self.stack_pref, self.globals, self.tokenizer.name)

    def parse_instruction(self, ins: 'RiscVInstructionToken'):
        if self.active_section is None:
            self.op_text()
            self.implicit_sections = True

        ASSERT_EQ(self.active_section, 'text')
        sec = self.curr_sec()
        if isinstance(sec, InstructionMemorySection):
            sec.add_insn(ins)
        else:
            raise ParseException("SHOULD NOT BE REACHED")

    def handle_symbol(self, token: 'RiscVSymbolToken'):
        ASSERT_NOT_IN(token.name, self.symbols)
        sec_pos = self.curr_sec().size
        self.symbols[token.name] = (self.active_section, sec_pos)

    def handle_pseudo_op(self, op: 'RiscVPseudoOpToken'):
        name = 'op_' + op.name
        if hasattr(self, name):
            getattr(self, name)(op)
        else:
            raise ParseException("Unknown pseudo op: {}".format(op), (op,))

    ## Pseudo op implementations:
    def op_section(self, op: 'RiscVPseudoOpToken'):
        ASSERT_LEN(op.args, 1)
        name = op.args[0][1:]
        ASSERT_IN(name, ('data', 'rodata', 'text'))
        getattr(self, 'op_' + name)(op)

    def op_text(self, op: 'RiscVPseudoOpToken' = None):
        self.set_sec('text', MemoryFlags(read_only=True, executable=True), cls=InstructionMemorySection)

    def op_data(self, op: 'RiscVPseudoOpToken' = None):
        self.set_sec('data', MemoryFlags(read_only=False, executable=False))

    def op_rodata(self, op: 'RiscVPseudoOpToken' = None):
        self.set_sec('rodata', MemoryFlags(read_only=True, executable=False))

    def op_space(self, op: 'RiscVPseudoOpToken'):
        ASSERT_IN(self.active_section, ('data', 'rodata'))
        ASSERT_LEN(op.args, 1)
        size = parse_numeric_argument(op.args[0])
        self.curr_sec().add(bytearray(size))

    def op_ascii(self, op: 'RiscVPseudoOpToken'):
        ASSERT_IN(self.active_section, ('data', 'rodata'))
        ASSERT_LEN(op.args, 1)
        str = op.args[0][1:-1].encode('ascii').decode('unicode_escape')
        self.curr_sec().add(bytearray(str, 'ascii'))

    def op_asciiz(self, op: 'RiscVPseudoOpToken'):
        ASSERT_IN(self.active_section, ('data', 'rodata'))
        ASSERT_LEN(op.args, 1)
        str = op.args[0][1:-1].encode('ascii').decode('unicode_escape')
        self.curr_sec().add(bytearray(str + '\0', 'ascii'))

    def op_stack(self, op: 'RiscVPseudoOpToken'):
        ASSERT_LEN(op.args, 1)
        size = parse_numeric_argument(op.args[0])
        self.stack_pref = size

    def op_global(self, op: 'RiscVPseudoOpToken'):
        ASSERT_LEN(op.args, 1)
        name = op.args[0]
        self.globals.append(name)

    def op_set(self, op: 'RiscVPseudoOpToken'):
        ASSERT_LEN(op.args, 2)
        name = op.args[0]
        val = parse_numeric_argument(op.args[1])
        self.symbols[name] = ('_static_', val)

    def op_align(self, op: 'RiscVPseudoOpToken'):
        pass

    def op_word(self, op: 'RiscVPseudoOpToken'):
        ASSERT_LEN(op.args, 1)
        val = parse_numeric_argument(op.args[0])
        self.curr_sec().add(int_to_bytes(val, 4))


    ## Section handler code
    def set_sec(self, name: str, flags: MemoryFlags, cls=MemorySection):
        if name not in self.sections:
            self.sections[name] = cls(name, flags)
        self.active_section = name

    def curr_sec(self):
        return self.sections[self.active_section]
