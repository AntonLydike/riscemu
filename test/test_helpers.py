
from riscemu.helpers import *

def test_align_address():
    assert align_addr(3, 1) == 3
    assert align_addr(3, 2) == 4
    assert align_addr(3, 4) == 4
    assert align_addr(3, 8) == 8
    assert align_addr(8, 8) == 8


def test_parse_numeric():
    assert parse_numeric_argument('13') == 13
    assert parse_numeric_argument('0x100') == 256
    assert parse_numeric_argument('-13') == -13
