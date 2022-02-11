"""
RiscEmu (c) 2021 Anton Lydike

SPDX-License-Identifier: MIT

This package holds all instruction sets, available to the processor
"""

from .instruction_set import InstructionSet
from .RV32M import RV32M
from .RV32I import RV32I
from .RV32A import RV32A

InstructionSetDict = {
    v.__name__: v for v in [RV32I, RV32M, RV32A]
}
