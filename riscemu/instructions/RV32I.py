"""
RiscEmu (c) 2021 Anton Lydike

SPDX-License-Identifier: MIT
"""

from .instruction_set import InstructionSet, ASSERT_LEN

from ..colors import FMT_DEBUG, FMT_NONE
from ..syscall import Syscall
from ..core import Instruction, Int32, UInt32, UserModeCPU, LaunchDebuggerException


class RV32I(InstructionSet):
    """
    The RV32I instruction set. Some instructions are missing, such as
    fence, fence.i, rdcycle, rdcycleh, rdtime, rdtimeh, rdinstret, rdinstreth
    All atomic read/writes are also not implemented yet

    See https://maxvytech.com/images/RV32I-11-2018.pdf for a more detailed overview
    """

    def instruction_lb(self, ins: "Instruction"):
        rd, addr = self.parse_mem_ins(ins)
        self.regs.set(rd, UInt32.sign_extend(self.mmu.read(addr.unsigned_value, 1), 8))

    def instruction_lh(self, ins: "Instruction"):
        rd, addr = self.parse_mem_ins(ins)
        self.regs.set(rd, UInt32.sign_extend(self.mmu.read(addr.unsigned_value, 2), 16))

    def instruction_lw(self, ins: "Instruction"):
        rd, addr = self.parse_mem_ins(ins)
        self.regs.set(rd, UInt32(self.mmu.read(addr.unsigned_value, 4)))

    def instruction_lbu(self, ins: "Instruction"):
        rd, addr = self.parse_mem_ins(ins)
        self.regs.set(rd, UInt32(self.mmu.read(addr.unsigned_value, 1)))

    def instruction_lhu(self, ins: "Instruction"):
        rd, addr = self.parse_mem_ins(ins)
        self.regs.set(rd, UInt32(self.mmu.read(addr.unsigned_value, 2)))

    def instruction_sb(self, ins: "Instruction"):
        rd, addr = self.parse_mem_ins(ins)
        self.mmu.write(addr.unsigned_value, 1, self.regs.get(rd).to_bytes(1))

    def instruction_sh(self, ins: "Instruction"):
        rd, addr = self.parse_mem_ins(ins)
        self.mmu.write(addr.unsigned_value, 2, self.regs.get(rd).to_bytes(2))

    def instruction_sw(self, ins: "Instruction"):
        rd, addr = self.parse_mem_ins(ins)
        self.mmu.write(addr.unsigned_value, 4, self.regs.get(rd).to_bytes(4))

    def instruction_sll(self, ins: "Instruction"):
        ASSERT_LEN(ins.args, 3)
        dst = ins.get_reg(0)
        src1 = ins.get_reg(1)
        src2 = ins.get_reg(2)
        self.regs.set(dst, self.regs.get(src1) << (self.regs.get(src2) & 0b11111))

    def instruction_slli(self, ins: "Instruction"):
        ASSERT_LEN(ins.args, 3)
        dst = ins.get_reg(0)
        src1 = ins.get_reg(1)
        imm = ins.get_imm(2)
        self.regs.set(dst, self.regs.get(src1) << (imm.abs_value & 0b11111))

    def instruction_srl(self, ins: "Instruction"):
        ASSERT_LEN(ins.args, 3)
        dst = ins.get_reg(0)
        src1 = ins.get_reg(1)
        src2 = ins.get_reg(2)
        self.regs.set(
            dst, self.regs.get(src1).shift_right_logical(self.regs.get(src2) & 0b11111)
        )

    def instruction_srli(self, ins: "Instruction"):
        ASSERT_LEN(ins.args, 3)
        dst = ins.get_reg(0)
        src1 = ins.get_reg(1)
        imm = ins.get_imm(2)
        self.regs.set(
            dst, self.regs.get(src1).shift_right_logical(imm.abs_value & 0b11111)
        )

    def instruction_sra(self, ins: "Instruction"):
        ASSERT_LEN(ins.args, 3)
        dst = ins.get_reg(0)
        src1 = ins.get_reg(1)
        src2 = ins.get_reg(2)
        self.regs.set(dst, self.regs.get(src1) >> (self.regs.get(src2) & 0b11111))

    def instruction_srai(self, ins: "Instruction"):
        ASSERT_LEN(ins.args, 3)
        dst = ins.get_reg(0)
        src1 = ins.get_reg(1)
        imm = ins.get_imm(2)
        self.regs.set(dst, self.regs.get(src1) >> (imm.abs_value & 0b11111))

    def instruction_add(self, ins: "Instruction"):
        dst, rs1, rs2 = self.parse_rd_rs_rs(ins)
        self.regs.set(dst, rs1 + rs2)

    def instruction_addi(self, ins: "Instruction"):
        dst, rs1, imm = self.parse_rd_rs_imm(ins)
        self.regs.set(dst, rs1 + imm.abs_value)

    def instruction_sub(self, ins: "Instruction"):
        dst, rs1, rs2 = self.parse_rd_rs_rs(ins)
        self.regs.set(dst, rs1 - rs2)

    def instruction_lui(self, ins: "Instruction"):
        ASSERT_LEN(ins.args, 2)
        reg = ins.get_reg(0)
        self.regs.set(reg, ins.get_imm(1).abs_value << 12)

    def instruction_auipc(self, ins: "Instruction"):
        ASSERT_LEN(ins.args, 2)
        reg = ins.get_reg(0)
        imm = ins.get_imm(1).abs_value << 12
        self.regs.set(reg, imm + self.cpu.pc)

    def instruction_xor(self, ins: "Instruction"):
        rd, rs1, rs2 = self.parse_rd_rs_rs(ins)
        self.regs.set(rd, rs1 ^ rs2)

    def instruction_xori(self, ins: "Instruction"):
        rd, rs1, imm = self.parse_rd_rs_imm(ins)
        self.regs.set(rd, rs1 ^ imm.abs_value)

    def instruction_or(self, ins: "Instruction"):
        rd, rs1, rs2 = self.parse_rd_rs_rs(ins)
        self.regs.set(rd, rs1 | rs2)

    def instruction_ori(self, ins: "Instruction"):
        rd, rs1, imm = self.parse_rd_rs_imm(ins)
        self.regs.set(rd, rs1 | imm.abs_value)

    def instruction_and(self, ins: "Instruction"):
        rd, rs1, rs2 = self.parse_rd_rs_rs(ins)
        self.regs.set(rd, rs1 & rs2)

    def instruction_andi(self, ins: "Instruction"):
        rd, rs1, imm = self.parse_rd_rs_imm(ins)
        self.regs.set(rd, rs1 & imm.abs_value)

    def instruction_slt(self, ins: "Instruction"):
        rd, rs1, rs2 = self.parse_rd_rs_rs(ins)
        self.regs.set(rd, UInt32(rs1 < rs2))

    def instruction_slti(self, ins: "Instruction"):
        rd, rs1, imm = self.parse_rd_rs_imm(ins)
        self.regs.set(rd, UInt32(rs1 < imm))

    def instruction_sltu(self, ins: "Instruction"):
        dst, rs1, rs2 = self.parse_rd_rs_rs(ins)
        self.regs.set(dst, UInt32(rs1.unsigned_value < rs2.unsigned_value))

    def instruction_sltiu(self, ins: "Instruction"):
        dst, rs1, imm = self.parse_rd_rs_imm(ins)
        self.regs.set(dst, UInt32(rs1.unsigned_value < imm.abs_value.unsigned_value))

    def instruction_beq(self, ins: "Instruction"):
        rs1, rs2, dst = self.parse_rs_rs_imm(ins)
        if rs1 == rs2:
            self.cpu.pc += dst.pcrel_value.value - 4

    def instruction_bne(self, ins: "Instruction"):
        rs1, rs2, dst = self.parse_rs_rs_imm(ins)
        if rs1 != rs2:
            self.cpu.pc += dst.pcrel_value.value - 4

    def instruction_blt(self, ins: "Instruction"):
        rs1, rs2, dst = self.parse_rs_rs_imm(ins)
        if rs1 < rs2:
            self.cpu.pc += dst.pcrel_value.value - 4

    def instruction_bge(self, ins: "Instruction"):
        rs1, rs2, dst = self.parse_rs_rs_imm(ins)
        if rs1 >= rs2:
            self.cpu.pc += dst.pcrel_value.value - 4

    def instruction_bltu(self, ins: "Instruction"):
        rs1, rs2, dst = self.parse_rs_rs_imm(ins)
        if rs1.unsigned_value < rs2.unsigned_value:
            self.cpu.pc += dst.pcrel_value.value - 4

    def instruction_bgeu(self, ins: "Instruction"):
        rs1, rs2, dst = self.parse_rs_rs_imm(ins)
        if rs1.unsigned_value >= rs2.unsigned_value:
            self.cpu.pc += dst.pcrel_value.value - 4

    def instruction_j(self, ins: "Instruction"):
        ASSERT_LEN(ins.args, 1)
        addr = ins.get_imm(0)
        self.cpu.pc += addr.pcrel_value.value - 4

    def instruction_jal(self, ins: "Instruction"):
        reg = "ra"  # default register is ra
        if len(ins.args) == 1:
            addr = ins.get_imm(0)
        else:
            ASSERT_LEN(ins.args, 2)
            reg = ins.get_reg(0)
            addr = ins.get_imm(1)
        self.regs.set(reg, UInt32(self.cpu.pc))
        self.cpu.pc += addr.pcrel_value.value - 4

    def instruction_jalr(self, ins: "Instruction"):
        ASSERT_LEN(ins.args, 3)
        reg = ins.get_reg(0)
        base = ins.get_reg(1)
        addr = ins.get_imm(2).abs_value.value
        self.regs.set(reg, Int32(self.cpu.pc))
        self.cpu.pc = self.regs.get(base).unsigned_value + addr

    def instruction_ret(self, ins: "Instruction"):
        ASSERT_LEN(ins.args, 0)
        self.cpu.pc = self.regs.get("ra").unsigned_value

    def instruction_ecall(self, ins: "Instruction"):
        self.instruction_scall(ins)

    def instruction_ebreak(self, ins: "Instruction"):
        self.instruction_sbreak(ins)

    def instruction_scall(self, ins: "Instruction"):
        ASSERT_LEN(ins.args, 0)

        if not isinstance(self.cpu, UserModeCPU):
            # FIXME: add exception for syscall not supported or something
            raise

        syscall = Syscall(self.regs.get("a7"), self.cpu)
        self.cpu.syscall_int.handle_syscall(syscall)

    def instruction_sbreak(self, ins: "Instruction"):
        ASSERT_LEN(ins.args, 0)
        if self.cpu.conf.debug_instruction:
            print(
                FMT_DEBUG
                + "Debug instruction encountered at 0x{:08X}".format(self.cpu.pc - 1)
                + FMT_NONE
            )
            raise LaunchDebuggerException()

    def instruction_nop(self, ins: "Instruction"):
        ASSERT_LEN(ins.args, 0)
        pass

    def instruction_li(self, ins: "Instruction"):
        ASSERT_LEN(ins.args, 2)
        reg = ins.get_reg(0)
        immediate = ins.get_imm(1).abs_value
        self.regs.set(reg, Int32(immediate))

    def instruction_la(self, ins: "Instruction"):
        ASSERT_LEN(ins.args, 2)
        reg = ins.get_reg(0)
        immediate = ins.get_imm(1).abs_value
        self.regs.set(reg, Int32(immediate))

    def instruction_mv(self, ins: "Instruction"):
        ASSERT_LEN(ins.args, 2)
        rd, rs = ins.get_reg(0), ins.get_reg(1)
        self.regs.set(rd, self.regs.get(rs))
