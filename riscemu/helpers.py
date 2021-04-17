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


def int_to_bytes(val, bytes=4):
    """
    int -> byte (two's complement)
    """
    return bytearray([
        (val >> ((bytes-i-1) * 8)) & 0xFF for i in range(bytes)
    ])


def int_from_bytes(bytes):
    """
    byte -> int (two's complement)
    """
    num = 0
    for b in bytes:
        num = num << 8
        num += b
    sign = num >> (len(bytes) * 8 - 1)
    if sign:
        return num - 2 ** (8 * len(bytes))
    return num

FMT_ORANGE = '\033[33m'
FMT_GRAY = '\033[37m'
FMT_BOLD = '\033[1m'
FMT_NONE = '\033[0m'
FMT_UNDERLINE = '\033[4m'