from .instruction_set import InstructionSet, Instruction
from riscemu.core.exceptions import INS_NOT_IMPLEMENTED
from ..core import Int32, UInt32


class RV32A(InstructionSet):
    """
    The RV32A instruction set. Currently, load-reserved and store conditionally are not supported
    due to limitations in the way the MMU is implemented. Maybe a later implementation will add support
    for this?
    """

    def instruction_lr_w(self, ins: "Instruction"):
        INS_NOT_IMPLEMENTED(ins)

    def instruction_sc_w(self, ins: "Instruction"):
        INS_NOT_IMPLEMENTED(ins)

    def instruction_amoswap_w(self, ins: "Instruction"):
        dest, addr, val = self.parse_rd_rs_rs(ins)
        if dest == "zero":
            self.mmu.write(addr.unsigned_value, val.to_bytes())
        else:
            old = Int32(self.mmu.read(addr.unsigned_value, 4))
            self.mmu.write(addr.unsigned_value, val.to_bytes())
            self.regs.set(dest, old)

    def instruction_amoadd_w(self, ins: "Instruction"):
        dest, addr, val = self.parse_rd_rs_rs(ins)
        old = Int32(self.mmu.read(addr.unsigned_value, 4))
        self.mmu.write(addr.unsigned_value, (old + val).to_bytes(4))
        self.regs.set(dest, old)

    def instruction_amoand_w(self, ins: "Instruction"):
        dest, addr, val = self.parse_rd_rs_rs(ins)
        old = Int32(self.mmu.read(addr.unsigned_value, 4))
        self.mmu.write(addr.unsigned_value, (old & val).to_bytes(4))
        self.regs.set(dest, old)

    def instruction_amoor_w(self, ins: "Instruction"):
        dest, addr, val = self.parse_rd_rs_rs(ins)
        old = Int32(self.mmu.read(addr.unsigned_value, 4))
        self.mmu.write(addr.unsigned_value, (old | val).to_bytes(4))
        self.regs.set(dest, old)

    def instruction_amoxor_w(self, ins: "Instruction"):
        dest, addr, val = self.parse_rd_rs_rs(ins)
        old = Int32(self.mmu.read(addr.unsigned_value, 4))
        self.mmu.write(addr.unsigned_value, (old ^ val).to_bytes(4))
        self.regs.set(dest, old)

    def instruction_amomax_w(self, ins: "Instruction"):
        dest, addr, val = self.parse_rd_rs_rs(ins)
        old = Int32(self.mmu.read(addr.unsigned_value, 4))
        self.mmu.write(addr.unsigned_value, max(old, val).to_bytes(4))
        self.regs.set(dest, old)

    def instruction_amomaxu_w(self, ins: "Instruction"):
        val: UInt32
        dest, addr, val = self.parse_rd_rs_rs(ins)
        old = UInt32(self.mmu.read(addr.unsigned_value, 4))

        self.mmu.write(addr.unsigned_value, max(old, val.unsigned()).to_bytes())
        self.regs.set(dest, old)

    def instruction_amomin_w(self, ins: "Instruction"):
        dest, addr, val = self.parse_rd_rs_rs(ins)
        old = Int32(self.mmu.read(addr.unsigned_value, 4))
        self.mmu.write(addr.unsigned_value, min(old, val).to_bytes(4))
        self.regs.set(dest, old)

    def instruction_amominu_w(self, ins: "Instruction"):
        val: UInt32
        dest, addr, val = self.parse_rd_rs_rs(ins)
        old = UInt32(self.mmu.read(addr.unsigned_value, 4))

        self.mmu.write(addr.unsigned_value, min(old, val.unsigned()).to_bytes(4))
        self.regs.set(dest, old)
