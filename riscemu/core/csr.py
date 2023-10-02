from collections import defaultdict

from typing import Dict, Callable, Optional, Union
from . import UInt32, PrivModes, csr_constants
from .traps import InstructionAccessFault

from ..colors import FMT_ERROR, FMT_NONE


def _invalid_setter(addr: int, old_val: UInt32, new_val: UInt32):
    print(FMT_ERROR + f"Cannot write csr 0x{addr:03X}" + FMT_NONE)
    raise InstructionAccessFault(addr)


def _invalid_getter(addr: int, curr_val: UInt32) -> UInt32:
    print(FMT_ERROR + f"Cannot read csr 0x{addr:03X}" + FMT_NONE)
    raise InstructionAccessFault(addr)


class MStatusRegister:
    """
    helper for the mstatus register
    """

    state: UInt32

    def __init__(self):
        self.state = UInt32()

    @property
    def uie(self) -> UInt32:
        return (self.state & (1 << 0)) >> 0

    @uie.setter
    def uie(self, new_val: UInt32):
        new_val = new_val ^ self.uie
        self.state = self.state ^ (new_val << 0)

    @property
    def sie(self) -> UInt32:
        return (self.state & (1 << 1)) >> 1

    @sie.setter
    def sie(self, new_val: UInt32):
        new_val = new_val ^ self.sie
        self.state = self.state ^ (new_val << 1)

    @property
    def mie(self) -> UInt32:
        return (self.state & (1 << 3)) >> 3

    @mie.setter
    def mie(self, new_val: UInt32):
        new_val = new_val ^ self.mie
        self.state = self.state ^ (new_val << 3)

    @property
    def upie(self) -> UInt32:
        return (self.state & (1 << 4)) >> 4

    @upie.setter
    def upie(self, new_val: UInt32):
        new_val = new_val ^ self.upie
        self.state = self.state ^ (new_val << 4)

    @property
    def spie(self) -> UInt32:
        return (self.state & (1 << 5)) >> 5

    @spie.setter
    def spie(self, new_val: UInt32):
        new_val = new_val ^ self.spie
        self.state = self.state ^ (new_val << 5)

    @property
    def mpie(self) -> UInt32:
        return (self.state & (1 << 7)) >> 7

    @mpie.setter
    def mpie(self, new_val: UInt32):
        new_val = new_val ^ self.mpie
        self.state = self.state ^ (new_val << 7)

    @property
    def spp(self) -> UInt32:
        return (self.state & (1 << 8)) >> 8

    @spp.setter
    def spp(self, new_val: UInt32):
        new_val = new_val ^ self.spp
        self.state = self.state ^ (new_val << 8)

    @property
    def mpp(self) -> UInt32:
        # bitwidth = 2
        return (self.state & (0b11 << 11)) >> 11

    @mpp.setter
    def mpp(self, new_val: UInt32):
        new_val = new_val ^ self.mpp
        self.state = self.state ^ (new_val << 11)

    @property
    def fs(self) -> UInt32:
        # bitwidth = 2
        return (self.state & (0b11 << 13)) >> 13

    @fs.setter
    def fs(self, new_val: UInt32):
        new_val = new_val ^ self.fs
        self.state = self.state ^ (new_val << 13)

    @property
    def xs(self) -> UInt32:
        # bitwidth = 2
        return (self.state & (0b11 << 15)) >> 15

    @xs.setter
    def xs(self, new_val: UInt32):
        new_val = new_val ^ self.xs
        self.state = self.state ^ (new_val << 15)

    @property
    def mpriv(self) -> UInt32:
        return (self.state & (1 << 17)) >> 17

    @mpriv.setter
    def mpriv(self, new_val: UInt32):
        new_val = new_val ^ self.mpriv
        self.state = self.state ^ (new_val << 17)

    @property
    def sum(self) -> UInt32:
        return (self.state & (1 << 18)) >> 18

    @sum.setter
    def sum(self, new_val: UInt32):
        new_val = new_val ^ self.sum
        self.state = self.state ^ (new_val << 18)

    @property
    def mxr(self) -> UInt32:
        return (self.state & (1 << 19)) >> 19

    @mxr.setter
    def mxr(self, new_val: UInt32):
        new_val = new_val ^ self.mxr
        self.state = self.state ^ (new_val << 19)

    @property
    def tvm(self) -> UInt32:
        return (self.state & (1 << 20)) >> 20

    @tvm.setter
    def tvm(self, new_val: UInt32):
        new_val = new_val ^ self.tvm
        self.state = self.state ^ (new_val << 20)

    @property
    def tw(self) -> UInt32:
        return (self.state & (1 << 21)) >> 21

    @tw.setter
    def tw(self, new_val: UInt32):
        new_val = new_val ^ self.tw
        self.state = self.state ^ (new_val << 21)

    @property
    def tsr(self) -> UInt32:
        return (self.state & (1 << 22)) >> 22

    @tsr.setter
    def tsr(self, new_val: UInt32):
        new_val = new_val ^ self.tsr
        self.state = self.state ^ (new_val << 22)

    @property
    def sd(self) -> UInt32:
        return (self.state & (1 << 31)) >> 31

    @sd.setter
    def sd(self, new_val: UInt32):
        new_val = new_val ^ self.sd
        self.state = self.state ^ (new_val << 31)


class CSR:
    """
    Represents a processors control and status registers
    """

    state: Dict[int, UInt32]

    setters: Dict[int, Callable[[int, UInt32, UInt32], UInt32]]
    getters: Dict[int, Callable[[int, UInt32], UInt32]]

    mstatus: MStatusRegister

    def __init__(self):
        self.state = defaultdict(UInt32)
        self.mstatus = MStatusRegister()
        # wire mstatus state up to our csr state
        self.state[CSR.name_to_addr("mstatus")] = self.mstatus.state

        self.getters = dict()
        self.setters = dict()

    def get(self, addr: int) -> UInt32:
        if addr in self.getters:
            return self.getters[addr](addr, self.state[addr])
        return self.state[addr]

    def set(self, addr: int, val: UInt32):
        if addr in self.setters:
            self.state[addr] = self.setters[addr](addr, self.state[addr], val)
        else:
            self.state[addr] = val

    def register_callback(
        self,
        addr: int,
        *,
        getter: Optional[Callable[[int, UInt32], UInt32]] = None,
        setter: Optional[Callable[[int, UInt32, UInt32], UInt32]] = None,
    ):
        """
        addr: the CSR address
        getter: a function mapping (addr, old_val_in_store) -> actual value
        setter: a function mapping (addr, old_val_in_store, given_val) -> new_val_in_store

        where the _in_store values denote the values in the CSR store.
        Values may be handled by external stores, if that's the case
        these arguments can be safely ignored.
        """
        if getter is None:
            getter = _invalid_getter
        self.getters[addr] = getter
        if setter is None:
            setter = _invalid_setter
        self.setters[addr] = setter

    @staticmethod
    def assert_can_read(mode: PrivModes, addr: int):
        if (addr >> 8) & 3 > mode.value:
            raise InstructionAccessFault(addr)

    @staticmethod
    def assert_can_write(mode: PrivModes, addr: int):
        if (addr >> 8) & 3 > mode.value or addr >> 10 == 0b11:
            raise InstructionAccessFault(addr)

    @staticmethod
    def name_to_addr(addr: Union[str, int]) -> Optional[int]:
        if isinstance(addr, str):
            if addr not in csr_constants.CSR_NAME_TO_ADDR:
                print("Unknown CSR register {}".format(addr))
                return None
            return csr_constants.CSR_NAME_TO_ADDR[addr]
        return addr
