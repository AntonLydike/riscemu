import math

from riscemu.core import Float32

# pi encoded as a 32bit little endian float
PI_BYTES_LE = b"\xdb\x0fI@"


def test_float_serialization():
    assert Float32(PI_BYTES_LE) == Float32(math.pi)
    assert Float32(math.pi).bytes == PI_BYTES_LE


def test_random_float_ops():
    val = Float32(5)
    assert val**2 == 25
    assert val // 2 == 2
    assert val * 3 == 15
    assert val - 2 == 3
    assert val * val == 25
    assert Float32(9) ** 0.5 == 3


def test_float_from_raw_int_conversion():
    assert Float32.from_bytes(1084227584) == Float32(5.0)
