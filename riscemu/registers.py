"""
RiscEmu (c) 2021-2022 Anton Lydike

SPDX-License-Identifier: MIT
"""

from collections import defaultdict

from .helpers import *

if typing.TYPE_CHECKING:
    from .types import Int32


class Registers:
    """
    Represents a bunch of registers
    """

    def __init__(self):
        from .types import Int32
        self.vals = defaultdict(lambda: Int32(0))
        self.last_set = None
        self.last_read = None

    def dump(self, full=False):
        """
        Dump all registers to stdout
        :param full: If True, floating point registers are dumped too
        """
        named_regs = [self._reg_repr(reg) for reg in Registers.named_registers()]

        lines = [[] for i in range(12)]
        if not full:
            regs = [('a', 8), ('s', 12), ('t', 7)]
        else:
            regs = [
                ('a', 8),
                ('s', 12),
                ('t', 7),
                ('ft', 8),
                ('fa', 8),
                ('fs', 12),
            ]
        for name, s in regs:
            for i in range(12):
                if i >= s:
                    lines[i].append(" " * 15)
                else:
                    reg = '{}{}'.format(name, i)
                    lines[i].append(self._reg_repr(reg))

        print("Registers[{},{}](".format(
            FMT_ORANGE + FMT_UNDERLINE + 'read' + FMT_NONE,
            FMT_ORANGE + FMT_BOLD + 'written' + FMT_NONE
        ))
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
        print("Registers[a]:" + " ".join(self._reg_repr('a{}'.format(i)) for i in range(8)))

    def _reg_repr(self, reg):
        txt = '{:4}=0x{:08X}'.format(reg, self.get(reg, False))
        if reg == 'fp':
            reg = 's0'
        if reg == self.last_set:
            return FMT_ORANGE + FMT_BOLD + txt + FMT_NONE
        if reg == self.last_read:
            return FMT_ORANGE + FMT_UNDERLINE + txt + FMT_NONE
        if reg == 'zero':
            return txt
        if self.get(reg, False) == 0 and reg not in Registers.named_registers():
            return FMT_GRAY + txt + FMT_NONE
        return txt

    def set(self, reg, val: 'Int32', mark_set=True) -> bool:
        """
        Set a register content to val
        :param reg: The register to set
        :param val: The new value
        :param mark_set: If True, marks this register as "last accessed" (only used internally)
        :return: If the operation was successful
        """

        from .types import Int32
        # remove after refactoring is complete
        if not isinstance(val, Int32):
            raise RuntimeError("Setting register to non-Int32 value! Please refactor your code!")

        if reg == 'zero':
            return False
        # if reg not in Registers.all_registers():
        #    raise InvalidRegisterException(reg)
        # replace fp register with s1, as these are the same register
        if reg == 'fp':
            reg = 's1'
        if mark_set:
            self.last_set = reg
        # check 32 bit signed bounds
        self.vals[reg] = val
        return True

    def get(self, reg, mark_read=True) -> 'Int32':
        """
        Retuns the contents of register reg
        :param reg: The register name
        :param mark_read: If the register should be markes as "last read" (only used internally)
        :return: The contents of register reg
        """
        # if reg not in Registers.all_registers():
        #    raise InvalidRegisterException(reg)
        if reg == 'fp':
            reg = 's0'
        if mark_read:
            self.last_read = reg
        return self.vals[reg]

    @staticmethod
    def all_registers():
        """
        Return a list of all valid registers
        :return: The list
        """
        return ['zero', 'ra', 'sp', 'gp', 'tp', 's0', 'fp',
                't0', 't1', 't2', 't3', 't4', 't5', 't6',
                's1', 's2', 's3', 's4', 's5', 's6', 's7', 's8', 's9', 's10', 's11',
                'a0', 'a1', 'a2', 'a3', 'a4', 'a5', 'a6', 'a7',
                'ft0', 'ft1', 'ft2', 'ft3', 'ft4', 'ft5', 'ft6', 'ft7',
                'fs0', 'fs1', 'fs2', 'fs3', 'fs4', 'fs5', 'fs6', 'fs7', 'fs8', 'fs9', 'fs10', 'fs11',
                'fa0', 'fa1', 'fa2', 'fa3', 'fa4', 'fa5', 'fa6', 'fa7']

    @staticmethod
    def named_registers():
        """
        Return all named registers
        :return: The list
        """
        return ['zero', 'ra', 'sp', 'gp', 'tp', 'fp']
