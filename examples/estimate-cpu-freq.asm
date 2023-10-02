.data
// 16 words of data for benchmarking loads/stores
buf0:
    .word   1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16

.text
.globl main

main:
    mv      s5, ra

    // warmup
    printf  "warmup"
    li      a0, 1000
    jal     nop_loop

    la      a1, nop_loop
    li      a0, 1000
    printf  "Measuring nops:"
    jal measure_loop
    li      a0, 10000
    jal measure_loop

    la      a1, arith_loop
    li      a0, 1000
    printf  "Measuring addi:"
    jal measure_loop
    li      a0, 10000
    jal measure_loop

    la      a1, memory_loop
    la      a2, buf0
    li      a0, 1000
    printf  "Measuring load/stores:"
    jal measure_loop
    li      a0, 10000
    jal measure_loop

    mv      ra, s5
    ret


// rtclock tickrate is 32768
// execute bench at addr a1, a0 times
measure_loop:
    mv      s4, ra
    csrrs   s0, zero, cycle
    csrrs   s2, zero, time
    jalr    ra, a1, 0
    csrrs   s1, zero, cycle
    csrrs   s3, zero, time
    sub     s0, s1, s0
    sub     s1, s3, s2
    fcvt.s.w ft0, s1
    li      t1, 32768       // cpu tickrate
    fcvt.s.w ft1, t1
    fdiv.s  ft0, ft0, ft1   // ft0 = seconds of execution time
    fcvt.s.w ft1, s0        // ft1 = number of ins executed
    fdiv.s  ft2, ft1, ft0   // ft2 = ins/second
    li      t0, 1000
    fcvt.s.w ft1, t0        // ft1 = 1k
    fdiv.s  ft2, ft2, ft1   // ft2 = kins/sec

    printf  "executed {} instructions in {:.4f} seconds ({:.2f}ki/s)", s0, ft0, ft2
    mv      ra, s4
    ret

// first loop, executes a0*32 nop + a0 addi + a0 beq instructions (a0 > 1)
nop_loop:
    nop
    nop
    nop
    nop
    nop
    nop
    nop
    nop
    nop
    nop
    nop
    nop
    nop
    nop
    nop
    nop
    nop
    nop
    nop
    nop
    nop
    nop
    nop
    nop
    nop
    nop
    nop
    nop
    nop
    nop
    nop
    nop
    addi    a0, a0, -1
    blt     zero, a0, nop_loop
    ret

// second loop, executes a0*16 load/store pairs + a0 addi + a0 beq instructions (a0 > 1)
memory_loop:
    lw      t0, 0(a2)
    sw      t0, 0(a2)
    lw      t0, 4(a2)
    sw      t0, 4(a2)
    lw      t0, 8(a2)
    sw      t0, 8(a2)
    lw      t0, 12(a2)
    sw      t0, 12(a2)
    lw      t0, 16(a2)
    sw      t0, 16(a2)
    lw      t0, 20(a2)
    sw      t0, 20(a2)
    lw      t0, 24(a2)
    sw      t0, 24(a2)
    lw      t0, 28(a2)
    sw      t0, 28(a2)
    lw      t0, 32(a2)
    sw      t0, 32(a2)
    lw      t0, 36(a2)
    sw      t0, 36(a2)
    lw      t0, 40(a2)
    sw      t0, 40(a2)
    lw      t0, 44(a2)
    sw      t0, 44(a2)
    lw      t0, 48(a2)
    sw      t0, 48(a2)
    lw      t0, 52(a2)
    sw      t0, 52(a2)
    lw      t0, 56(a2)
    sw      t0, 56(a2)
    lw      t0, 60(a2)
    sw      t0, 60(a2)
    addi    a0, a0, -1
    bge     a0, zero, nop_loop
    ret

// third loop, executes a0*32 addi + a0 addi + a0 beq instructions (a0 > 1)
arith_loop:
    addi    t0, a0, 1234
    addi    t0, a0, 1234
    addi    t0, a0, 1234
    addi    t0, a0, 1234
    addi    t0, a0, 1234
    addi    t0, a0, 1234
    addi    t0, a0, 1234
    addi    t0, a0, 1234
    addi    t0, a0, 1234
    addi    t0, a0, 1234
    addi    t0, a0, 1234
    addi    t0, a0, 1234
    addi    t0, a0, 1234
    addi    t0, a0, 1234
    addi    t0, a0, 1234
    addi    t0, a0, 1234
    addi    t0, a0, 1234
    addi    t0, a0, 1234
    addi    t0, a0, 1234
    addi    t0, a0, 1234
    addi    t0, a0, 1234
    addi    t0, a0, 1234
    addi    t0, a0, 1234
    addi    t0, a0, 1234
    addi    t0, a0, 1234
    addi    t0, a0, 1234
    addi    t0, a0, 1234
    addi    t0, a0, 1234
    addi    t0, a0, 1234
    addi    t0, a0, 1234
    addi    t0, a0, 1234
    addi    t0, a0, 1234
    addi    a0, a0, -1
    blt     zero, a0, nop_loop
    ret
