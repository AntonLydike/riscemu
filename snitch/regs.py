from riscemu.registers import Registers
from riscemu.MMU import MMU
from riscemu.types import Int32, UInt32

from dataclasses import dataclass

from enum import Enum


class StreamMode(Enum):
    READ = 1
    #WRITE = 2
    #READWRITE = 3

@dataclass
class StreamDef:
    base: int
    """
    Base address to read from
    """
    size: int
    """
    How many elements are in here
    """
    stride: int
    """
    stride = register width
    """
    mode: StreamMode = StreamMode.READ
    """
    Differentiate between read/write
    """
    repetition: int = 1
    """
    Return same element multiple times
    """
    # internal:
    pos: int = 0
    """
    Next element in stream
    """


class StreamingRegs(Registers):
    mem: MMU

    streams: dict[str, StreamDef]
    enabled: bool

    def __init__(self, mem: MMU, infinite_regs: bool = False):
        self.mem = mem
        self.enabled = False
        self.streams = dict()
        super().__init__(infinite_regs)

    def get(self, reg, mark_read=True) -> 'Int32':
        if not self.enabled or reg not in self.streams:
            return super().get(reg, mark_read)

        # do the streaming stuff:
        stream = self.streams[reg]
        # TODO: Implement other modes
        assert stream.mode is StreamMode.READ
        # TODO: Check overflow
        # TODO: repetition
        assert stream.repetition == 1
        addr = stream.base + (4 * stream.pos * stream.stride)
        val = self.mem.read_int(addr)
        # increment pos
        print("stream: got val {} from addr 0x{:x}, stream {}".format(
            val, addr, stream
        ))
        stream.pos += 1
        return val

    #def set(self, reg, val: 'Int32', mark_set=True) -> bool:
    #    pass


