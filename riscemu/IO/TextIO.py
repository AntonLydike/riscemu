from .IOModule import IOModule
from ..priv.Exceptions import InstructionAccessFault
from ..types import T_RelativeAddress, Instruction, MemoryFlags, Int32


class TextIO(IOModule):
    def read_ins(self, offset: T_RelativeAddress) -> Instruction:
        raise InstructionAccessFault(self.base + offset)

    def __init__(self, base: int, buflen: int = 128):
        super(TextIO, self).__init__('TextIO', MemoryFlags(False, False), buflen + 4, base=base)
        self.buff = bytearray(buflen)
        self.current_line = ""

    def read(self, addr: int, size: int) -> bytearray:
        raise InstructionAccessFault(self.base + addr)

    def write(self, addr: int, size: int, data: bytearray):
        if addr == 0:
            if size > 4:
                raise InstructionAccessFault(addr)
            if Int32(data) != 0:
                self._print()
                return
        buff_start = addr - 4
        self.buff[buff_start:buff_start + size] = data[0:size]

    def _print(self):
        buff = self.buff
        self.buff = bytearray(self.size)
        if b'\x00' in buff:
            buff = buff.split(b'\x00')[0]
        text = buff.decode('ascii')
        if '\n' in text:
            lines = text.split("\n")
            lines[0] = self.current_line + lines[0]
            for line in lines[:-1]:
                self._present(line)
            self.current_line = lines[-1]
        else:
            self.current_line += text

    def _present(self, text: str):
        print("[TextIO:{:x}] {}".format(self.base, text))
