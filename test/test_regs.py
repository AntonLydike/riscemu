import pytest

from riscemu.core.registers import Registers
from riscemu.core import BaseFloat


def test_float_regs():
    r = Registers()
    # uninitialized register is zero
    assert r.get_f("fs0") == 0
    # get/set
    val = BaseFloat(3.14)
    r.set_f("fs0", val)
    assert r.get_f("fs0") == val


def test_unlimited_regs_works():
    r = Registers(infinite_regs=True)
    r.get("infinite")
    r.get_f("finfinite")


def test_unknown_reg_fails():
    r = Registers(infinite_regs=False)
    with pytest.raises(RuntimeError, match="Invalid register: az1"):
        r.get("az1")
