"""
RiscEmu (c) 2021 Anton Lydike

SPDX-License-Identifier: MIT
"""

from ..instructions.RV32I import *
from ..Exceptions import INS_NOT_IMPLEMENTED
from .Exceptions import *
from .privmodes import PrivModes
from ..colors import FMT_CPU, FMT_NONE
import typing

if typing.TYPE_CHECKING:
    from riscemu.priv.PrivCPU import PrivCPU


class PrivRV32I(RV32I):
    cpu: 'PrivCPU'
    """
    This is an extension of RV32I, written for the PrivCPU class
    """

    def instruction_csrrw(self, ins: 'LoadedInstruction'):
        rd, rs, csr_addr = self.parse_crs_ins(ins)
        old_val = None
        if rd != 'zero':
            self.cpu.csr.assert_can_read(self.cpu.mode, csr_addr)
            old_val = self.cpu.csr.get(csr_addr)
        if rs != 'zero':
            new_val = self.regs.get(rs)
            self.cpu.csr.assert_can_write(self.cpu.mode, csr_addr)
            self.cpu.csr.set(csr_addr, new_val)
        if old_val is not None:
            self.regs.set(rd, old_val)

    def instruction_csrrs(self, ins: 'LoadedInstruction'):
        rd, rs, csr_addr = self.parse_crs_ins(ins)
        if rs != 'zero':
            # oh no, this should not happen!
            INS_NOT_IMPLEMENTED(ins)
        if rd != 'zero':
            self.cpu.csr.assert_can_read(self.cpu.mode, csr_addr)
            old_val = self.cpu.csr.get(csr_addr)
            self.regs.set(rd, old_val)


    def instruction_csrrc(self, ins: 'LoadedInstruction'):
        INS_NOT_IMPLEMENTED(ins)

    def instruction_csrrsi(self, ins: 'LoadedInstruction'):
        INS_NOT_IMPLEMENTED(ins)

    def instruction_csrrwi(self, ins: 'LoadedInstruction'):
        ASSERT_LEN(ins.args, 3)
        rd, imm, addr = ins.get_reg(0), ins.get_imm(1), ins.get_imm(2)
        if rd != 'zero':
            self.cpu.csr.assert_can_read(self.cpu.mode, addr)
            old_val = self.cpu.csr.get(addr)
            self.regs.set(rd, old_val)
        self.cpu.csr.assert_can_write(self.cpu.mode, addr)
        self.cpu.csr.set(addr, imm)


    def instruction_csrrci(self, ins: 'LoadedInstruction'):
        INS_NOT_IMPLEMENTED(ins)

    def instruction_mret(self, ins: 'LoadedInstruction'):
        if self.cpu.mode != PrivModes.MACHINE:
            print("MRET not inside machine level code!")
            raise IllegalInstructionTrap(ins)
        # retore mie
        mpie = self.cpu.csr.get_mstatus('mpie')
        self.cpu.csr.set_mstatus('mie', mpie)
        # restore priv
        mpp = self.cpu.csr.get_mstatus('mpp')
        self.cpu.mode = PrivModes(mpp)
        # restore pc
        mepc = self.cpu.csr.get('mepc')
        self.cpu.pc = mepc

        sec = self.mmu.get_sec_containing(mepc)
        if sec is not None:
            print(FMT_CPU + "[CPU] [{}] returning to mode: {} in binary {}, section {}, addr 0x{:x}".format(
                self.cpu.cycle,
                PrivModes(mpp),
                sec.owner,
                sec.name,
                mepc
            ) + FMT_NONE)

    def instruction_uret(self, ins: 'LoadedInstruction'):
        raise IllegalInstructionTrap(ins)

    def instruction_sret(self, ins: 'LoadedInstruction'):
        raise IllegalInstructionTrap(ins)

    def instruction_scall(self, ins: 'LoadedInstruction'):
        """
        Overwrite the scall from userspace RV32I
        """
        raise EcallTrap(self.cpu.mode)

    def instruction_beq(self, ins: 'LoadedInstruction'):
        rs1, rs2, dst = self.parse_rs_rs_imm(ins)
        if rs1 == rs2:
            self.pc += dst - 4

    def instruction_bne(self, ins: 'LoadedInstruction'):
        rs1, rs2, dst = self.parse_rs_rs_imm(ins)
        if rs1 != rs2:
            self.pc += dst - 4

    def instruction_blt(self, ins: 'LoadedInstruction'):
        rs1, rs2, dst = self.parse_rs_rs_imm(ins)
        if rs1 < rs2:
            self.pc += dst - 4

    def instruction_bge(self, ins: 'LoadedInstruction'):
        rs1, rs2, dst = self.parse_rs_rs_imm(ins)
        if rs1 >= rs2:
            self.pc += dst - 4

    def instruction_bltu(self, ins: 'LoadedInstruction'):
        rs1, rs2, dst = self.parse_rs_rs_imm(ins, signed=False)
        if rs1 < rs2:
            self.pc += dst - 4

    def instruction_bgeu(self, ins: 'LoadedInstruction'):
        rs1, rs2, dst = self.parse_rs_rs_imm(ins, signed=False)
        if rs1 >= rs2:
            self.pc += dst - 4

    # technically deprecated
    def instruction_j(self, ins: 'LoadedInstruction'):
        raise NotImplementedError("Should never be reached!")

    def instruction_jal(self, ins: 'LoadedInstruction'):
        ASSERT_LEN(ins.args, 2)
        reg = ins.get_reg(0)
        addr = ins.get_imm(1)
        self.regs.set(reg, self.pc)
        self.pc += addr - 4

    def instruction_jalr(self, ins: 'LoadedInstruction'):
        ASSERT_LEN(ins.args, 3)
        rd, rs, imm = self.parse_rd_rs_imm(ins)
        self.regs.set(rd, self.pc)
        self.pc = rs + imm - 4

    def instruction_sbreak(self, ins: 'LoadedInstruction'):
        raise LaunchDebuggerException()

    def parse_crs_ins(self, ins: 'LoadedInstruction'):
        ASSERT_LEN(ins.args, 3)
        return ins.get_reg(0), ins.get_reg(1), ins.get_imm(2)

    def parse_mem_ins(self, ins: 'LoadedInstruction') -> Tuple[str, int]:
        ASSERT_LEN(ins.args, 3)
        addr = self.get_reg_content(ins, 1) + ins.get_imm(2)
        reg = ins.get_reg(0)
        return reg, addr
