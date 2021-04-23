"""
RiscEmu (c) 2021 Anton Lydike

SPDX-License-Identifier: MIT
"""

from dataclasses import dataclass
from typing import Optional


@dataclass(frozen=True, init=True)
class RunConfig:
    stack_size: int = 0     # 8 * 1024 * 1024 * 8 # for 8MB stack
    include_scall_symbols: bool = True
    add_accept_imm: bool = False
    # debugging
    debug_instruction: bool = True
    debug_on_exception: bool = True
    # allowed syscalls
    scall_input: bool = True
    scall_fs: bool = False

