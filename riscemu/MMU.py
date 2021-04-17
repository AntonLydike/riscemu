from dataclasses import dataclass

@dataclass(frozen=True)
class MemoryFlags:
    read_only: bool
    executable: bool

class MemoryRegion:
    addr:int
    len:int
    flags: MemoryFlags


class MMU:
    def __init__(self):
