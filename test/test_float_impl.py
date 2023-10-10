import math

from riscemu.core import Float32, Float64

# pi encoded as a 32bit little endian float
PI_BYTES_LE = b"\xdb\x0fI@"


def test_float_serialization():
    assert Float32(PI_BYTES_LE) == Float32(math.pi)
    assert Float32(math.pi).bytes == PI_BYTES_LE


def test_float_bitcast():
    f32_pi = Float32(math.pi)
    f64_pi32 = Float64.bitcast(f32_pi)
    assert f32_pi.bytes == Float32.bitcast(f64_pi32).bytes

    f64_pi = Float64(math.pi)
    f32_pi64 = Float32.bitcast(f64_pi)
    assert f64_pi.bytes[-4:] == f32_pi64.bytes
    assert Float64.bitcast(f32_pi64).bytes[:4] == b"\x00\x00\x00\x00"


def test_random_float_ops32():
    val = Float32(5)
    assert val**2 == 25
    assert val // 2 == 2
    assert val * 3 == 15
    assert val - 2 == 3
    assert val * val == 25
    assert Float32(9) ** 0.5 == 3


def test_random_float_ops64():
    val = Float64(5)
    assert val**2 == 25
    assert val // 2 == 2
    assert val * 3 == 15
    assert val - 2 == 3
    assert val * val == 25
    assert Float64(9) ** 0.5 == 3


def test_float_from_raw_bytes_conversion():
    assert Float32.from_bytes(b"\x00\x00\xa0@") == Float32(5.0)
