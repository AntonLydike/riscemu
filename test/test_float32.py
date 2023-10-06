import math

from riscemu.core import BaseFloat

# pi encoded as a 32bit little endian float
PI_BYTES_LE = b"\xdb\x0fI@"


def test_float_serialization():
    assert BaseFloat(PI_BYTES_LE) == BaseFloat(math.pi)
    assert BaseFloat(math.pi).bytes == PI_BYTES_LE


def test_random_float_ops():
    val = BaseFloat(5)
    assert val**2 == 25
    assert val // 2 == 2
    assert val * 3 == 15
    assert val - 2 == 3
    assert val * val == 25
    assert BaseFloat(9) ** 0.5 == 3


def test_float_from_raw_int_conversion():
    assert BaseFloat.from_bytes(1084227584) == BaseFloat(5.0)
