import traceback
from dataclasses import dataclass
from collections import defaultdict

from .Exceptions import *
from .helpers import *

import typing
if typing.TYPE_CHECKING:
    from . import MMU, Executable, LoadedExecutable, LoadedInstruction

COLOR = True

FMT_ORANGE = '\033[33m'
FMT_GRAY = '\033[37m'
FMT_BOLD = '\033[1m'
FMT_NONE = '\033[0m'
FMT_UNDERLINE = '\033[4m'


class Registers:
    def __init__(self):
        self.vals = defaultdict(lambda: 0)
        self.last_mod = None
        self.last_access = None

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

    def dump_reg_a(self):
        print("Registers[a]:" + " ".join(self.reg_repr('a{}'.format(i)) for i in range(8)))

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
            raise InvalidRegisterException(reg)
        # replace fp register with s1, as these are the same register
        if reg == 'fp':
            reg = 's1'
        self.last_mod = reg
        self.vals[reg] = val

    def get(self, reg):
        if not reg in Registers.all_registers():
            raise InvalidRegisterException(reg)
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
    def __init__(self):
        from . import MMU, Executable, LoadedExecutable, LoadedInstruction

        self.mmu = MMU()
        self.regs = Registers()
        self.pc = 0
        self.exit = False

        self.syscall_int = SyscallInterface()

    def load(self, e: 'Executable'):
        return self.mmu.load_bin(e)

    def run_loaded(self, le: 'LoadedExecutable'):
        self.pc = le.run_ptr
        sp, hp = le.stack_heap
        self.regs.set('sp', sp)
        self.regs.set('a0', hp)  # set a0 to point to the heap

        self.__run()

    def __run(self):
        if self.pc <= 0:
            return False
        ins = None
        try:
            while not self.exit:
                ins = self.mmu.read_ins(self.pc)
                self.pc += 1
                self.__run_instruction(ins)
        except RiscemuBaseException as ex:
            print("[CPU] excpetion caught at {}:".format(ins))
            print("      " + ex.message())
            traceback.print_exception(type(ex), ex, ex.__traceback__)

    def __run_instruction(self, ins: 'LoadedInstruction'):
        name = 'instruction_' + ins.name
        if hasattr(self, name):
            getattr(self, name)(ins)
        else:
            raise RuntimeError("Unknown instruction: {}".format(ins))

    def instruction_lb(self, ins: 'LoadedInstruction'):
        INS_NOT_IMPLEMENTED(ins)

    def instruction_lh(self, ins: 'LoadedInstruction'):
        INS_NOT_IMPLEMENTED(ins)

    def instruction_lw(self, ins: 'LoadedInstruction'):
        INS_NOT_IMPLEMENTED(ins)

    def instruction_lbu(self, ins: 'LoadedInstruction'):
        INS_NOT_IMPLEMENTED(ins)

    def instruction_lhu(self, ins: 'LoadedInstruction'):
        INS_NOT_IMPLEMENTED(ins)

    def instruction_sb(self, ins: 'LoadedInstruction'):
        src = ins.get_reg(0)
        if len(ins.args) == 2:
            reg, imm = ins.get_imm_reg(1)
        else:
            reg = ins.get_reg(1)
            imm = ins.get_imm(2)
        addr = self.regs.get(reg) + imm
        self.mmu.write(addr, 1, int_to_bytes(self.regs.get(reg), 1))

    def instruction_sh(self, ins: 'LoadedInstruction'):
        src = ins.get_reg(0)
        if len(ins.args) == 2:
            reg, imm = ins.get_imm_reg(1)
        else:
            reg = ins.get_reg(1)
            imm = ins.get_imm(2)
        addr = self.regs.get(reg) + imm
        self.mmu.write(addr, 2, int_to_bytes(self.regs.get(reg), 2))

    def instruction_sw(self, ins: 'LoadedInstruction'):
        src = ins.get_reg(0)
        if len(ins.args) == 2:
            imm, reg = ins.get_imm_reg(1)
        else:
            reg = ins.get_reg(1)
            imm = ins.get_imm(2)
        addr = self.regs.get(reg) + imm
        self.mmu.write(addr, 4, int_to_bytes(self.regs.get(reg), 4))

    def instruction_sll(self, ins: 'LoadedInstruction'):
        INS_NOT_IMPLEMENTED(ins)

    def instruction_slli(self, ins: 'LoadedInstruction'):
        INS_NOT_IMPLEMENTED(ins)

    def instruction_srl(self, ins: 'LoadedInstruction'):
        INS_NOT_IMPLEMENTED(ins)

    def instruction_srli(self, ins: 'LoadedInstruction'):
        INS_NOT_IMPLEMENTED(ins)

    def instruction_sra(self, ins: 'LoadedInstruction'):
        INS_NOT_IMPLEMENTED(ins)

    def instruction_srai(self, ins: 'LoadedInstruction'):
        INS_NOT_IMPLEMENTED(ins)

    def instruction_add(self, ins: 'LoadedInstruction'):
        dst = ins.get_reg(0)
        src1 = ins.get_reg(1)
        src2 = ins.get_reg(2)
        self.regs.set(
            dst,
            self.regs.get(src1) + self.regs.get(src2)
        )

    def instruction_addi(self, ins: 'LoadedInstruction'):
        dst = ins.get_reg(0)
        src1 = ins.get_reg(1)
        imm = ins.get_imm(2)
        self.regs.set(
            dst,
            self.regs.get(src1) + imm
        )

    def instruction_sub(self, ins: 'LoadedInstruction'):
        INS_NOT_IMPLEMENTED(ins)

    def instruction_lui(self, ins: 'LoadedInstruction'):
        INS_NOT_IMPLEMENTED(ins)

    def instruction_auipc(self, ins: 'LoadedInstruction'):
        INS_NOT_IMPLEMENTED(ins)

    def instruction_xor(self, ins: 'LoadedInstruction'):
        INS_NOT_IMPLEMENTED(ins)

    def instruction_xori(self, ins: 'LoadedInstruction'):
        INS_NOT_IMPLEMENTED(ins)

    def instruction_or(self, ins: 'LoadedInstruction'):
        INS_NOT_IMPLEMENTED(ins)

    def instruction_ori(self, ins: 'LoadedInstruction'):
        INS_NOT_IMPLEMENTED(ins)

    def instruction_and(self, ins: 'LoadedInstruction'):
        INS_NOT_IMPLEMENTED(ins)

    def instruction_andi(self, ins: 'LoadedInstruction'):
        INS_NOT_IMPLEMENTED(ins)

    def instruction_slt(self, ins: 'LoadedInstruction'):
        INS_NOT_IMPLEMENTED(ins)

    def instruction_slti(self, ins: 'LoadedInstruction'):
        INS_NOT_IMPLEMENTED(ins)

    def instruction_sltu(self, ins: 'LoadedInstruction'):
        INS_NOT_IMPLEMENTED(ins)

    def instruction_sltiu(self, ins: 'LoadedInstruction'):
        INS_NOT_IMPLEMENTED(ins)

    def instruction_beq(self, ins: 'LoadedInstruction'):
        INS_NOT_IMPLEMENTED(ins)

    def instruction_bne(self, ins: 'LoadedInstruction'):
        INS_NOT_IMPLEMENTED(ins)

    def instruction_blt(self, ins: 'LoadedInstruction'):
        ASSERT_LEN(ins.args, 3)
        reg1 = ins.get_reg(0)
        reg2 = ins.get_reg(1)
        dest = ins.get_imm(2)
        if self.regs.get(reg1) < self.regs.get(reg2):
            self.pc = dest


    def instruction_bge(self, ins: 'LoadedInstruction'):
        INS_NOT_IMPLEMENTED(ins)

    def instruction_bltu(self, ins: 'LoadedInstruction'):
        INS_NOT_IMPLEMENTED(ins)

    def instruction_bgeu(self, ins: 'LoadedInstruction'):
        INS_NOT_IMPLEMENTED(ins)

    def instruction_j(self, ins: 'LoadedInstruction'):
        INS_NOT_IMPLEMENTED(ins)

    def instruction_jr(self, ins: 'LoadedInstruction'):
        INS_NOT_IMPLEMENTED(ins)

    def instruction_jal(self, ins: 'LoadedInstruction'):
        INS_NOT_IMPLEMENTED(ins)

    def instruction_jalr(self, ins: 'LoadedInstruction'):
        INS_NOT_IMPLEMENTED(ins)

    def instruction_ret(self, ins: 'LoadedInstruction'):
        INS_NOT_IMPLEMENTED(ins)

    def instruction_scall(self, ins: 'LoadedInstruction'):
        syscall = Syscall(self.regs.get('a7'), self.regs)
        self.syscall_int.handle_syscall(syscall)

    def instruction_break(self, ins: 'LoadedInstruction'):
        INS_NOT_IMPLEMENTED(ins)

    def instruction_nop(self, ins: 'LoadedInstruction'):
        INS_NOT_IMPLEMENTED(ins)

    def instruction_dbg(self, ins: 'LoadedInstruction'):
        import code
        code.interact(local=dict(globals(), **locals()))

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
        print("syscall {} received!".format(scall.id))
        scall.registers.dump_reg_a()


