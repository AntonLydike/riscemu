# RISC-V (userspace) emulator in python

Implementing a basic RISC-V emulator, aimed at being easily extendable.

Currently supported (but not implemented) instructions:

````
lb, lh, lw, lbu, lhu, sb, sh, sw, sll, slli, srl, srli, sra, 
srai, add, addi, sub, lui, auipc, xor, xori, or, ori, and, 
andi, slt, slti, sltu, sltiu, beq, bne, blt, bge, bltu, bgeu, 
j, jr, jal, jalr, ret, scall, break, nop
````

See the docs on [asembly](docs/assembly.md) and [the cpu](docs/CPU.md) for more detail.

Currently, symbols (such as `main:`) are looked-up in runtime. This allows for better debugging, I believe.

Basic IO should work, as open, read, write and close are supported for stdin/stdout/stderr and even aribtrary file paths (if enabled)

## Resources:
  * Pseudo ops: https://www.codetd.com/article/8981522
  * RISC-V reference card: https://www.cl.cam.ac.uk/teaching/1617/ECAD+Arch/files/docs/RISCVGreenCardv8-20151013.pdf
  
## TODO:
 * add global symbol lookup table
 * better pseudo-ops
 * mmu inspect methods
 
