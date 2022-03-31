from riscemu.colors import FMT_ERROR, FMT_NONE, FMT_BOLD, FMT_GREEN
from riscemu.instructions import InstructionSet
from riscemu.types import Instruction, CPU
from riscemu.decoder import RISCV_REGS

FMT_SUCCESS = FMT_GREEN + FMT_BOLD


def assert_equals(ins: Instruction, cpu: CPU):
    a, b = (get_arg_from_ins(ins, i, cpu) for i in (0, 2))
    return a == b


def assert_equals_mem(ins: Instruction, cpu: CPU):
    a, b = (get_arg_from_ins(ins, i, cpu) for i in (0, 2))
    a = cpu.mmu.read_int(a)
    return a == b


def assert_in(ins: Instruction, cpu: CPU):
    a = get_arg_from_ins(ins, 0, cpu)
    others = [get_arg_from_ins(ins, i, cpu) for i in range(2, len(ins.args))]
    return a in others


def _not(func):
    def test(ins: Instruction, cpu: CPU):
        return not func(ins, cpu)

    return test


def get_arg_from_ins(ins: Instruction, num: int, cpu: CPU):
    a = ins.args[num]
    if a in RISCV_REGS:
        return cpu.regs.get(a)
    return ins.get_imm(num)


assert_ops = {
    '==': assert_equals,
    '!=': _not(assert_equals),
    'in': assert_in,
    'not_in': _not(assert_in),
}


class TestIS(InstructionSet):
    def __init__(self, cpu: 'CPU'):
        print('[Test] loading testing ISA, this is only meant for running testcases and is not part of the RISC-V ISA!')
        self.failed = False
        super().__init__(cpu)

    def instruction_assert(self, ins: Instruction):
        if len(ins.args) < 3:
            print(FMT_ERROR + '[Test] Unknown assert statement: {}'.format(ins) + FMT_NONE)
            return
        op = ins.args[1]
        if op not in assert_ops:
            print(FMT_ERROR + '[Test] Unknown operation statement: {} in {}'.format(op, ins) + FMT_NONE)
            return

        if assert_ops[op](ins, self.cpu):
            print(FMT_SUCCESS + '[TestCase] 🟢 passed assertion {}'.format(ins))
        else:
            print(FMT_ERROR + '[TestCase] 🔴 failed assertion {}'.format(ins))
            self.cpu.halted = True
            self.failed = True

    def instruction_fail(self, ins: Instruction):
            print(FMT_ERROR + '[TestCase] 🔴 reached fail instruction! {}'.format(ins))
            self.cpu.halted = True
            self.failed = True

    def assert_mem(self, ins: Instruction):