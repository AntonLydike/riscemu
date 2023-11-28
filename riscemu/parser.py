"""
RiscEmu (c) 2021 Anton Lydike

SPDX-License-Identifier: MIT
"""
import re
from io import IOBase
from typing import Dict, Tuple, Iterable, Callable, List, TextIO

from .assembler import MemorySectionType, ParseContext, AssemblerDirectives
from .colors import FMT_PARSE
from .helpers import Peekable
from .tokenizer import Token, TokenType, tokenize
from .core import (
    Program,
    T_ParserOpts,
    ProgramLoader,
    SimpleInstruction,
    ParseException,
)

REG_NAME_CANONICALIZER = {
    "fp": "s0",
    "x0": "zero",
    "x1": "ra",
    "x2": "sp",
    "x3": "gp",
    "x4": "tp",
    "x5": "t0",
    "x6": "t1",
    "x7": "t2",
    "x8": "s0",
    "x9": "s1",
    "x10": "a0",
    "x11": "a1",
    "x12": "a2",
    "x13": "a3",
    "x14": "a4",
    "x15": "a5",
    "x16": "a6",
    "x17": "a7",
    "x18": "s2",
    "x19": "s3",
    "x20": "s4",
    "x21": "s5",
    "x22": "s6",
    "x23": "s7",
    "x24": "s8",
    "x25": "s9",
    "x26": "s10",
    "x27": "s11",
    "x28": "t3",
    "x29": "t4",
    "x30": "t5",
    "x31": "t6",
    "f0": "ft0",
    "f1": "ft1",
    "f2": "ft2",
    "f3": "ft3",
    "f4": "ft4",
    "f5": "ft5",
    "f6": "ft6",
    "f7": "ft7",
    "f8": "fs0",
    "f9": "fs1",
    "f10": "fa0",
    "f11": "fa1",
    "f12": "fa2",
    "f13": "fa3",
    "f14": "fa4",
    "f15": "fa5",
    "f16": "fa6",
    "f17": "fa7",
    "f18": "fs2",
    "f19": "fs3",
    "f20": "fs4",
    "f21": "fs5",
    "f22": "fs6",
    "f23": "fs7",
    "f24": "fs8",
    "f25": "fs9",
    "f26": "fs10",
    "f27": "fs11",
    "f28": "ft8",
    "f29": "ft9",
    "f30": "ft10",
    "f31": "ft11",
}


def parse_instruction(token: Token, args: Tuple[str], context: ParseContext):
    if context.section is None:
        context.new_section(".text", MemorySectionType.Instructions)
    if context.section.type != MemorySectionType.Instructions:
        raise ParseException(
            "{} {} encountered in invalid context: {}".format(token, args, context)
        )
    ins = SimpleInstruction(
        token.value,
        parse_instruction_arguments(args),
        context.context,
        context.current_address(),
    )
    context.section.data.append(ins)


def parse_label(token: Token, args: Tuple[str], context: ParseContext):
    name = token.value[:-1]
    if re.match(r"^\d+$", name):
        # relative label:
        context.context.numbered_labels[name].append(context.current_address())
    else:
        if name in context.context.labels:
            print(FMT_PARSE + "Warn: Symbol {} defined twice!".format(name))
        context.add_label(name, context.current_address(), is_relative=True)


PARSERS: Dict[TokenType, Callable[[Token, Tuple[str], ParseContext], None]] = {
    TokenType.PSEUDO_OP: AssemblerDirectives.handle_instruction,
    TokenType.LABEL: parse_label,
    TokenType.INSTRUCTION_NAME: parse_instruction,
}


def parse_tokens(name: str, tokens_iter: Iterable[Token]) -> Program:
    """
    Convert a token stream into a parsed program
    :param name: the programs name
    :param tokens_iter: the programs content, tokenized
    :return: a parsed program
    """
    context = ParseContext(name)

    for token, args in composite_tokenizer(Peekable[Token](tokens_iter)):
        if token.type not in PARSERS:
            raise ParseException("Unexpected token type: {}, {}".format(token, args))
        PARSERS[token.type](token, args, context)

    return context.finalize()


def composite_tokenizer(
    tokens_iter: Iterable[Token],
) -> Iterable[Tuple[Token, Tuple[str]]]:
    """
    Convert an iterator over tokens into an iterator over tuples: (token, list(token))

    The first token is either a pseudo_op, label, or instruction name. The token list are all remaining tokens before
    a newline is encountered
    :param tokens_iter: An iterator over tokens
    :return: An iterator over a slightly more structured representation of the tokens
    """
    tokens: Peekable[Token] = Peekable[Token](tokens_iter)

    while not tokens.is_empty():
        token = next(tokens)
        if token.type in (
            TokenType.PSEUDO_OP,
            TokenType.LABEL,
            TokenType.INSTRUCTION_NAME,
        ):
            yield token, tuple(take_arguments(tokens))


def take_arguments(tokens: Peekable[Token]) -> Iterable[str]:
    """
    Consumes (argument comma)* and yields argument.value until newline is reached
    If an argument is not followed by either a newline or a comma, a parse exception is raised
    The newline at the end is consumed
    :param tokens: A Peekable iterator over some Tokens
    """
    while True:
        if tokens.peek().type == TokenType.ARGUMENT:
            yield next(tokens).value
        elif tokens.peek().type == TokenType.NEWLINE:
            next(tokens)
            break
        elif tokens.peek().type == TokenType.COMMA:
            next(tokens)
        else:
            break

        # raise ParseException("Expected newline, instead got {}".format(tokens.peek()))


def parse_instruction_arguments(args: Tuple[str]) -> Tuple[str]:
    """
    Parses argument Tuples of instructions. In this process canonicalize register names
    :param args: A tuple of an instructions arguments
    :return: A tuple of an instructions parsed arguments
    """
    return tuple(canonicalize_register_names(args))


def canonicalize_register_names(args: Tuple[str]) -> Iterable[str]:
    """
    Translate register indices names to ABI names. Leaves other arguments unchanged.
    Examples:
    "x0" -> "zero"
    "x5" -> "t0"
    "x8" -> "s0"
    "fp" -> "s0"
    :param args: A tuple of an instructions arguments
    :return: An iterator over the arguments of an instruction, but with canonicalized register names
    """
    for arg in args:
        yield REG_NAME_CANONICALIZER.get(arg, arg)


class AssemblyFileLoader(ProgramLoader):
    """
    This class loads assembly files written by hand. It understands some assembler
    directives and supports most pseudo instructions. It does very little verification
    of source correctness.

    It also supports numbered jump targets and properly supports local and global scope
    (globl assembly directive)


    The AssemblyFileLoader loads .asm and .s files by default, and acts as a weak
    fallback to all other filetypes.
    """

    is_binary = False

    source: TextIO

    def parse(self) -> Program:
        with self.source as f:
            return parse_tokens(self.filename, tokenize(f))

    @classmethod
    def can_parse(cls, source_name: str) -> float:
        """
        Parse a string assembly file.
        It also acts as a weak fallback if no other loaders want to take the file.
        """
        # gcc recognizes these line endings as assembly. So we will do too.
        if source_name == "-" or source_name.split(".")[-1].lower() in ("asm", "s"):
            return 1
        return 0.01

    @classmethod
    def get_options(cls, argv: List[str]) -> Tuple[List[str], T_ParserOpts]:
        return argv, {}
