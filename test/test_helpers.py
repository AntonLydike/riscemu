from unittest import TestCase

from riscemu.helpers import *


class Test(TestCase):
    def test_int_to_bytes(self):
        self.assertEqual(int_to_bytes(-1), bytearray([0xff] * 4), "-1")
        self.assertEqual(int_to_bytes(1), bytearray([0, 0, 0, 1]), "1")
        self.assertEqual(int_to_bytes(1231132), bytearray(b'\x00\x12\xc9\x1c'), "random number")
        self.assertEqual(int_to_bytes(-1231132), bytearray(b'\xff\xed6\xe4'), "random negative number")

    def test_int_from_bytes(self):
        self.assertEqual(bytearray([0xff] * 4), int_to_bytes(-1), "-1")
        self.assertEqual(bytearray([0, 0, 0, 1]), int_to_bytes(1), "1")
        self.assertEqual(bytearray(b'\x00\x12\xc9\x1c'), int_to_bytes(1231132), "random number")
        self.assertEqual(bytearray(b'\xff\xed6\xe4'), int_to_bytes(-1231132), "random negative number")

    def test_to_unsigned(self):
        self.assertEqual(to_unsigned(-1), 0xFFFFFFFF)
        self.assertEqual(to_unsigned(-100), 0xffffff9c)
        self.assertEqual(to_unsigned(1), 1)
        self.assertEqual(to_unsigned(0xffffffff), 0xffffffff)
        self.assertEqual(to_unsigned(0xffed36e4), 0xffed36e4)

    def test_to_signed(self):
        self.assertEqual(to_signed(0xFFFFFFFF), -1)
        self.assertEqual(to_signed(0xffed36e4), -1231132)
        self.assertEqual(to_signed(0x0FFFFFFF), 0x0FFFFFFF)

    def test_bind_twos_complement(self):
        minval = -(1 << 31)
        maxval = ((1 << 31)-1)

        self.assertEqual(bind_twos_complement(minval), minval, "minval preserves")
        self.assertEqual(bind_twos_complement(minval), minval, )
        self.assertEqual(bind_twos_complement(maxval), maxval, "maxval preserves")
        self.assertEqual(bind_twos_complement(minval - 1), maxval, "minval-1 wraps")
        self.assertEqual(bind_twos_complement(maxval + 1), minval, "maxval+1 wraps")
        self.assertEqual(bind_twos_complement(0), 0, "0 is 0")
        self.assertEqual(bind_twos_complement(1), 1, "1 is 1")
        self.assertEqual(bind_twos_complement(-1), -1, "-1 is -1")