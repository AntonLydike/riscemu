from time import time

from . import UInt32


class RTClock:
    """
    Represents a realtime clock. Can be set up to start at a certain time t0, and
    has a certain tickrate.
    """

    tickrate: int
    t0: float

    def __init__(self, tickrate: int, t0: float | None = None):
        if t0 is None:
            self.t0 = time()
        self.tickrate = tickrate

    def get_low32(self, *args):
        return UInt32(int(time() * self.tickrate))

    def get_hi32(self, *args):
        return UInt32(int(time() * self.tickrate) >> 32)

    def get_as_int(self):
        return time() * self.tickrate
