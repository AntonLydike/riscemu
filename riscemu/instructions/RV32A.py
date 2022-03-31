from .instruction_set import InstructionSet, Instruction
from riscemu.types.exceptions import INS_NOT_IMPLEMENTED
from ..types import Int32, UInt32


class RV32A(InstructionSet):
    """
    The RV32A instruction set. Currently, load-reserved and store conditionally are not supported
    due to limitations in the way the MMU is implemented. Maybe a later implementation will add support
    for this?
    """

    def instruction_lr_w(self, ins: 'Instruction'):
        INS_NOT_IMPLEMENTED(ins)

    def instruction_sc_w(self, ins: 'Instruction'):
        INS_NOT_IMPLEMENTED(ins)

    def instruction_amoswap_w(self, ins: 'Instruction'):
        dest, addr, val = self.parse_rd_rs_rs(ins)
        if dest == 'zero':
            self.mmu.write(addr, val.to_bytes())
        else:
            old = Int32(self.mmu.read(addr, 4))
            self.mmu.write(addr, val.to_bytes())
            self.regs.set(dest, old)

    def instruction_amoadd_w(self, ins: 'Instruction'):
        dest, addr, val = self.parse_rd_rs_rs(ins)
        old = Int32(self.mmu.read(addr, 4))
        self.mmu.write(addr, (old + val).to_bytes(4))
        self.regs.set(dest, old)

    def instruction_amoand_w(self, ins: 'Instruction'):
        dest, addr, val = self.parse_rd_rs_rs(ins)
        old = Int32(self.mmu.read(addr, 4))
        self.mmu.write(addr, (old & val).to_bytes(4))
        self.regs.set(dest, old)

    def instruction_amoor_w(self, ins: 'Instruction'):
        dest, addr, val = self.parse_rd_rs_rs(ins)
        old = Int32(self.mmu.read(addr, 4))
        self.mmu.write(addr, (old | val).to_bytes(4))
        self.regs.set(dest, old)

    def instruction_amoxor_w(self, ins: 'Instruction'):
        dest, addr, val = self.parse_rd_rs_rs(ins)
        old = Int32(self.mmu.read(addr, 4))
        self.mmu.write(addr, (old ^ val).to_bytes(4))
        self.regs.set(dest, old)

    def instruction_amomax_w(self, ins: 'Instruction'):
        dest, addr, val = self.parse_rd_rs_rs(ins)
        old = Int32(self.mmu.read(addr, 4))
        self.mmu.write(addr, max(old, val).to_bytes(4))
        self.regs.set(dest, old)

    def instruction_amomaxu_w(self, ins: 'Instruction'):
        val: UInt32
        dest, addr, val = self.parse_rd_rs_rs(ins, signed=False)
        old = UInt32(self.mmu.read(addr, 4))

        self.mmu.write(addr, max(old, val).to_bytes())
        self.regs.set(dest, old)

    def instruction_amomin_w(self, ins: 'Instruction'):
        dest, addr, val = self.parse_rd_rs_rs(ins)
        old = Int32(self.mmu.read(addr, 4))
        self.mmu.write(addr, min(old, val).to_bytes(4))
        self.regs.set(dest, old)

    def instruction_amominu_w(self, ins: 'Instruction'):
        val: UInt32
        dest, addr, val = self.parse_rd_rs_rs(ins, signed=False)
        old = UInt32(self.mmu.read(addr, 4))

        self.mmu.write(addr, min(old, val).to_bytes(4))
        self.regs.set(dest, old)
