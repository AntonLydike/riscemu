from typing import Optional


class CpuTrap(BaseException):
    code: int
    interrupt: int
    mtval: int

    def __init__(self, interrupt: int, code: int, mtval=0):
        assert 0 <= interrupt <= 1

        self.interrupt = interrupt
        self.code = code
        self.mtval = mtval

    @property
    def mcause(self):
        return (self.code << 31) + self.interrupt


class IllegalInstructionTrap(CpuTrap):
    def __init__(self):
        super().__init__(0, 2, 0)


class InstructionAddressMisalignedTrap(CpuTrap):
    def __init__(self, addr: int):
        super().__init__(0, 0, addr)


class InstructionAccessFault(CpuTrap):
    def __init__(self, addr: int):
        super().__init__(0, 1, addr)


