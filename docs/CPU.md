# The CPU

The CPU emulates some RISC-V instructions:

  * all loads/stores: `lb, lh, lw, lbu, lhu, sw, sh, sb`
    * supported arg format is either `rd, imm(reg)` or `reg, reg, imm`
  * all branch statements: `beq, bne, blt, bge, bltu, bgeu`
  * all jumps `j, jal, jalr, ret`
  * basic arithmetic: `add, addi, sub` (not `lui, auipc`)
  * shifts: `sll, slli, srl, srli, sra, srai`
  * `scall, ecall, sbreak, ebreak` (both `s` and `e` version are the same instrcution)
  * compares (non immediate): `slt, sltu`, not `slti, sltiu`
  * logiacl (non immediate): `and, or, xor` not (`andi, ori, xori`)
