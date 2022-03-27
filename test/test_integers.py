from unittest import TestCase

from riscemu.types import Int32, UInt32


class TestTokenizer(TestCase):

    def test_logical_right_shift(self):
        a = Int32(100)
        self.assertEqual(a.shift_right_logical(0), a)
        self.assertEqual(a.shift_right_logical(10), 0)
        self.assertEqual(a.shift_right_logical(1), 100>>1)

        a = Int32(-100)
        self.assertEqual(a.shift_right_logical(0), a)
        self.assertEqual(a.shift_right_logical(1), 2147483598)
        self.assertEqual(a.shift_right_logical(10), 4194303)
        self.assertEqual(a.shift_right_logical(31), 1)
        self.assertEqual(a.shift_right_logical(32), 0)
