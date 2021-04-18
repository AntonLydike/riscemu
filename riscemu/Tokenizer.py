import re
from enum import IntEnum
from typing import List

from .CPU import CPU, Registers

REGISTERS = list(Registers.all_registers())

INSTRUCTIONS = list(CPU.all_instructions())

PSEUDO_OPS = [
    '.asciiz',
    '.double',
    '.extern',
    '.global',
    '.align',
    '.float',
    '.kdata',
    '.ktext',
    '.space',
    '.ascii',
    '.byte',
    '.data',
    '.half',
    '.text',
    '.word'
    '.set',
]

COMMENT_START = ["#", ";"]

REG_VALID_SYMBOL_LABEL = re.compile(r'^([A-z_.][A-z_0-9.]*[A-z_0-9]|[A-z_]):')

REG_WHITESPACE_UNTIL_NEWLINE = re.compile(r'^(\s*)\n')

REG_WHITESPACE = re.compile(r'^\s*')

REG_NONWHITESPACE = re.compile(r'^[^\s]*')

REG_UNTIL_NEWLINE = re.compile(r'^[^\n]*')

REG_WHITESPACE_NO_LINEBREAK = re.compile(r'^[ \t]*')

REG_VALID_ARGUMENT = re.compile(
    r'^([+-]?(0x[0-9A-f]+|[0-9]+)|[A-z_.][A-z0-9_.]*[A-z_0-9]|[A-z_])(\(([A-z_.][A-z_0-9.]*[A-z_0-9]|[A-z_])\))?'
)

REG_ARG_SPLIT = re.compile(r'^,[ \t]*')


def split_accepting_quotes(string, at=REG_ARG_SPLIT, quotes=('"', "'")):
    pos = 0
    last_piece = 0
    pieces = []
    in_quotes = False
    if string is None:
        return pieces
    while pos < len(string):
        match = at.match(string[pos:])
        if match is not None:
            if not in_quotes:
                pieces.append(string[last_piece:pos])
                pos += len(match.group(0))
                last_piece = pos
            else:
                pos += len(match.group(0))
        elif string[pos] in quotes:
            in_quotes = not in_quotes
            pos += 1
        elif string[pos] in COMMENT_START and not in_quotes:  # entering comment
            break
        else:
            pos += 1
    if in_quotes:
        print("[Tokenizer.split] unbalanced quotes in \"{}\"!".format(string))
    pieces.append(string[last_piece:pos])
    return pieces


class RiscVInput:
    def __init__(self, content: str, name: str):
        self.content = content
        self.pos = 0
        self.len = len(content)
        self.name = name

    @staticmethod
    def from_file(src: str):
        with open(src, 'r') as f:
            return RiscVInput(f.read(), src)

    def peek(self, offset: int = 0, size: int = 1, regex: re.Pattern = None, text: str = None, regex_group: int = 0):
        at = self.pos + offset

        if regex:
            if not isinstance(regex, re.Pattern):
                print("uncompiled regex passed to peek!")
                regex = re.compile(regex)
            match = regex.match(self.content[at:])
            if match is None:
                return None

            if regex_group != 0 and not match.group(0).startswith(match.group(regex_group)):
                print("Cannot peek regex group that does not start at match start!")
                return None
            return match.group(regex_group)
        if text:
            if self.content[at:].startswith(text):
                return self.content[at:at + len(text)]
            return False
        return self.content[at:at + size]

    def peek_one_of(self, options: List[str]):
        longest_peek = 0
        ret = False
        for text in options:
            if self.peek(text=text):
                if len(text) > longest_peek:
                    longest_peek = len(text)
                    ret = text
        return ret

    def consume(self, size: int = 1, regex: re.Pattern = None, text: str = None, regex_group: int = 0):
        at = self.pos

        if regex:
            if not isinstance(regex, re.Pattern):
                print("uncompiled regex passed to peek!")
                regex = re.compile(regex)
            match = regex.match(self.content[at:])
            if match is None:
                print("Regex matched none at {}!".format(self.context()))
                return None

            if regex_group != 0 and not match.group(0).startswith(match.group(regex_group)):
                print("Cannot consume regex group that does not start at match start!")
                return None
            self.pos += len(match.group(regex_group))
            return match.group(regex_group)

        if text:
            if self.content[at:].startswith(text):
                self.pos += len(text)
                return text
            return None

        self.pos += size
        return self.content[at:at + size]

    def consume_one_of(self, options: List[str]):
        longest_peek = 0
        ret = False
        for text in options:
            if self.peek(text=text):
                if len(text) > longest_peek:
                    longest_peek = len(text)
                    ret = text
        self.consume(text=ret)
        return ret

    def seek_newline(self):
        return self.consume(regex=REG_WHITESPACE_UNTIL_NEWLINE, regex_group=1)

    def consume_whitespace(self, linebreak=True):
        if linebreak:
            return self.consume(regex=REG_WHITESPACE)
        return self.consume(regex=REG_WHITESPACE_NO_LINEBREAK)

    def has_next(self):
        return self.pos < self.len

    def context(self, size: int = 5):
        """
        returns a context string:
        <local input before pos>|<local input after pos>
        """
        start = max(self.pos - size, 0)
        end = min(self.pos + size, self.len - 1)

        return self.content[start:self.pos] + '|' + self.content[self.pos:end]


class TokenType(IntEnum):
    SYMBOL = 0
    INSTRUCTION = 1
    PSEUDO_OP = 2

    def __repr__(self):
        return self.name

    def __str__(self):
        return self.name


class RiscVToken:
    type: TokenType

    def __init__(self, t_type: TokenType):
        self.type = t_type

    def __repr__(self):
        return "{}[{}]({})".format(self.__class__.__name__, self.type, self.text())

    def text(self):
        """
        create text representation of instruction
        """
        return "unknown"


class RiscVInstructionToken(RiscVToken):
    def __init__(self, name, args):
        super().__init__(TokenType.INSTRUCTION)
        self.instruction = name
        self.args = args

    def text(self):
        if len(self.args) == 0:
            return self.instruction
        if len(self.args) == 1:
            return "{} {}".format(self.instruction, self.args[0])
        if len(self.args) == 2:
            return "{} {}, {}".format(self.instruction, *self.args)
        return "{} {}, {}, {}".format(self.instruction, *self.args)


class RiscVSymbolToken(RiscVToken):
    def __init__(self, name):
        super().__init__(TokenType.SYMBOL)
        self.name = name

    def text(self):
        return self.name


class RiscVPseudoOpToken(RiscVToken):
    def __init__(self, name, args):
        super().__init__(TokenType.PSEUDO_OP)
        self.name = name
        self.args = args

    def text(self):
        return "{} {}".format(self.name, self.args)


class RiscVTokenizer:
    def __init__(self, input: RiscVInput):
        self.input = input
        self.tokens: List[RiscVToken] = []
        self.name = input.name

    def tokenize(self):
        while self.input.has_next():
            # remove leading whitespaces, place cursor at text start
            self.input.consume_whitespace()

            # check if we have a pseudo op
            if self.input.peek_one_of(PSEUDO_OPS):
                self.parse_pseudo_op()

            # check if we have a symbol (like main:)
            elif self.input.peek(regex=REG_VALID_SYMBOL_LABEL):
                self.parse_symbol()

            # comment
            elif self.input.peek() in COMMENT_START:
                self.parse_comment()

            # must be instruction
            elif self.input.peek_one_of(INSTRUCTIONS):
                self.parse_instruction()
            else:
                token = self.input.peek(size=5)
                print("Unknown token around {} at: {}".format(repr(token), repr(self.input.context())))
                self.input.consume_whitespace()
                print("After whitespace at: {}".format(repr(self.input.context())))
            self.input.consume_whitespace()

    def parse_pseudo_op(self):
        name = self.input.consume_one_of(PSEUDO_OPS)
        self.input.consume_whitespace(linebreak=False)

        arg_str = self.input.consume(regex=REG_UNTIL_NEWLINE)
        if not arg_str:
            args = []
        else:
            args = split_accepting_quotes(arg_str)

        self.tokens.append(RiscVPseudoOpToken(name[1:], args))

    def parse_symbol(self):
        name = self.input.consume(regex=REG_VALID_SYMBOL_LABEL)
        self.tokens.append(RiscVSymbolToken(name[:-1]))
        if not self.input.consume_whitespace():
            print("[Tokenizer] symbol declaration should always be followed by whitespace (at {})!".format(
                self.input.context()))

    def parse_instruction(self):
        ins = self.input.consume_one_of(INSTRUCTIONS)
        args = []
        self.input.consume_whitespace(linebreak=False)
        while self.input.peek(regex=REG_VALID_ARGUMENT) and len(args) < 3:
            arg = self.input.consume(regex=REG_VALID_ARGUMENT)
            args.append(arg)
            if self.input.peek(text=','):
                self.input.consume(text=',')
                self.input.consume_whitespace(linebreak=False)
            else:
                break
        self.tokens.append(RiscVInstructionToken(ins, args))

    def parse_comment(self):
        # just consume the rest
        self.input.consume(regex=REG_UNTIL_NEWLINE)
