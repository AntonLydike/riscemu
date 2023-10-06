"""
RiscEmu (c) 2021-2022 Anton Lydike

SPDX-License-Identifier: MIT
"""

from dataclasses import dataclass


@dataclass(frozen=True, init=True)
class RunConfig:
    stack_size: int = 8 * 1024 * 64  # for 8KB stack
    include_scall_symbols: bool = True
    add_accept_imm: bool = False
    # debugging
    debug_instruction: bool = True
    debug_on_exception: bool = True
    # allowed syscalls
    scall_input: bool = True
    scall_fs: bool = False
    verbosity: int = 0
    slowdown: float = 1
    unlimited_registers: bool = False
    flen: int = 64
    # runtime config
    use_libc: bool = False
    ignore_exit_code: bool = False
    # csr stuff:
    # frequency of the real-time clock
    rtclock_tickrate: int = 32768
