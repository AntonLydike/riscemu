from typing import Optional, NewType
from enum import Enum
from .privmodes import PrivModes
from .CSRConsts import MCAUSE_TRANSLATION

import typing

from .. import RiscemuBaseException
from ..colors import FMT_PARSE, FMT_NONE
from ..types import UInt32

if typing.TYPE_CHECKING:
    from .ElfLoader import ElfInstruction


class CpuTrapType(Enum):
    TIMER = 1
    SOFTWARE = 2
    EXTERNAL = 3
    EXCEPTION = 4


class CpuTrap(BaseException):
    code: int
    """
    31-bit value encoding the exception code in the mstatus register
    """
    interrupt: int
    """
    The isInterrupt bit in the mstatus register
    """

    mtval: UInt32
    """
    contents of the mtval register
    """

    type: CpuTrapType
    """
    The type (timer, external, software) of the trap
    """

    priv: PrivModes
    """
    The privilege level this trap targets 
    """

    def __init__(self, code: int, mtval, type: CpuTrapType, priv: PrivModes = PrivModes.MACHINE):
        self.interrupt = 0 if type == CpuTrapType.EXCEPTION else 1
        self.code = code
        self.mtval = UInt32(mtval)
        self.priv = priv
        self.type = type

    @property
    def mcause(self):
        return (self.interrupt << 31) + self.code

    def message(self) -> str:
        return ""

    def __repr__(self):
        name = "Reserved interrupt({}, {})".format(self.interrupt, self.code)

        if (self.interrupt, self.code) in MCAUSE_TRANSLATION:
            name = MCAUSE_TRANSLATION[(self.interrupt, self.code)] + "({}, {})".format(self.interrupt, self.code)

        return "{} {{priv={}, type={}, mtval={:x}}} {}".format(
            name, self.priv.name, self.type.name, self.mtval, self.message()
        )

    def __str__(self):
        return self.__repr__()


class IllegalInstructionTrap(CpuTrap):
    def __init__(self, ins: 'ElfInstruction'):
        super().__init__(2, ins.encoded, CpuTrapType.EXCEPTION)


class InstructionAddressMisalignedTrap(CpuTrap):
    def __init__(self, addr: int):
        super().__init__(0, addr, CpuTrapType.EXCEPTION)


class InstructionAccessFault(CpuTrap):
    def __init__(self, addr: int):
        super().__init__(1, addr, CpuTrapType.EXCEPTION)


class TimerInterrupt(CpuTrap):
    def __init__(self):
        super().__init__(7, 0, CpuTrapType.TIMER)


class EcallTrap(CpuTrap):
    def __init__(self, mode: PrivModes):
        super().__init__(mode.value + 8, 0, CpuTrapType.EXCEPTION)


class InvalidElfException(RiscemuBaseException):
    def __init__(self, msg: str):
        super().__init__()
        self.msg = msg

    def message(self):
        return FMT_PARSE + "{}(\"{}\")".format(self.__class__.__name__, self.msg) + FMT_NONE


class LoadAccessFault(CpuTrap):
    def __init__(self, msg, addr, size, op):
        super(LoadAccessFault, self).__init__(5, addr, CpuTrapType.EXCEPTION)
        self.msg = msg
        self.addr = addr
        self.size = size
        self.op = op

    def message(self):
        return "(During {} at 0x{:08x} of size {}: {})".format(
            self.op,
            self.addr,
            self.size,
            self.msg
        )
