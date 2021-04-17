from .Exceptions import NumberFormatException

def align_addr(addr: int, to_bytes: int = 8):
    """
    align an address to `to_bytes` (meaning addr & to_bytes = 0)
    """
    return addr + (-addr % to_bytes)


def parse_numeric_argument(arg: str):
    """
    parse hex or int strings
    """
    if arg.startswith('0x') or arg.startswith('0X'):
        return int(arg, 16)
    return int(arg)


def int_to_bytes(val, bytes=4, unsigned=False):
    """
    int -> byte (two's complement)
    """
    if unsigned and val < 0:
        raise NumberFormatException("unsigned negative number!")
    return bytearray([
        (val >> ((bytes-i-1) * 8)) & 0xFF for i in range(bytes)
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
        return 2**(bytes * 8) + num
    return num


def to_signed(num: int, bytes=4):
    if num >> (bytes * 8 - 1):
        return num - 2 ** (8 * bytes)
    return num

# Colors

FMT_RED = '\033[31m'
FMT_ORANGE = '\033[33m'
FMT_GRAY = '\033[37m'
FMT_CYAN = '\033[36m'
FMT_GREEN = '\033[32m'
FMT_BOLD = '\033[1m'
FMT_MAGENTA = '\033[35m'
FMT_NONE = '\033[0m'
FMT_UNDERLINE = '\033[4m'

FMT_ERROR = FMT_RED + FMT_BOLD
