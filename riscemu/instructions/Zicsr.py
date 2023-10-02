from typing import Tuple

from .instruction_set import InstructionSet, Instruction
from ..core import Int32, UInt32
from ..core.csr_constants import CSR_NAME_TO_ADDR
from ..helpers import parse_numeric_argument


class Zicsr(InstructionSet):
    def instruction_csrrw(self, ins: Instruction):
        rd, new_val, csr = self._parse_csr_ins(ins)
        if rd != "zero":
            self.regs.set(rd, self.cpu.csr.get(csr))
        self.cpu.csr.set(csr, new_val)

    def instruction_csrrwi(self, ins: Instruction):
        rd, new_val, csr = self.parse_csr_imm_ins(ins)
        if rd != "zero":
            self.regs.set(rd, self.cpu.csr.get(csr))
        self.cpu.csr.set(csr, new_val)

    def instruction_csrrs(self, ins: Instruction):
        rd, bitmask, csr = self._parse_csr_ins(ins)
        val = self.cpu.csr.get(csr)
        if rd != "zero":
            self.regs.set(rd, val)
        if bitmask != 0:
            self.cpu.csr.set(csr, val | bitmask)

    def instruction_csrrsi(self, ins: Instruction):
        rd, bitmask, csr = self.parse_csr_imm_ins(ins)
        val = self.cpu.csr.get(csr)
        if rd != "zero":
            self.regs.set(rd, val)
        if bitmask != 0:
            self.cpu.csr.set(csr, val | bitmask)

    def instruction_csrrc(self, ins: Instruction):
        rd, bitmask, csr = self._parse_csr_ins(ins)
        val = self.cpu.csr.get(csr)
        if rd != "zero":
            self.regs.set(rd, val)
        if bitmask != 0:
            self.cpu.csr.set(csr, val & ~bitmask)

    def instruction_csrrci(self, ins: Instruction):
        rd, bitmask, csr = self.parse_csr_imm_ins(ins)
        val = self.cpu.csr.get(csr)
        if rd != "zero":
            self.regs.set(rd, val)
        if bitmask != 0:
            self.cpu.csr.set(csr, val & ~bitmask)

    def instruction_rdtime(self, ins: Instruction):
        rd = ins.get_reg(0)
        self.regs.set(rd, self.cpu.rtclock.get_low32())

    def instruction_rdtimeh(self, ins: Instruction):
        rd = ins.get_reg(0)
        self.regs.set(rd, self.cpu.rtclock.get_hi32())

    # FIXME: rdclycle[h] and rdinstret[h] are not provided yet

    def _parse_csr_ins(self, ins: Instruction) -> Tuple[str, UInt32, int]:
        assert len(ins.args) == 3
        rd = ins.get_reg(0)
        rs = self.regs.get(ins.get_reg(1)).unsigned()

        return rd, rs, self._ins_get_csr_addr(ins)

    def parse_csr_imm_ins(self, ins: Instruction) -> Tuple[str, UInt32, int]:
        assert len(ins.args) == 3
        rd = ins.get_reg(0)
        # make sure we only have 5 bit immediate values here
        rs = ins.get_imm(1).abs_value.unsigned()
        if rs > 0b11111:
            print(f"Warning! more than 5bit immediate value in csr ins {ins}!")
            rs = rs & 0b11111

        return rd, rs, self._ins_get_csr_addr(ins)

    @staticmethod
    def _ins_get_csr_addr(ins: Instruction) -> int:
        # TODO: somehow handle elf instructions at some point?
        if isinstance(ins.args[2], str) and ins.args[2].lower() in CSR_NAME_TO_ADDR:
            return CSR_NAME_TO_ADDR[ins.args[2].lower()]

        return ins.get_imm(2).abs_value.unsigned_value
