from abc import ABC, abstractmethod


class IOModule(ABC):
    addr: int
    size: int

    def __init__(self, addr: int, size: int):
        self.addr = addr
        self.size = size

    @abstractmethod
    def read(self, addr: int, size: int):
        pass

    @abstractmethod
    def write(self, addr: int, data: bytearray, size: int):
        pass

    def contains(self, addr, size: int = 0):
        return self.addr <= addr < self.addr + self.size and \
               self.addr <= addr + size <= self.addr + self.size
