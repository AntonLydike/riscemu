from dataclasses import dataclass
from typing import Optional


@dataclass(frozen=True, init=True)
class RunConfig:
    color: bool = True
    preffered_stack_size: Optional[int] = None
    debug_instruction: bool = True
    # allowed syscalls
    scall_input: bool = True
    scall_fs: bool = False

