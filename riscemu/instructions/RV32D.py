"""
RiscEmu (c) 2023 Anton Lydike

SPDX-License-Identifier: MIT

This file contains copious amounts of docstrings that were all taken
from https://msyksphinz-self.github.io/riscv-isadoc/html/rvfd.html
(all the docstrings on the instruction methods documenting the opcodes
and their function)
"""
from typing import Tuple

from .instruction_set import InstructionSet, Instruction
from .float_base import FloatArithBase
from riscemu.core import INS_NOT_IMPLEMENTED, Float32, Int32, UInt32, Float64


class RV32D(FloatArithBase[Float64]):
    flen = 64
    _float_cls = Float64
