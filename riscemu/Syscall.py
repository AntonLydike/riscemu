from dataclasses import dataclass
from .Registers import Registers
from .Exceptions import InvalidSyscallException

import typing

if typing.TYPE_CHECKING:
    from . import CPU

SYSCALLS = {
    63: 'read',
    64: 'write',
    93: 'exit'
}


@dataclass(frozen=True)
class Syscall:
    id: int
    registers: Registers
    cpu: 'CPU'

    @property
    def name(self):
        return SYSCALLS.get(self.id, "unknown")

    def __repr__(self):
        return "Syscall(id={}, name={})".format(
            self.id, self.name
        )


class SyscallInterface:
    def handle_syscall(self, scall: Syscall):
        if getattr(self, scall.name):
            getattr(self, scall.name)(scall)
        else:
            raise InvalidSyscallException(scall)

    def read(self, scall: Syscall):
        pass

    def write(self, scall: Syscall):
        pass

    def exit(self, scall: Syscall):
        scall.cpu.exit = True
        scall.cpu.exit_code = scall.registers.get('a0')
