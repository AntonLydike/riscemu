from .instruction_set import InstructionSet, Instruction


class RV_Debug(InstructionSet):
    def instruction_print(self, ins: Instruction):
        reg = ins.get_reg(0)
        print("register {} contains value {}".format(reg, self.regs.get(reg)))

    def instruction_print_uint(self, ins: Instruction):
        reg = ins.get_reg(0)
        print(
            "register {} contains value {}".format(
                reg, self.regs.get(reg).unsigned_value
            )
        )

    def instruction_print_hex(self, ins: Instruction):
        reg = ins.get_reg(0)
        print("register {} contains value {}".format(reg, hex(self.regs.get(reg))))

    def instruction_print_uhex(self, ins: Instruction):
        reg = ins.get_reg(0)
        print(
            "register {} contains value {}".format(
                reg, hex(self.regs.get(reg).unsigned_value)
            )
        )
