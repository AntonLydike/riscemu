"""
RiscEmu (c) 2021 Anton Lydike

SPDX-License-Identifier: MIT
"""

from math import log10, ceil
from .Exceptions import *


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


def int_to_bytes(val, bytes=4, unsigned=False) -> bytearray:
    """
    int -> byte (two's complement)
    """
    if unsigned and val < 0:
        raise NumberFormatException("unsigned negative number!")
    return bytearray(to_unsigned(val, bytes).to_bytes(bytes, 'little'))


def int_from_bytes(bytes, unsigned=False) -> int:
    """
    byte -> int (two's complement)
    """
    num = int.from_bytes(bytes, 'little')

    if unsigned:
        return num

    return to_signed(num)


def to_unsigned(num: int, bytes=4) -> int:
    if num < 0:
        return (2 ** (bytes * 8)) + num
    return num


def to_signed(num: int, bytes=4) -> int:
    if num >> (bytes * 8 - 1):
        return num - 2 ** (8 * bytes)
    return num


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
        return highlight_in_list([('{:0' + spc + 'd}').format(int_from_bytes(ch)) for ch in chunks], highlight)
    if fmt == 'uint':
        spc = str(ceil(log10(2 ** (group * 8))))
        return highlight_in_list([('{:0' + spc + 'd}').format(int_from_bytes(ch, unsigned=True)) for ch in chunks],
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
