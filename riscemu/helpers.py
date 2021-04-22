from math import log10, ceil, log
from .Exceptions import NumberFormatException
from .colors import *
from .Exceptions import *


def align_addr(addr: int, to_bytes: int = 8):
    """
    align an address to `to_bytes` (meaning addr & to_bytes = 0)
    """
    return addr + (-addr % to_bytes)


def parse_numeric_argument(arg: str):
    """
    parse hex or int strings
    """
    try:
        if '0x' in arg or '0X' in arg:
            return int(arg, 16)
        return int(arg)
    except ValueError as ex:
        raise ParseException('Invalid immediate argument \"{}\", maybe missing symbol?'.format(arg), (arg, ex))


def int_to_bytes(val, bytes=4, unsigned=False):
    """
    int -> byte (two's complement)
    """
    if unsigned and val < 0:
        raise NumberFormatException("unsigned negative number!")
    return bytearray([
        (val >> ((bytes - i - 1) * 8)) & 0xFF for i in range(bytes)
    ])


def int_from_bytes(bytes, unsigned=False):
    """
    byte -> int (two's complement)
    """
    num = 0
    for b in bytes:
        num = num << 8
        num += b

    if unsigned:
        return num

    return to_signed(num)


def to_unsigned(num: int, bytes=4):
    if num < 0:
        return 2 ** (bytes * 8) + num
    return num


def to_signed(num: int, bytes=4):
    if num >> (bytes * 8 - 1):
        return num - 2 ** (8 * bytes)
    return num


def create_chunks(my_list, chunk_size):
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
        print("printing ascii", "".join(chr(b) for b in byte_arr))
        return "".join(repr(chr(b))[1:-1] for b in byte_arr)
