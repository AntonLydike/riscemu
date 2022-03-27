from unittest import TestCase

from riscemu.helpers import *


class TestHelpers(TestCase):

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