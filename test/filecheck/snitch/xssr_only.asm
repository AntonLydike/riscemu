// RUN: python3 -m snitch %s -o libc | filecheck %s

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

    // check values were written correctly:
    la t0, vec0
    la t1, vec1
    li a0, 40
loop2:
    add     s0, t0, a0
    add     s1, t1, a0
    // load vec0 element
    flw     ft0, 0(s0)
    // load vec1 element
    flw     ft1, 0(s1)
    // assert ft1 - ft0 == ft0
    fsub.s  ft2, ft1, ft0
    feq.s   s0, ft2, ft0
    beq     zero, s0, fail

    addi a0, a0, -4
    bne  a0, zero, loop2

    ret

fail:
    printf "failed {} != {} (at {})", ft0, ft1, a0
    li a0, -1
    ret

// CHECK: [CPU] Program exited with code 0
