"""
RiscEmu (c) 2021 Anton Lydike

SPDX-License-Identifier: MIT
"""

from math import log10, ceil
from typing import Iterable, Iterator, TypeVar, Generic, List, Optional

from .types.exceptions import *
from .types import Int32, UInt32


def align_addr(addr: int, to_bytes: int = 8) -> int:
    """
    align an address to `to_bytes` (meaning addr & to_bytes = 0)
    """
    return addr + (-addr % to_bytes)


def parse_numeric_argument(arg: str) -> int:
    """
    parse hex or int strings
    """
    try:
        if '0x' in arg or '0X' in arg:
            return int(arg, 16)
        return int(arg)
    except ValueError as ex:
        raise ParseException('Invalid immediate argument \"{}\", maybe missing symbol?'.format(arg), (arg, ex))


def create_chunks(my_list, chunk_size):
    """Split a list like [a,b,c,d,e,f,g,h,i,j,k,l,m] into e.g. [[a,b,c,d],[e,f,g,h],[i,j,k,l],[m]]"""
    return [my_list[i:i + chunk_size] for i in range(0, len(my_list), chunk_size)]


def apply_highlight(item, ind, hi_ind):
    """
    applies some hightlight such as underline to item if ind == hi_ind
    """
    if ind == hi_ind:
        return FMT_UNDERLINE + FMT_ORANGE + item + FMT_NONE
    return item


def highlight_in_list(items, hi_ind):
    return " ".join([apply_highlight(item, i, hi_ind) for i, item in enumerate(items)])


def format_bytes(byte_arr: bytearray, fmt: str, group: int = 1, highlight: int = -1):
    """Format byte array as per fmt. Group into groups of size `group`, and highlight index `highlight`."""
    chunks = create_chunks(byte_arr, group)
    if fmt == 'hex':
        return highlight_in_list(['0x{}'.format(ch.hex()) for ch in chunks], highlight)
    if fmt == 'int':
        spc = str(ceil(log10(2 ** (group * 8 - 1))) + 1)
        return highlight_in_list([('{:0' + spc + 'd}').format(Int32(ch)) for ch in chunks], highlight)
    if fmt == 'uint':
        spc = str(ceil(log10(2 ** (group * 8))))
        return highlight_in_list([('{:0' + spc + 'd}').format(UInt32(ch)) for ch in chunks],
                                 highlight)
    if fmt == 'ascii':
        return "".join(repr(chr(b))[1:-1] for b in byte_arr)


def bind_twos_complement(val):
    """
    does over/underflows for 32 bit two's complement numbers
    :param val:
    :return:
    """
    if val < -2147483648:
        return val + 4294967296
    elif val > 2147483647:
        return val - 4294967296
    return val


T = TypeVar('T')


class Peekable(Generic[T], Iterator[T]):
    def __init__(self, iterable: Iterable[T]):
        self.iterable = iter(iterable)
        self.cache: List[T] = list()

    def __iter__(self) -> Iterator[T]:
        return self

    def __next__(self) -> T:
        if self.cache:
            return self.cache.pop()
        return next(self.iterable)

    def peek(self) -> Optional[T]:
        try:
            if self.cache:
                return self.cache[0]
            pop = next(self.iterable)
            self.cache.append(pop)
            return pop
        except StopIteration:
            return None

    def push_back(self, item: T):
        self.cache = [item] + self.cache

    def is_empty(self) -> bool:
        return self.peek() is None


def get_section_base_name(section_name: str) -> str:
    if '.' not in section_name:
        print(FMT_PARSE + f"Invalid section {section_name}, not starting with a dot!" + FMT_NONE)
    return '.' + section_name.split('.')[1]
