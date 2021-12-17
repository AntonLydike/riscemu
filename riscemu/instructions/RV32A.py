from .InstructionSet import InstructionSet, LoadedInstruction
from ..exceptions import INS_NOT_IMPLEMENTED
from ..helpers import int_from_bytes, int_to_bytes, to_unsigned, to_signed


class RV32A(InstructionSet):
    """
    The RV32A instruction set. Currently, load-reserved and store conditionally are not supported
    due to limitations in the way the MMU is implemented. Maybe a later implementation will add support
    for this?
    """

    def instruction_lr_w(self, ins: 'LoadedInstruction'):
        INS_NOT_IMPLEMENTED(ins)

    def instruction_sc_w(self, ins: 'LoadedInstruction'):
        INS_NOT_IMPLEMENTED(ins)

    def instruction_amoswap_w(self, ins: 'LoadedInstruction'):
        dest, addr, val = self.parse_rd_rs_rs(ins)
        if dest == 'zero':
            self.mmu.write(addr, int_to_bytes(addr, 4))
        else:
            old = int_from_bytes(self.mmu.read(addr, 4))
            self.mmu.write(addr, int_to_bytes(val, 4))
            self.regs.set(dest, old)

    def instruction_amoadd_w(self, ins: 'LoadedInstruction'):
        dest, addr, val = self.parse_rd_rs_rs(ins)
        old = int_from_bytes(self.mmu.read(addr, 4))
        self.mmu.write(addr, int_to_bytes(old + val, 4))
        self.regs.set(dest, old)

    def instruction_amoand_w(self, ins: 'LoadedInstruction'):
        dest, addr, val = self.parse_rd_rs_rs(ins)
        old = int_from_bytes(self.mmu.read(addr, 4))
        self.mmu.write(addr, int_to_bytes(old & val, 4))
        self.regs.set(dest, old)

    def instruction_amoor_w(self, ins: 'LoadedInstruction'):
        dest, addr, val = self.parse_rd_rs_rs(ins)
        old = int_from_bytes(self.mmu.read(addr, 4))
        self.mmu.write(addr, int_to_bytes(old | val, 4))
        self.regs.set(dest, old)

    def instruction_amoxor_w(self, ins: 'LoadedInstruction'):
        dest, addr, val = self.parse_rd_rs_rs(ins)
        old = int_from_bytes(self.mmu.read(addr, 4))
        self.mmu.write(addr, int_to_bytes(old ^ val, 4))
        self.regs.set(dest, old)

    def instruction_amomax_w(self, ins: 'LoadedInstruction'):
        dest, addr, val = self.parse_rd_rs_rs(ins)
        old = int_from_bytes(self.mmu.read(addr, 4))
        self.mmu.write(addr, int_to_bytes(max(old, val), 4))
        self.regs.set(dest, old)

    def instruction_amomaxu_w(self, ins: 'LoadedInstruction'):
        dest, addr, val = self.parse_rd_rs_rs(ins)
        val = to_unsigned(val)
        old = int_from_bytes(self.mmu.read(addr, 4), unsigned=True)

        self.mmu.write(addr, int_to_bytes(to_signed(max(old, val)), 4))
        self.regs.set(dest, old)

    def instruction_amomin_w(self, ins: 'LoadedInstruction'):
        dest, addr, val = self.parse_rd_rs_rs(ins)
        old = int_from_bytes(self.mmu.read(addr, 4))
        self.mmu.write(addr, int_to_bytes(min(old, val), 4))
        self.regs.set(dest, old)

    def instruction_amominu_w(self, ins: 'LoadedInstruction'):
        dest, addr, val = self.parse_rd_rs_rs(ins)
        val = to_unsigned(val)
        old = int_from_bytes(self.mmu.read(addr, 4), unsigned=True)

        self.mmu.write(addr, int_to_bytes(to_signed(min(old, val)), 4))
        self.regs.set(dest, old)
