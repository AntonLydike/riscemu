import traceback
from dataclasses import dataclass

from .Exceptions import *
from .helpers import *
from .Config import RunConfig
from .Registers import Registers
from .Syscall import SyscallInterface, Syscall

import typing
if typing.TYPE_CHECKING:
    from . import MMU, Executable, LoadedExecutable, LoadedInstruction



class CPU:
    def __init__(self, conf: RunConfig):
        from . import MMU
        self.pc = 0
        self.exit = False
        self.exit_code = 0
        self.conf = conf

        self.mmu = MMU(conf)
        self.regs = Registers()
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
        ASSERT_LEN(ins.args, 3)
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
        ASSERT_LEN(ins.args, 3)
        reg1 = ins.get_reg(0)
        reg2 = ins.get_reg(1)
        dest = ins.get_imm(2)
        if self.regs.get(reg1) == self.regs.get(reg2):
            self.pc = dest

    def instruction_bne(self, ins: 'LoadedInstruction'):
        ASSERT_LEN(ins.args, 3)
        reg1 = ins.get_reg(0)
        reg2 = ins.get_reg(1)
        dest = ins.get_imm(2)
        if self.regs.get(reg1) != self.regs.get(reg2):
            self.pc = dest

    def instruction_blt(self, ins: 'LoadedInstruction'):
        ASSERT_LEN(ins.args, 3)
        reg1 = ins.get_reg(0)
        reg2 = ins.get_reg(1)
        dest = ins.get_imm(2)
        if self.regs.get(reg1) < self.regs.get(reg2):
            self.pc = dest

    def instruction_bge(self, ins: 'LoadedInstruction'):
        ASSERT_LEN(ins.args, 3)
        reg1 = ins.get_reg(0)
        reg2 = ins.get_reg(1)
        dest = ins.get_imm(2)
        if self.regs.get(reg1) >= self.regs.get(reg2):
            self.pc = dest

    def instruction_bltu(self, ins: 'LoadedInstruction'):
        ASSERT_LEN(ins.args, 3)
        reg1 = to_unsigned(ins.get_reg(0))
        reg2 = to_unsigned(ins.get_reg(1))
        dest = ins.get_imm(2)
        if self.regs.get(reg1) < self.regs.get(reg2):
            self.pc = dest

    def instruction_bgeu(self, ins: 'LoadedInstruction'):
        ASSERT_LEN(ins.args, 3)
        reg1 = to_unsigned(ins.get_reg(0))
        reg2 = to_unsigned(ins.get_reg(1))
        dest = ins.get_imm(2)
        if self.regs.get(reg1) >= self.regs.get(reg2):
            self.pc = dest

    def instruction_j(self, ins: 'LoadedInstruction'):
        INS_NOT_IMPLEMENTED(ins)

    def instruction_jr(self, ins: 'LoadedInstruction'):
        INS_NOT_IMPLEMENTED(ins)

    def instruction_jal(self, ins: 'LoadedInstruction'):
        reg = 'ra'  # default register is ra
        if len(ins.args) == 1:
            addr = ins.get_imm(0)
        else:
            ASSERT_LEN(ins.args, 2)
            reg = ins.get_reg(0)
            addr = ins.get_imm(1)
        self.regs.set(reg, self.pc)
        self.pc = addr

    def instruction_jalr(self, ins: 'LoadedInstruction'):
        ASSERT_LEN(ins.args, 2)
        reg = ins.get_reg(0)
        addr = ins.get_imm(1)
        self.regs.set(reg, self.pc)
        self.pc = addr

    def instruction_ret(self, ins: 'LoadedInstruction'):
        ASSERT_LEN(ins.args, 0)
        self.pc = self.regs.get('ra')

    def instruction_ecall(self, ins: 'LoadedInstruction'):
        self.instruction_scall(ins)

    def instruction_ebreak(self, ins: 'LoadedInstruction'):
        self.instruction_ebreak(ins)

    def instruction_scall(self, ins: 'LoadedInstruction'):
        ASSERT_LEN(ins.args, 0)
        syscall = Syscall(self.regs.get('a7'), self.regs)
        self.syscall_int.handle_syscall(syscall)

    def instruction_sbreak(self, ins: 'LoadedInstruction'):
        if self.conf.debug_instruction:
            import code
            code.interact(local=dict(globals(), **locals()))


    def instruction_nop(self, ins: 'LoadedInstruction'):
        pass


    @staticmethod
    def all_instructions():
        for method in vars(CPU):
            if method.startswith('instruction_'):
                yield method[12:]

