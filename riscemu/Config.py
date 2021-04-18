from dataclasses import dataclass
from typing import Optional


@dataclass(frozen=True, init=True)
class RunConfig:
    color: bool = True
    preffered_stack_size: Optional[int] = None
    # debugging
    debug_instruction: bool = True
    debug_on_exception = True
    # allowed syscalls
    scall_input: bool = True
    scall_fs: bool = False

