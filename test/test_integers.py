from riscemu.types import Int32, UInt32


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
