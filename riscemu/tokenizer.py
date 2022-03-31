"""
RiscEmu (c) 2021 Anton Lydike

SPDX-License-Identifier: MIT
"""

import re
from dataclasses import dataclass
from enum import Enum, auto
from typing import List, Iterable

from riscemu.decoder import RISCV_REGS
from riscemu.types.exceptions import ParseException

LINE_COMMENT_STARTERS = ('#', ';', '//')
WHITESPACE_PATTERN = re.compile(r'\s+')
MEMORY_ADDRESS_PATTERN = re.compile(r'^(0[xX][A-f0-9]+|\d+|0b[0-1]+|[A-z0-9_-]+)\(([A-z]+[0-9]{0,2})\)$')
REGISTER_NAMES = RISCV_REGS


class TokenType(Enum):
    COMMA = auto()
    ARGUMENT = auto()
    PSEUDO_OP = auto()
    INSTRUCTION_NAME = auto()
    NEWLINE = auto()
    LABEL = auto()


@dataclass(frozen=True)
class Token:
    type: TokenType
    value: str

    def __str__(self):
        if self.type == TokenType.NEWLINE:
            return '\\n'
        if self.type == TokenType.COMMA:
            return ', '
        return '{}({})'.format(self.type.name[0:3], self.value)


NEWLINE = Token(TokenType.NEWLINE, '\n')
COMMA = Token(TokenType.COMMA, ',')


def tokenize(input: Iterable[str]) -> Iterable[Token]:
    for line in input:
        for line_comment_start in LINE_COMMENT_STARTERS:
            if line_comment_start in line:
                line = line[:line.index(line_comment_start)]
        line.strip(' \t\n')
        if not line:
            continue

        parts = list(part for part in split_whitespace_respecting_quotes(line) if part)

        yield from parse_line(parts)
        yield NEWLINE


def parse_line(parts: List[str]) -> Iterable[Token]:
    if len(parts) == 0:
        return ()
    first_token = parts[0]

    if first_token[0] == '.':
        yield Token(TokenType.PSEUDO_OP, first_token)
    elif first_token[-1] == ':':
        yield Token(TokenType.LABEL, first_token)
        yield from parse_line(parts[1:])
        return
    else:
        yield Token(TokenType.INSTRUCTION_NAME, first_token)

    for part in parts[1:]:
        if part == ',':
            yield COMMA
            continue
        yield from parse_arg(part)


def parse_arg(arg: str) -> Iterable[Token]:
    comma = arg[-1] == ','
    arg = arg[:-1] if comma else arg
    mem_match_resul = re.match(MEMORY_ADDRESS_PATTERN, arg)
    if mem_match_resul:
        register = mem_match_resul.group(2).lower()
        if register not in RISCV_REGS:
            raise ParseException(f'"{register}" is not a valid register!')
        yield Token(TokenType.ARGUMENT, register)
        yield Token(TokenType.ARGUMENT, mem_match_resul.group(1))
    else:
        yield Token(TokenType.ARGUMENT, arg)
    if comma:
        yield COMMA


def print_tokens(tokens: Iterable[Token]):
    for token in tokens:
        print(token, end='\n' if token == NEWLINE else '')
    print("", flush=True, end="")


def split_whitespace_respecting_quotes(line: str) -> Iterable[str]:
    quote = ""
    part = ""
    for c in line:
        if c == quote:
            yield part
            part = ""
            quote = ""
            continue

        if quote != "":
            part += c
            continue

        if c in "\"'":
            if part:
                yield part
            quote = c
            part = ""
            continue

        if c in ' \t\n':
            if part:
                yield part
            part = ""
            continue

        part += c

    if part:
        yield part
