from dataclasses import dataclass
from collections import defaultdict

COLOR = True

FMT_ORANGE = '\033[33m'
FMT_GRAY = '\033[37m'
FMT_BOLD = '\033[1m'
FMT_NONE = '\033[0m'
FMT_UNDERLINE = '\033[4m'


class Registers:
    def __init__(self, cpu: 'CPU'):
        self.cpu = cpu
        self.vals = defaultdict(lambda: 0)
        self.last_mod = 'ft0'
        self.last_access = 'a3'

    def dump(self, small=False):
        named_regs = [self.reg_repr(reg) for reg in Registers.named_registers()]

        lines = [[] for i in range(12)]
        if small:
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
                    lines[i].append(self.reg_repr(reg))

        print("Registers[{},{}](".format(
            FMT_ORANGE + FMT_UNDERLINE + 'read' + FMT_NONE,
            FMT_ORANGE + FMT_BOLD + 'written' + FMT_NONE
        ))
        if small:
            print("\t" + " ".join(named_regs[0:3]))
            print("\t" + " ".join(named_regs[3:]))
            print("\t" + "--------------- " * 3)
        else:
            print("\t" + " ".join(named_regs))
            print("\t" + "--------------- " * 6)
        for line in lines:
            print("\t" + " ".join(line))
        print(")")

    def reg_repr(self, reg):
        txt = '{:4}=0x{:08X}'.format(reg, self.get(reg))
        if reg == 'fp':
            reg = 's0'
        if reg == self.last_mod:
            return FMT_ORANGE + FMT_BOLD + txt + FMT_NONE
        if reg == self.last_access:
            return FMT_ORANGE + FMT_UNDERLINE + txt + FMT_NONE
        if reg == 'zero':
            return txt
        if self.get(reg) == 0 and reg not in Registers.named_registers():
            return FMT_GRAY + txt + FMT_NONE
        return txt

    def set(self, reg, val):
        if reg == 'zero':
            print("[Registers.set] trying to set read-only register: {}".format(reg))
            return False
        if reg not in Registers.all_registers():
            print("[Registers.set] invalid register name: {}".format(reg))
            return False
        # replace fp register with s1, as these are the same register
        if reg == 'fp':
            reg = 's1'
        self.last_mod = reg
        setattr(self, reg, val)

    def get(self, reg):
        if not reg in Registers.all_registers():
            print("[Registers.get] invalid register name: {}".format(reg))
            return 0
        if reg == 'fp':
            reg = 's0'
        return self.vals[reg]

    @staticmethod
    def all_registers():
        return ['zero', 'ra', 'sp', 'gp', 'tp', 's0', 'fp',
                't0', 't1', 't2', 't3', 't4', 't5', 't6',
                's1', 's2', 's3', 's4', 's5', 's6', 's7', 's8', 's9', 's10', 's11',
                'a0', 'a1', 'a2', 'a3', 'a4', 'a5', 'a6', 'a7',
                'ft0', 'ft1', 'ft2', 'ft3', 'ft4', 'ft5', 'ft6', 'ft7',
                'fs0', 'fs1', 'fs2', 'fs3', 'fs4', 'fs5', 'fs6', 'fs7', 'fs8', 'fs9', 'fs10', 'fs11',
                'fa0', 'fa1', 'fa2', 'fa3', 'fa4', 'fa5', 'fa6', 'fa7']

    @staticmethod
    def named_registers():
        return ['zero', 'ra', 'sp', 'gp', 'tp', 'fp']

class CPU:
    def instruction_lb(self, instruction):
        pass

    def instruction_lh(self, instruction):
        pass

    def instruction_lw(self, instruction):
        pass

    def instruction_lbu(self, instruction):
        pass

    def instruction_lhu(self, instruction):
        pass

    def instruction_sb(self, instruction):
        pass

    def instruction_sh(self, instruction):
        pass

    def instruction_sw(self, instruction):
        pass

    def instruction_sll(self, instruction):
        pass

    def instruction_slli(self, instruction):
        pass

    def instruction_srl(self, instruction):
        pass

    def instruction_srli(self, instruction):
        pass

    def instruction_sra(self, instruction):
        pass

    def instruction_srai(self, instruction):
        pass

    def instruction_add(self, instruction):
        pass

    def instruction_addi(self, instruction):
        pass

    def instruction_sub(self, instruction):
        pass

    def instruction_lui(self, instruction):
        pass

    def instruction_auipc(self, instruction):
        pass

    def instruction_xor(self, instruction):
        pass

    def instruction_xori(self, instruction):
        pass

    def instruction_or(self, instruction):
        pass

    def instruction_ori(self, instruction):
        pass

    def instruction_and(self, instruction):
        pass

    def instruction_andi(self, instruction):
        pass

    def instruction_slt(self, instruction):
        pass

    def instruction_slti(self, instruction):
        pass

    def instruction_sltu(self, instruction):
        pass

    def instruction_sltiu(self, instruction):
        pass

    def instruction_beq(self, instruction):
        pass

    def instruction_bne(self, instruction):
        pass

    def instruction_blt(self, instruction):
        pass

    def instruction_bge(self, instruction):
        pass

    def instruction_bltu(self, instruction):
        pass

    def instruction_bgeu(self, instruction):
        pass

    def instruction_j(self, instruction):
        pass

    def instruction_jr(self, instruction):
        pass

    def instruction_jal(self, instruction):
        pass

    def instruction_jalr(self, instruction):
        pass

    def instruction_ret(self, instruction):
        pass

    def instruction_scall(self, instruction):
        pass

    def instruction_break(self, instruction):
        pass

    def instruction_nop(self, instruction):
        pass

    @staticmethod
    def all_instructions():
        for method in vars(CPU):
            if method.startswith('instruction_'):
                yield method[12:]


@dataclass(frozen=True)
class Syscall:
    id: int
    registers: Registers


class SyscallInterface:
    def handle_syscall(self, scall: Syscall):
        pass


a = Registers(None)
a.dump()
