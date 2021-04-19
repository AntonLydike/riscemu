# Assembly

Assembly tokenization should be working completely. It knows what instructions the CPU implementation supports and parses based on them.


## Instruction sets:
* RV32I
    * Loads/Stores: `lb, lh, lw, lbu, lhu, sw, sh, sb` (supported arg format is either `rd, imm(reg)` or `rd, reg, imm`)
    * Branch statements: `beq, bne, blt, bge, bltu, bgeu`
    * Jumps `j, jal, jalr, ret`
    * Basic arithmetic: `add, addi, sub, lui, auipc`
    * Shifts: `sll, slli, srl, srli, sra, srai`
    * Syscall/Debugging:`scall, ecall, sbreak, ebreak` (both `s` and `e` version are the same instruction)
    * Compares: `slt, sltu, slti, sltiu`
    * Logical: `and, or, xor, andi, ori, xori`
    * Not implemented: `fence, fence.i, rdcycle, rdcycleh, rdtime, rdtimeh, rdinstret, rdinstreth`
* RV32M
    * Multiplication: `mul, mulh`, not implemented yet are `mulhsu, mulhu`
    * Division: `div, divu, rem, remu`



## Pseudo-ops
The following pseudo-ops are implemented as of yet:
* `.space <len>` reverse <len> bytes of zero
* `.ascii 'text'` put text into memory
* `.asciiz 'text'` put text into memory (null terminated)
* `.section .<name>` same as `.<name>`, see sections
* `.set <name>, <value>` to create a const symbol with a given value
* `.global <name>` mark symbol `<name>` as a global symbol. It is available from all loaded programs
* `.align <bytes>` currently a nop as cpu does not care about alignment as of now

## Sections: 
Currently only these three sections are supported: 
* `data` read-write data (non-executable)
* `rodata` read-only data (non-executable)
* `text` executable data (read-only)


## Allocating stack
another pseudo-op is recognized: `.stack <len>`. This marks the executable as requesting at least `<len>` bytes of stack. 
If the loader respects this wish, the sp is initialized pointing to the end of the stack.

 