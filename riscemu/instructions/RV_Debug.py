from typing import Union

from .instruction_set import InstructionSet, Instruction
from ..core import BaseFloat, Int32, Float32


class RV_Debug(InstructionSet):
    def instruction_print(self, ins: Instruction):
        reg = ins.get_reg(0)
        if len(ins.args) == 2:
            msg = ins.args[1]
            print(msg.format(reg, self.regs.get(reg)))
        else:
            print("register {} contains value {}".format(reg, self.regs.get(reg)))

    def instruction_printf(self, ins: Instruction):
        fmt_str = ins.args[0]
        regs = tuple(self.smart_get_reg(x) for x in ins.args[1:])
        print(fmt_str.format(*regs))

    def instruction_print_float(self, ins: Instruction):
        reg = ins.get_reg(0)
        print("register {} contains value {}".format(reg, self.regs.get_f(reg).value))

    def instruction_print_float_s(self, ins: Instruction):
        reg = ins.get_reg(0)
        print(
            "register {} contains value {}".format(
                reg, Float32.bitcast(self.regs.get_f(reg)).value
            )
        )

    def instruction_print_uint(self, ins: Instruction):
        reg = ins.get_reg(0)
        print(
            "register {} contains value {}".format(
                reg, self.regs.get(reg).unsigned_value
            )
        )

    def instruction_print_hex(self, ins: Instruction):
        reg = ins.get_reg(0)
        print(
            "register {} contains value {}".format(reg, hex(self.regs.get(reg).value))
        )

    def instruction_print_uhex(self, ins: Instruction):
        reg = ins.get_reg(0)
        print(
            "register {} contains value {}".format(
                reg, hex(self.regs.get(reg).unsigned_value)
            )
        )

    def smart_get_reg(self, reg_name: str) -> Union[Int32, BaseFloat]:
        if reg_name[0] == "f":
            return self.regs.get_f(reg_name)
        return self.regs.get(reg_name)
