from riscemu.core import Int32, UInt32
import pytest


def test_logical_right_shift():
    a = Int32(100)
    assert a.shift_right_logical(0) == a
    assert a.shift_right_logical(10) == 0
    assert a.shift_right_logical(1) == 100 >> 1

    a = Int32(-100)
    assert a.shift_right_logical(0) == a
    assert a.shift_right_logical(1) == 2147483598
    assert a.shift_right_logical(10) == 4194303
    assert a.shift_right_logical(31) == 1
    assert a.shift_right_logical(32) == 0


@pytest.mark.parametrize(
    "val,expected_int",
    (
        (
            (0.0, 0),
            (-1.0, -1),
            (3.14159, 3),
            (float("NaN"), Int32.MIN_VALUE),
            (float("-inf"), Int32.MIN_VALUE),
            (float("inf"), Int32.MAX_VALUE),
            (1.0e100, Int32.MAX_VALUE),
            (-1.0e100, Int32.MIN_VALUE),
        )
    ),
)
def test_float_to_int_conversion(val: float, expected_int: int):
    assert Int32.from_float(val) == expected_int


@pytest.mark.parametrize(
    "val,expected_int",
    (
        (
            (0.0, 0),
            (3.14159, 3),
            (float("NaN"), UInt32.MIN_VALUE),
            (float("-inf"), UInt32.MIN_VALUE),
            (float("inf"), UInt32.MAX_VALUE),
            (1.0e100, UInt32.MAX_VALUE),
            (-1.0e100, UInt32.MIN_VALUE),
            (-1.0, UInt32.MIN_VALUE),
        )
    ),
)
def test_float_to_uint_conversion(val: float, expected_int: int):
    assert UInt32.from_float(val) == expected_int
