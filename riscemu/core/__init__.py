from typing import Dict, Any
import re

# define some base type aliases so we can keep track of absolute and relative addresses
T_RelativeAddress = int
T_AbsoluteAddress = int

# parser options are just dictionaries with arbitrary values
T_ParserOpts = Dict[str, Any]

NUMBER_SYMBOL_PATTERN = re.compile(r"^\d+[fb]$")

# exceptions
from .exceptions import (
    ParseException,
    NumberFormatException,
    MemoryAccessException,
    OutOfMemoryException,
    LinkerException,
    LaunchDebuggerException,
    RiscemuBaseException,
    InvalidRegisterException,
    InvalidAllocationException,
    InvalidSyscallException,
    UnimplementedInstruction,
    INS_NOT_IMPLEMENTED,
)

# base classes
from .flags import MemoryFlags
from .int32 import UInt32, Int32
from .float import BaseFloat, Float32, Float64
from .rtclock import RTClock
from .instruction import Instruction, Immediate, InstructionWithEncoding
from .instruction_context import InstructionContext
from .memory_section import MemorySection
from .program import Program
from .program_loader import ProgramLoader
from .privmodes import PrivModes
from .mmu import MMU
from .csr import CSR
from .registers import Registers
from .cpu import CPU
from .simple_instruction import SimpleInstruction
from .instruction_memory_section import InstructionMemorySection
from .binary_data_memory_section import BinaryDataMemorySection
from .usermode_cpu import UserModeCPU

__all__ = [
    "T_RelativeAddress",
    "T_AbsoluteAddress",
    "T_ParserOpts",
    "NUMBER_SYMBOL_PATTERN",
    "ParseException",
    "NumberFormatException",
    "MemoryAccessException",
    "OutOfMemoryException",
    "LinkerException",
    "LaunchDebuggerException",
    "RiscemuBaseException",
    "InvalidRegisterException",
    "InvalidAllocationException",
    "InvalidSyscallException",
    "UnimplementedInstruction",
    "INS_NOT_IMPLEMENTED",
    "MemoryFlags",
    "UInt32",
    "Int32",
    "BaseFloat",
    "Float32",
    "Float64",
    "RTClock",
    "Instruction",
    "Immediate",
    "InstructionWithEncoding",
    "InstructionContext",
    "MemorySection",
    "Program",
    "ProgramLoader",
    "PrivModes",
    "MMU",
    "CSR",
    "Registers",
    "CPU",
    "SimpleInstruction",
    "InstructionMemorySection",
    "BinaryDataMemorySection",
    "UserModeCPU",
]
