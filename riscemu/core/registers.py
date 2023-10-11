"""
RiscEmu (c) 2023 Anton Lydike

SPDX-License-Identifier: MIT
"""

from collections import defaultdict
from typing import Type

from ..helpers import *

from . import Int32, BaseFloat


class Registers:
    """
    Represents a bunch of registers
    """

    valid_regs = {
        "zero",
        "ra",
        "sp",
        "gp",
        "tp",
        "s0",
        "fp",
        "t0",
        "t1",
        "t2",
        "t3",
        "t4",
        "t5",
        "t6",
        "s1",
        "s2",
        "s3",
        "s4",
        "s5",
        "s6",
        "s7",
        "s8",
        "s9",
        "s10",
        "s11",
        "a0",
        "a1",
        "a2",
        "a3",
        "a4",
        "a5",
        "a6",
        "a7",
    }

    float_regs = {
        "ft0",
        "ft1",
        "ft2",
        "ft3",
        "ft4",
        "ft5",
        "ft6",
        "ft7",
        "ft8",
        "ft9",
        "ft10",
        "ft11",
        "fs0",
        "fs1",
        "fs2",
        "fs3",
        "fs4",
        "fs5",
        "fs6",
        "fs7",
        "fs8",
        "fs9",
        "fs10",
        "fs11",
        "fa0",
        "fa1",
        "fa2",
        "fa3",
        "fa4",
        "fa5",
        "fa6",
        "fa7",
    }

    flen: int
    _float_type: Type[BaseFloat]

    def __init__(self, infinite_regs: bool = False, flen: int = 32):
        self.vals: dict[str, Int32] = defaultdict(UInt32)
        self.flen = flen
        self._float_type = BaseFloat.flen_to_cls(flen)
        self.float_vals: dict[str, BaseFloat] = defaultdict(self._float_type)

        self.last_set = None
        self.last_read = None

        self.infinite_regs = infinite_regs

    def dump(self, full: bool = False):
        """
        Dump all registers to stdout
        :param full: If True, floating point registers are dumped too
        """
        named_regs = [self._reg_repr(reg) for reg in Registers.named_registers()]

        lines: list[list[str]] = [[] for _ in range(12)]
        if not full:
            regs = [("a", 8), ("s", 12), ("t", 7)]
        else:
            regs = [
                ("a", 8),
                ("s", 12),
                ("t", 7),
                ("ft", 8),
                ("fa", 8),
                ("fs", 12),
            ]
        for name, s in regs:
            for i in range(12):
                if i >= s:
                    lines[i].append(" " * 15)
                else:
                    reg = "{}{}".format(name, i)
                    lines[i].append(self._reg_repr(reg))

        print(
            "Registers[{},{}](".format(
                FMT_ORANGE + FMT_UNDERLINE + "read" + FMT_NONE,
                FMT_ORANGE + FMT_BOLD + "written" + FMT_NONE,
            )
        )
        if not full:
            print("\t" + " ".join(named_regs[0:3]))
            print("\t" + " ".join(named_regs[3:]))
            print("\t" + "--------------- " * 3)
        else:
            print("\t" + " ".join(named_regs))
            print("\t" + "--------------- " * 6)
        for line in lines:
            print("\t" + " ".join(line))
        print(")")

    def dump_reg_a(self):
        """
        Dump the a registers
        """
        print(
            "Registers[a]:"
            + " ".join(self._reg_repr("a{}".format(i)) for i in range(8))
        )

    def _reg_repr(self, reg: str, name_len=4, fmt="08X"):
        if reg in self.float_regs:
            txt = "{:{}}={: .3e}".format(reg, name_len, self.get_f(reg, False))
        else:
            txt = "{:{}}=0x{:{}}".format(reg, name_len, self.get(reg, False), fmt)
        if reg == "fp":
            reg = "s0"
        if reg == self.last_set:
            return FMT_ORANGE + FMT_BOLD + txt + FMT_NONE
        if reg == self.last_read:
            return FMT_ORANGE + FMT_UNDERLINE + txt + FMT_NONE
        if reg == "zero":
            return txt
        should_grayscale_int = (
            reg in self.valid_regs
            and self.get(reg, False) == 0
            and reg not in Registers.named_registers()
        )
        should_grayscale_float = reg in self.float_regs and self.get_f(reg, False) == 0
        if should_grayscale_int or should_grayscale_float:
            return FMT_GRAY + txt + FMT_NONE
        return txt

    def set(self, reg: str, val: Int32, mark_set: bool = True) -> bool:
        """
        Set a register content to val
        :param reg: The register to set
        :param val: The new value
        :param mark_set: If True, marks this register as "last accessed" (only used internally)
        :return: If the operation was successful
        """

        if reg == "zero":
            return False
        # if reg not in Registers.all_registers():
        #    raise InvalidRegisterException(reg)
        # replace fp register with s1, as these are the same register
        if reg == "fp":
            reg = "s1"
        if mark_set:
            self.last_set = reg

        if not self.infinite_regs and reg not in self.valid_regs:
            raise RuntimeError("Invalid register: {}".format(reg))

        self.vals[reg] = val.unsigned()
        return True

    def get(self, reg: str, mark_read: bool = True) -> Int32:
        """
        Returns the contents of register reg
        :param reg: The register name
        :param mark_read: If the register should be marked as "last read" (only used internally)
        :return: The contents of register reg
        """
        # if reg not in Registers.all_registers():
        #    raise InvalidRegisterException(reg)
        if reg == "fp":
            reg = "s0"

        if not self.infinite_regs and reg not in self.valid_regs:
            raise RuntimeError("Invalid register: {}".format(reg))

        if mark_read:
            self.last_read = reg
        return self.vals[reg]

    def get_f(self, reg: str) -> BaseFloat:
        if not self.infinite_regs and reg not in self.float_regs:
            raise RuntimeError("Invalid float register: {}".format(reg))
        return self.float_vals[reg]

    def set_f(self, reg: str, val: BaseFloat):
        if not self.infinite_regs and reg not in self.float_regs:
            raise RuntimeError("Invalid float register: {}".format(reg))
        self.float_vals[reg] = self._float_type.bitcast(val)

    @staticmethod
    def named_registers():
        """
        Return all named registers
        :return: The list
        """
        return ["zero", "ra", "sp", "gp", "tp", "fp"]

    def __repr__(self):
        return "<Registers[xlen=32,flen={}]{}>".format(
            self.flen,
            "{"
            + ", ".join(self._reg_repr("a{}".format(i), 2, "0x") for i in range(8))
            + "}",
        )
