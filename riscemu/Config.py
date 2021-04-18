from dataclasses import dataclass
from typing import Optional


@dataclass(frozen=True, init=True)
class RunConfig:
    preffered_stack_size: Optional[int] = None
    include_scall_symbols: bool = True
    # debugging
    debug_instruction: bool = True
    debug_on_exception: bool = True
    # allowed syscalls
    scall_input: bool = True
    scall_fs: bool = False

