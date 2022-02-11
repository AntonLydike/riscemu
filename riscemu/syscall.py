"""
RiscEmu (c) 2021 Anton Lydike

SPDX-License-Identifier: MIT
"""

import sys
from dataclasses import dataclass
from typing import Dict, IO

from .helpers import *

if typing.TYPE_CHECKING:
    from riscemu.CPU import UserModeCPU

SYSCALLS = {
    63: 'read',
    64: 'write',
    93: 'exit',
    1024: 'open',
    1025: 'close',
}
"""All available syscalls (mapped id->name)"""

OPEN_MODES = {
    0: 'rb',
    1: 'wb',
    2: 'r+b',
    3: 'x',
    4: 'ab',
}
"""All available file open modes"""


@dataclass(frozen=True)
class Syscall:
    """
    Represents a syscall
    """
    id: int
    """The syscall number (e.g. 64 - write)"""
    cpu: 'UserModeCPU'
    """The CPU object that created the syscall"""

    @property
    def name(self):
        return SYSCALLS.get(self.id, "unknown")

    def __repr__(self):
        return "Syscall(id={}, name={})".format(
            self.id, self.name
        )

    def ret(self, code):
        self.cpu.regs.set('a0', code)


def get_syscall_symbols():
    """
    Generate global syscall symbols (such as SCALL_READ, SCALL_EXIT etc)

    :return: dictionary of all syscall symbols (SCALL_<name> -> id)
    """
    return {
        ('SCALL_' + name.upper()): num for num, name in SYSCALLS.items()
    }


class SyscallInterface:
    """
    Handles syscalls
    """
    open_files: Dict[int, IO]
    next_open_handle: int

    def handle_syscall(self, scall: Syscall):
        self.next_open_handle = 3
        self.open_files = {
            0: sys.stdin,
            1: sys.stdout,
            2: sys.stderr
        }

        if getattr(self, scall.name):
            getattr(self, scall.name)(scall)
        else:
            raise InvalidSyscallException(scall)

    def read(self, scall: Syscall):
        """
        read syscall (63): read from file no a0, into addr a1, at most a2 bytes
        on return a0 will be the number of read bytes or -1 if an error occured
        """
        fileno = scall.cpu.regs.get('a0')
        addr = scall.cpu.regs.get('a1')
        size = scall.cpu.regs.get('a2')
        if fileno not in self.open_files:
            scall.cpu.regs.set('a0', -1)
            return

        chars = self.open_files[fileno].readline(size)
        try:
            data = bytearray(chars, 'ascii')
            scall.cpu.mmu.write(addr, len(data), data)
            return scall.ret(len(data))

        except UnicodeEncodeError:
            print(FMT_SYSCALL + '[Syscall] read: UnicodeError - invalid input "{}"'.format(chars) + FMT_NONE)
            return scall.ret(-1)

    def write(self, scall: Syscall):
        """
        write syscall (64): write a2 bytes from addr a1 into fileno a0
        on return a0 will hold the number of bytes written or -1 if an error occured
        """
        fileno = scall.cpu.regs.get('a0')
        addr = scall.cpu.regs.get('a1')
        size = scall.cpu.regs.get('a2')
        if fileno not in self.open_files:
            return scall.ret(-1)

        data = scall.cpu.mmu.read(addr, size)

        if not isinstance(data, bytearray):
            print(FMT_SYSCALL + '[Syscall] write: writing from .text region not supported.' + FMT_NONE)
            return scall.ret(-1)

        self.open_files[fileno].write(data.decode('ascii'))
        return scall.ret(size)

    def open(self, scall: Syscall):
        """
        open syscall (1024): read path of a2 bytes from addr a1, in mode a0
        returns the file no in a0

        modes:
            - 0: read
            - 1: write (truncate)
            - 2: read/write (no truncate)
            - 3: only create
            - 4: append

        Requires running with flag scall-fs
        """
        # FIXME: this should be toggleable in a global setting or somethign
        if True:
            print(FMT_SYSCALL + '[Syscall] open: opening files not supported without scall-fs flag!' + FMT_NONE)
            return scall.ret(-1)

        mode = scall.cpu.regs.get('a0')
        addr = scall.cpu.regs.get('a1')
        size = scall.cpu.regs.get('a2')

        mode_st = OPEN_MODES.get(mode, )
        if mode_st == -1:
            print(FMT_SYSCALL + '[Syscall] open: unknown opening mode {}!'.format(mode) + FMT_NONE)
            return scall.ret(-1)

        path = scall.cpu.mmu.read(addr, size).decode('ascii')

        fileno = self.next_open_handle
        self.next_open_handle += 1

        try:
            self.open_files[fileno] = open(path, mode_st)
        except OSError as err:
            print(FMT_SYSCALL + '[Syscall] open: encountered error during {}!'.format(err.strerror) + FMT_NONE)
            return scall.ret(-1)

        print(FMT_SYSCALL + '[Syscall] open: opened fd {} to {}!'.format(fileno, path) + FMT_NONE)
        return scall.ret(fileno)

    def close(self, scall: Syscall):
        """
        close syscall (1025): closes file no a0

        return -1 if an error was encountered, otherwise returns 0
        """
        fileno = scall.cpu.regs.get('a0')
        if fileno not in self.open_files:
            print(FMT_SYSCALL + '[Syscall] close: unknown fileno {}!'.format(fileno) + FMT_NONE)
            return scall.ret(-1)

        self.open_files[fileno].close()
        print(FMT_SYSCALL + '[Syscall] close: closed fd {}!'.format(fileno) + FMT_NONE)
        del self.open_files[fileno]
        return scall.ret(0)

    def exit(self, scall: Syscall):
        """
        Exit syscall. Exits the system with status code a0
        """
        scall.cpu.halted = True
        scall.cpu.exit_code = scall.cpu.regs.get('a0')

    def __repr__(self):
        return "{}(\n\tfiles={}\n)".format(
            self.__class__.__name__,
            self.open_files
        )
