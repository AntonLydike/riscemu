from typing import Dict, Union, Callable, Optional
from collections import defaultdict
from .privmodes import PrivModes
from .Exceptions import InstructionAccessFault
from ..colors import FMT_CSR, FMT_NONE

from .CSRConsts import CSR_NAME_TO_ADDR, MSTATUS_LEN_2, MSTATUS_OFFSETS
from ..types import UInt32


class CSR:
    """
    This holds all Control and Status Registers (CSR)
    """
    regs: Dict[int, UInt32]
    """
    All Control and Status Registers are stored here
    """

    virtual_regs: Dict[int, Callable[[], UInt32]]
    """
    list of virtual CSR registers, with values computed on read
    """

    listeners: Dict[int, Callable[[UInt32, UInt32], None]]

    mstatus_cache: Dict[str, UInt32]
    mstatus_cache_dirty = True

    def __init__(self):
        self.regs = defaultdict(lambda: UInt32(0))
        self.listeners = defaultdict(lambda: (lambda x, y: None))
        self.virtual_regs = dict()
        self.mstatus_cache = dict()
        # TODO: implement write masks (bitmasks which control writeable bits in registers

    def set(self, addr: Union[str, int], val: Union[int, UInt32]):
        addr = self._name_to_addr(addr)
        if addr is None:
            return
        val = UInt32(val)
        self.listeners[addr](self.regs[addr], val)
        if addr == 0x300:
            self.mstatus_cache_dirty = True
        self.regs[addr] = val

    def get(self, addr: Union[str, int]) -> UInt32:
        addr = self._name_to_addr(addr)
        if addr is None:
            raise RuntimeError(f"Invalid CSR name: {addr}!")
        if addr in self.virtual_regs:
            return self.virtual_regs[addr]()
        return self.regs[addr]

    def set_listener(self, addr: Union[str, int], listener: Callable[[UInt32, UInt32], None]):
        addr = self._name_to_addr(addr)
        if addr is None:
            print("unknown csr address name: {}".format(addr))
            return
        self.listeners[addr] = listener

    # mstatus properties
    def set_mstatus(self, name: str, val: UInt32):
        """
        Set mstatus bits using this helper. mstatus is a 32 bit register, holding various machine status flags
        Setting them by hand is super painful, so this helper allows you to set specific bits.

        Please make sure your supplied value has the correct width!

        :param name:
        :param val:
        :return:
        """
        size = 2 if name in MSTATUS_LEN_2 else 1
        off = MSTATUS_OFFSETS[name]
        mask = (2 ** size - 1) << off
        old_val = self.get('mstatus')
        erased = old_val & (~mask)
        new_val = erased | (val << off)
        self.set('mstatus', new_val)

    def get_mstatus(self, name) -> UInt32:
        if not self.mstatus_cache_dirty and name in self.mstatus_cache:
            return self.mstatus_cache[name]

        size = 2 if name in MSTATUS_LEN_2 else 1
        off = MSTATUS_OFFSETS[name]
        mask = (2 ** size - 1) << off
        val = (self.get('mstatus') & mask) >> off
        if self.mstatus_cache_dirty:
            self.mstatus_cache = dict(name=val)
        else:
            self.mstatus_cache[name] = val
        return val

    def callback(self, addr: Union[str, int]):
        def inner(func: Callable[[UInt32, UInt32], None]):
            self.set_listener(addr, func)
            return func

        return inner

    def assert_can_read(self, mode: PrivModes, addr: int):
        if (addr >> 8) & 3 > mode.value:
            raise InstructionAccessFault(addr)

    def assert_can_write(self, mode: PrivModes, addr: int):
        if (addr >> 8) & 3 > mode.value or addr >> 10 == 11:
            raise InstructionAccessFault(addr)

    def _name_to_addr(self, addr: Union[str, int]) -> Optional[int]:
        if isinstance(addr, str):
            if addr not in CSR_NAME_TO_ADDR:
                print("Unknown CSR register {}".format(addr))
                return None
            return CSR_NAME_TO_ADDR[addr]
        return addr

    def virtual_register(self, addr: Union[str, int]):
        addr = self._name_to_addr(addr)
        if addr is None:
            print("unknown csr address name: {}".format(addr))

        def inner(func: Callable[[], UInt32]):
            self.virtual_regs[addr] = func
            return func

        return inner

    def dump_mstatus(self):
        print(FMT_CSR + "[CSR] dumping mstatus:")
        i = 0
        for name in MSTATUS_OFFSETS:
            print("   {:<5} {}".format(name, self.get_mstatus(name)), end="")
            if i % 6 == 5:
                print()
            i += 1
        print(FMT_NONE)
