# RiscV (userspace) emulator in python

Implementing a basic RISC-V emulator, aimed at being easily extendable.

Currently supported (but not implemented) instructions:

````
lb, lh, lw, lbu, lhu, sb, sh, sw, sll, slli, srl, srli, sra, 
srai, add, addi, sub, lui, auipc, xor, xori, or, ori, and, 
andi, slt, slti, sltu, sltiu, beq, bne, blt, bge, bltu, bgeu, 
j, jr, jal, jalr, ret, scall, break, nop
````

Current register implementation (should be all standard userspace registers): 
```
Registers[read,written](
        zero=0x00000000 ra  =0x00000000 sp  =0x00000000 gp  =0x00000000 tp  =0x00000000 fp  =0x00000000
        --------------- --------------- --------------- --------------- --------------- --------------- 
        a0  =0x00000000 s0  =0x00000000 t0  =0x00000000 ft0 =0x00000000 fa0 =0x00000000 fs0 =0x00000000
        a1  =0x00000000 s1  =0x00000000 t1  =0x00000000 ft1 =0x00000000 fa1 =0x00000000 fs1 =0x00000000
        a2  =0x00000000 s2  =0x00000000 t2  =0x00000000 ft2 =0x00000000 fa2 =0x00000000 fs2 =0x00000000
        a3  =0x00000000 s3  =0x00000000 t3  =0x00000000 ft3 =0x00000000 fa3 =0x00000000 fs3 =0x00000000
        a4  =0x00000000 s4  =0x00000000 t4  =0x00000000 ft4 =0x00000000 fa4 =0x00000000 fs4 =0x00000000
        a5  =0x00000000 s5  =0x00000000 t5  =0x00000000 ft5 =0x00000000 fa5 =0x00000000 fs5 =0x00000000
        a6  =0x00000000 s6  =0x00000000 t6  =0x00000000 ft6 =0x00000000 fa6 =0x00000000 fs6 =0x00000000
        a7  =0x00000000 s7  =0x00000000                 ft7 =0x00000000 fa7 =0x00000000 fs7 =0x00000000
                        s8  =0x00000000                                                 fs8 =0x00000000
                        s9  =0x00000000                                                 fs9 =0x00000000
                        s10 =0x00000000                                                 fs10=0x00000000
                        s11 =0x00000000                                                 fs11=0x00000000
)
```

Current pseudo ops:
```
.align, .ascii, .asciiz, .byte, .data, .double, .extern,
.float, .globl, .half, .kdata, .ktext, .set, .space, .text, .word
```

## Resources:
  * Pseudo ops: https://www.codetd.com/article/8981522
  