// RUN: python3 -m riscemu -v %s -o libc | filecheck %s

.data

data:
.byte       0x11, 0x22, 0x33, 0x44, 0x55, 0x66, 0x77, 0x88
.byte       0x99, 0xAA, 0xBB, 0xCC, 0xDD, 0xEE, 0xFF, 0x00

dest:
.byte       0xAB, 0xAB, 0xAB, 0xAB, 0xAB, 0xAB, 0xAB, 0xAB
.byte       0xAB, 0xAB, 0xAB, 0xAB, 0xAB, 0xAB, 0xAB, 0xAB

small_str:
.string     "test"

.text

.globl      main
main:
// test that strlen(data) == 15
        addi    sp, sp, -4
        sw      ra, 0(sp)
        la      a0, data
        // call strlen(data)
        jal     strlen
        li      t0, 15
        bne     a0, t0, _fail

// now memcpy strlen(data)+1 bytes from data to dest
        la      a0, dest
        la      a1, data
        li      a2, 16
        // call strncpy(dest, data, 16)
        jal     strncpy
        la      a1, dest
        // fail because strncpy should return pointer to dest
        bne     a0, a1, _fail
        // check that dest and data are the same
        jal     check_data_dest_is_same
        la      a0, dest
        li      a1, 0x11
        li      a2, 16
// test that memset(dest) workds
        // call memset(dest, 0x11, 16)
        jal     memset
        // check that all of dest is 0x11111111
        li      t1, 0x11111111
        la      a0, dest
        lw      t0, 0(a0)
        bne     t0, t1, _fail
        lw      t0, 1(a0)
        bne     t0, t1, _fail
        lw      t0, 2(a0)
        bne     t0, t1, _fail
        lw      t0, 3(a0)
        bne     t0, t1, _fail
// test memchr
        // test memchr
        la      a0, data
        li      a1, 0x55
        li      a2, 16
        // memchr(data, 0x55, 16)
        jal     memchr
        la      t0, data
        addi    t0, t0, 4
        // fail if a0 != data+4
        bne     a0, t0, _fail
        la      a0, data
        li      a1, 0x12
        li      a2, 16
        // memchr(data, 0x12, 16)
        jal     memchr
        // check that result is NULL
        bne     a0, zero, _fail
// test strcpy
        la      a0, dest
        la      a1, small_str
        // call strcpy(dest, small_str)
        jal     strcpy
        la      t0, dest
        lw      t1, 0(a0)
        // ascii for "tset", as risc-v is little endian
        li      t2, 0x74736574
        bne     t1, t2, _fail

// return to exit() wrapper
        lw      ra, 0(sp)
        addi    sp, sp, 4
        li      a0, 0
        ret

_fail:
        ebreak
        // fail the test run
        li      a0, -1
        jal     exit


check_data_dest_is_same:
        la      a0, data
        la      a1, dest
        li      a2, 4
1:
        lw      t0, 0(a0)
        lw      t1, 0(a1)
        bne     t0, t1, _fail
        addi    a0, a0, 4
        addi    a1, a1, 4
        addi    a2, a2, -1
        blt     zero, a2, 1b
        ret


//CHECK: [CPU] Program exited with code 0
