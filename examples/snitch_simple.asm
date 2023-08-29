.data

vec0:
.word 0x0, 0x3f800000, 0x40000000, 0x40400000, 0x40800000, 0x40a00000, 0x40c00000, 0x40e00000, 0x41000000, 0x41100000
vec1:
.word 0x0, 0x3f800000, 0x40000000, 0x40400000, 0x40800000, 0x40a00000, 0x40c00000, 0x40e00000, 0x41000000, 0x41100000
dest:
.space 40

.text
.globl main

main:
    // ssr config
    ssr.configure   0, 10, 4
    ssr.configure   1, 10, 4
    ssr.configure   2, 10, 4

    la              a0, vec0
    ssr.read        a0, 0, 0

    la              a0, vec1
    ssr.read        a0, 1, 0

    la              a0, dest
    ssr.write       a0, 2, 0

    ssr.enable

    // set up loop
    li a0, 10
loop:
    fadd.s      ft2, ft0, ft1

    addi a0, a0, -1
    bne  a0, zero, loop

    // end of loop:
    ssr.disable

    ret
