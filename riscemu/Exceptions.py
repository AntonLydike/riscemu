"""
RiscEmu (c) 2021 Anton Lydike

SPDX-License-Identifier: MIT
"""

import typing

from abc import abstractmethod
from .colors import *

if typing.TYPE_CHECKING:
    from .Executable import LoadedInstruction


class RiscemuBaseException(BaseException):
    @abstractmethod
    def message(self):
        pass


# Parsing exceptions:

class ParseException(RiscemuBaseException):
    def __init__(self, msg, data=None):
        super().__init__()
        self.msg = msg
        self.data = data

    def message(self):
        return FMT_PARSE + "{}(\"{}\", data={})".format(self.__class__.__name__, self.msg, self.data) + FMT_NONE


def ASSERT_EQ(a1, a2):
    if a1 != a2:
        raise ParseException("ASSERTION_FAILED: Expected elements to be equal!", (a1, a2))


def ASSERT_LEN(a1, size):
    if len(a1) != size:
        raise ParseException("ASSERTION_FAILED: Expected {} to be of length {}".format(a1, size), (a1, size))


def ASSERT_NOT_NULL(a1):
    if a1 is None:
        raise ParseException("ASSERTION_FAILED: Expected {} to be non null".format(a1), (a1,))


def ASSERT_NOT_IN(a1, a2):
    if a1 in a2:
        raise ParseException("ASSERTION_FAILED: Expected {} to not be in {}".format(a1, a2), (a1, a2))


def ASSERT_IN(a1, a2):
    if a1 not in a2:
        raise ParseException("ASSERTION_FAILED: Expected {} to not be in {}".format(a1, a2), (a1, a2))


class LinkerException(RiscemuBaseException):
    def __init__(self, msg, data):
        self.msg = msg
        self.data = data

    def message(self):
        return FMT_PARSE + "{}(\"{}\", data={})".format(self.__class__.__name__, self.msg, self.data) + FMT_NONE


# MMU Exceptions

class MemoryAccessException(RiscemuBaseException):
    def __init__(self, msg, addr, size, op):
        super(MemoryAccessException, self).__init__()
        self.msg = msg
        self.addr = addr
        self.size = size
        self.op = op

    def message(self):
        return FMT_MEM + "{}(During {} at 0x{:08x} of size {}: {})".format(
            self.__class__.__name__,
            self.op,
            self.addr,
            self.size,
            self.msg
        ) + FMT_NONE


class OutOfMemoryException(RiscemuBaseException):
    def __init__(self, action):
        self.action = action

    def message(self):
        return FMT_MEM + '{}(Ran out of memory during {})'.format(
            self.__class__.__name__,
            self.action
        ) + FMT_NONE


class InvalidAllocationException(RiscemuBaseException):
    def __init__(self, msg, name, size, flags):
        self.msg = msg
        self.name = name
        self.size = size
        self.flags = flags

    def message(self):
        return FMT_MEM + '{}[{}](name={}, size={}, flags={})'.format(
            self.__class__.__name__,
            self.msg,
            self.name,
            self.size,
            self.flags
        )

# CPU Exceptions


class UnimplementedInstruction(RiscemuBaseException):
    def __init__(self, ins: 'LoadedInstruction'):
        self.ins = ins

    def message(self):
        return FMT_CPU + "{}({})".format(
            self.__class__.__name__,
            repr(self.ins)
        ) + FMT_NONE


class InvalidRegisterException(RiscemuBaseException):
    def __init__(self, reg):
        self.reg = reg

    def message(self):
        return FMT_CPU + "{}(Invalid register {})".format(
            self.__class__.__name__,
            self.reg
        ) + FMT_NONE


class InvalidSyscallException(RiscemuBaseException):
    def __init__(self, scall):
        self.scall = scall

    def message(self):
        return FMT_SYSCALL + "{}(Invalid syscall: {})".format(
            self.__class__.__name__,
            self.scall
        ) + FMT_NONE


def INS_NOT_IMPLEMENTED(ins):
    raise UnimplementedInstruction(ins)


class NumberFormatException(RiscemuBaseException):
    def __init__(self, msg):
        super().__init__()
        self.msg = msg

    def message(self):
        return "{}({})".format(
            self.__class__.__name__,
            self.msg
        )


# this exception is not printed and simply signals that an interactive debugging session is
class LaunchDebuggerException(RiscemuBaseException):
    def message(self):
        return ""
