"""
RiscEmu (c) 2021 Anton Lydike

SPDX-License-Identifier: MIT

This package holds all instruction sets, available to the processor
"""

from .instruction_set import InstructionSet, Instruction
from .RV32M import RV32M
from .RV32I import RV32I
from .RV32A import RV32A
from .RV32F import RV32F
from .RV32D import RV32D
from .RV_Debug import RV_Debug
from .Zicsr import Zicsr

InstructionSetDict = {
    v.__name__: v for v in [RV32I, RV32M, RV32A, RV32F, RV32D, Zicsr, RV_Debug]
}

__all__ = [
    "Instruction",
    "InstructionSet",
    "InstructionSetDict",
    "RV32I",
    "RV32M",
    "RV32A",
    "RV32F",
    "RV32D",
    "Zicsr",
    "RV_Debug",
]
