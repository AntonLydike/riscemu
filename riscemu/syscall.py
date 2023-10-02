"""
RiscEmu (c) 2021 Anton Lydike

SPDX-License-Identifier: MIT
"""

import sys
from dataclasses import dataclass
from math import log2, ceil
from typing import Dict, IO, Union

from .core import (
    BinaryDataMemorySection,
    MemoryFlags,
    Int32,
    CPU,
    InvalidSyscallException,
)
from .colors import FMT_SYSCALL, FMT_NONE

SYSCALLS = {
    63: "read",
    64: "write",
    93: "exit",
    192: "mmap2",
    1024: "open",
    1025: "close",
}
"""
This dict contains a mapping for all available syscalls (code->name)

If you wish to add a syscall to the built-in system, you can extend this
dictionary and implement a method with the same name on the SyscallInterface
class.
"""

ADDITIONAL_SYMBOLS = {
    "MAP_PRIVATE": 1 << 0,
    "MAP_SHARED": 1 << 1,
    "MAP_ANON": 1 << 2,
    "MAP_ANONYMOUS": 1 << 2,
    "PROT_READ": 1 << 0,
    "PROT_WRITE": 1 << 1,
}
"""
A set of additional symbols that are used by various syscalls.
"""

OPEN_MODES = {
    0: "rb",
    1: "wb",
    2: "r+b",
    3: "x",
    4: "ab",
}
"""All available file open modes"""


@dataclass(frozen=True)
class Syscall:
    """
    Represents a syscall
    """

    id: int
    """The syscall number (e.g. 64 - write)"""
    cpu: CPU
    """The CPU object that created the syscall"""

    @property
    def name(self):
        return SYSCALLS.get(self.id, "unknown")

    def __repr__(self):
        return "Syscall(id={}, name={})".format(self.id, self.name)

    def ret(self, code: Union[int, Int32]):
        self.cpu.regs.set("a0", Int32(code))


def get_syscall_symbols():
    """
    Generate global syscall symbols (such as SCALL_READ, SCALL_EXIT etc)

    :return: dictionary of all syscall symbols (SCALL_<name> -> id)
    """
    items: Dict[str, int] = {
        ("SCALL_" + name.upper()): num for num, name in SYSCALLS.items()
    }

    items.update(ADDITIONAL_SYMBOLS)

    return items


class SyscallInterface:
    """
    Handles syscalls
    """

    open_files: Dict[int, IO]
    next_open_handle: int

    def handle_syscall(self, scall: Syscall):
        self.next_open_handle = 3
        self.open_files = {0: sys.stdin, 1: sys.stdout, 2: sys.stderr}

        if getattr(self, scall.name):
            getattr(self, scall.name)(scall)
        else:
            raise InvalidSyscallException(scall)

    def read(self, scall: Syscall):
        """
        read syscall (63): read from file no a0, into addr a1, at most a2 bytes
        on return a0 will be the number of read bytes or -1 if an error occurred
        """
        fileno = scall.cpu.regs.get("a0").unsigned_value
        addr = scall.cpu.regs.get("a1").unsigned_value
        size = scall.cpu.regs.get("a2").unsigned_value
        if fileno not in self.open_files:
            scall.ret(-1)
            return

        chars = self.open_files[fileno].readline(size)
        try:
            data = bytearray(chars, "ascii")
            scall.cpu.mmu.write(addr, len(data), data)
            return scall.ret(len(data))

        except UnicodeEncodeError:
            print(
                FMT_SYSCALL
                + '[Syscall] read: UnicodeError - invalid input "{}"'.format(chars)
                + FMT_NONE
            )
            return scall.ret(-1)

    def write(self, scall: Syscall):
        """
        write syscall (64): write a2 bytes from addr a1 into fileno a0
        on return a0 will hold the number of bytes written or -1 if an error occurred
        """
        fileno = scall.cpu.regs.get("a0").unsigned_value
        addr = scall.cpu.regs.get("a1").unsigned_value
        size = scall.cpu.regs.get("a2").unsigned_value
        if fileno not in self.open_files:
            return scall.ret(-1)

        data = scall.cpu.mmu.read(addr, size)

        if not isinstance(data, bytearray):
            print(
                FMT_SYSCALL
                + "[Syscall] write: writing from .text region not supported."
                + FMT_NONE
            )
            return scall.ret(-1)

        self.open_files[fileno].write(data.decode("ascii"))
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
        # FIXME: this should be toggleable in a global setting or something
        if True:
            print(
                FMT_SYSCALL
                + "[Syscall] open: opening files not supported without scall-fs flag!"
                + FMT_NONE
            )
            return scall.ret(-1)

        mode = scall.cpu.regs.get("a0").unsigned_value
        addr = scall.cpu.regs.get("a1").unsigned_value
        size = scall.cpu.regs.get("a2").unsigned_value

        mode_st = OPEN_MODES.get(
            mode,
        )
        if mode_st == -1:
            print(
                FMT_SYSCALL
                + "[Syscall] open: unknown opening mode {}!".format(mode)
                + FMT_NONE
            )
            return scall.ret(-1)

        path = scall.cpu.mmu.read(addr, size).decode("ascii")

        fileno = self.next_open_handle
        self.next_open_handle += 1

        try:
            self.open_files[fileno] = open(path, mode_st)
        except OSError as err:
            print(
                FMT_SYSCALL
                + "[Syscall] open: encountered error during {}!".format(err.strerror)
                + FMT_NONE
            )
            return scall.ret(-1)

        print(
            FMT_SYSCALL
            + "[Syscall] open: opened fd {} to {}!".format(fileno, path)
            + FMT_NONE
        )
        return scall.ret(fileno)

    def close(self, scall: Syscall):
        """
        close syscall (1025): closes file no a0

        return -1 if an error was encountered, otherwise returns 0
        """
        fileno = scall.cpu.regs.get("a0").unsigned_value
        if fileno not in self.open_files:
            print(
                FMT_SYSCALL
                + "[Syscall] close: unknown fileno {}!".format(fileno)
                + FMT_NONE
            )
            return scall.ret(-1)

        self.open_files[fileno].close()
        print(FMT_SYSCALL + "[Syscall] close: closed fd {}!".format(fileno) + FMT_NONE)
        del self.open_files[fileno]
        return scall.ret(0)

    def exit(self, scall: Syscall):
        """
        Exit syscall. Exits the system with status code a0
        """
        scall.cpu.halted = True
        scall.cpu.exit_code = scall.cpu.regs.get("a0").signed().value

    def mmap2(self, scall: Syscall):
        """
        mmap2 syscall:

        void *mmap(void *addr, size_t length, int prot, int flags,
                  int fd, off_t offset);

        Only supported modes:
        addr  = <any>
        prot  = either PROT_READ or PROT_READ | PROT_WRITE
        flags = MAP_PRIVATE | MAP_ANONYMOUS
        fd    = <ignored>
        off_t = <ignored>
        """
        addr = scall.cpu.regs.get("a0").unsigned_value
        size = scall.cpu.regs.get("a1").unsigned_value
        prot = scall.cpu.regs.get("a2").unsigned_value
        flags = scall.cpu.regs.get("a3").unsigned_value

        # error out if prot is not 1 or 3:
        # 1 = PROT_READ
        # 3 = PROT_READ | PROT_WRITE
        if prot != 1 and prot != 3:
            return scall.ret(-1)

        # round size up to multiple of 4096
        size = 4096 * ceil(size / 4096)
        section = BinaryDataMemorySection(
            bytearray(size),
            ".data.runtime-allocated",
            None,
            "system",
            base=addr,
            flags=MemoryFlags(read_only=prot != 3, executable=False),
        )

        # try to insert section
        if scall.cpu.mmu.load_section(section, addr != 0):
            return scall.ret(section.base)
        # if that failed, and we tried to force an address,
        # try again at any address
        elif addr != 0:
            section.base = 0
            if scall.cpu.mmu.load_section(section):
                return scall.ret(section.base)
        # if that didn't work, return error
        return scall.ret(-1)

    def __repr__(self):
        return "{}(\n\tfiles={}\n)".format(self.__class__.__name__, self.open_files)
