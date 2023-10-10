from typing import Dict, List, Tuple
from riscemu.core import Registers, MMU, BaseFloat

from dataclasses import dataclass

from enum import Enum


class StreamMode(Enum):
    READ = 1
    WRITE = 2
    # READWRITE = 3


@dataclass
class StreamDef:
    base: int = 0
    """
    Base address to read from
    """
    bound: int = 0
    """
    How many elements are in here
    """
    stride: int = 0
    """
    stride = register width
    """
    mode: StreamMode = StreamMode.READ
    """
    Differentiate between read/write
    """
    dim: int = 0
    """
    Supports nested loops
    """
    # internal:
    pos: int = 0
    """
    Next element in stream
    """


class StreamingRegs(Registers):
    mem: MMU
    dm_by_id: List[StreamDef]
    streams: Dict[str, StreamDef]
    enabled: bool

    def __init__(
        self,
        mem: MMU,
        xssr_regs: Tuple[str] = ("ft0", "ft1", "ft2"),
        infinite_regs: bool = False,
    ):
        self.mem = mem
        self.enabled = False
        self.streams = dict()
        self.dm_by_id = []
        for reg in xssr_regs:
            stream_def = StreamDef()
            self.dm_by_id.append(stream_def)
            self.streams[reg] = stream_def
        super().__init__(infinite_regs)

    def get_f(self, reg, mark_read=True) -> "BaseFloat":
        if not self.enabled or reg not in self.streams:
            return super().get_f(reg, mark_read)

        # do the streaming stuff:
        stream = self.streams[reg]
        # TODO: Implement other modes
        assert stream.mode is StreamMode.READ
        # TODO: Check overflow
        # TODO: repetition
        addr = stream.base + (stream.pos * stream.stride)
        val = self.mem.read_float(addr)
        # increment pos
        stream.pos += 1
        return val

    def set_f(self, reg, val: "BaseFloat", mark_set=True) -> bool:
        if not self.enabled or reg not in self.streams:
            return super().set_f(reg, mark_set)

        stream = self.streams[reg]
        assert stream.mode is StreamMode.WRITE

        addr = stream.base + (stream.pos * stream.stride)
        self.mem.write(addr, 4, bytearray(val.bytes))

        stream.pos += 1
        return True
