// RUN: python3 -m snitch %s -o libc -v --flen 32  | filecheck %s

.data

vec0:
.word 0x0, 0x3f800000, 0x40000000, 0x40400000, 0x40800000, 0x40a00000, 0x40c00000, 0x40e00000, 0x41000000, 0x41100000
vec1:
.word 0x0, 0x3f800000, 0x40000000, 0x40400000, 0x40800000, 0x40a00000, 0x40c00000, 0x40e00000, 0x41000000, 0x41100000
dest:
.space 40
expected:
.word 0x0, 0x3e800000, 0x3f800000, 0x40100000, 0x40800000, 0x40c80000, 0x41100000, 0x41440000, 0x41800000, 0x41a20000

.text
.globl main

main:
    // ssr config
    ssr.configure   0, 10, 4
    ssr.configure   1, 10, 4
    ssr.configure   2, 10, 4

    // ft0 streams from vec0
    la              a0, vec0
    ssr.read        a0, 0, 0

    // ft1 streams from vec1
    la              a0, vec1
    ssr.read        a0, 1, 0

    // ft2 streams to dest
    la              a0, dest
    ssr.write       a0, 2, 0

    li              a0, 9
    // some constant to divide by
    li              t0, 4
    fcvt.s.w        ft3, t0
    ssr.enable

    frep.o          a0, 2, 0, 0
    fmul.s          ft4, ft0, ft1   // ft3 = vec0[i] * vec1[i]
    fdiv.s          ft2, ft4, ft3   // dest[i] = ft3 / 4

    // stop ssr
    ssr.disable

    // check values were written correctly:
    la              t0, dest
    la              t1, expected
    li              a0, 36
loop:
    add             s0, t0, a0
    add             s1, t1, a0

    // load vec0, vec1 and dest elements
    flw             ft0, 0(s0)
    flw             ft1, 0(s1)

    // assert ft0 == ft1  (expected[i] == dest[i])
    feq.s           s0, ft0, ft1
    beq             zero, s0, fail

    addi            a0, a0, -4
    bge             a0, zero loop

    li              a0, 0
    ret

fail:
    printf          "Assertion failure: {} != {} (at {})", ft0, ft1, a0
    li              a0, -1
    ret

// CHECK: [CPU] Program exited with code 0
