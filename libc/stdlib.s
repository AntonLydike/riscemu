// A very basic implementation of a stdlib.h but in assembly.
// should(tm) work with riscemu.
//
// Copyright (c) 2023 Anton Lydike
// SPDX-License-Identifier: MIT

.data

_rand_seed:
.word   0x76767676
_atexit_calls:
// leave room for 8 atexit handlers here for now
.word   0x00, 0x00, 0x00, 0x00
.word   0x00, 0x00, 0x00, 0x00
_atexit_count:
.word   0x00

_malloc_base_ptr:
// first word is a pointer to some space
// second word is the offset inside that space
// space is always MALLOC_PAGE_SIZE bytes
.word   0x00, 0x00
.equ    MALLOC_PAGE_SIZE 4069

.text

// malloc/free

.globl malloc
.globl free

// malloc(size_t size)
malloc:
        // set aside size in s0
        sw  s0, -4(sp)
        mv  a0, s0
        la  t0, _malloc_base_ptr
        lw  t1, 0(t0)
        beq t1, zero, _malloc_init
_malloc_post_init:
        // if we are here, we always have
        // t0 = (&_malloc_base_ptr)
        // t1 = *(&_malloc_base_ptr)
        // new we load
        // t2 = base_ptr_offset
        lw  t2, 4(t0)
        // add allocated size to offset
        add t2, t2, s0
        // check for overflow
        li  t4, MALLOC_PAGE_SIZE
        bge t2, t4, _malloc_fail
        // save the new offset
        sw  t2, 4(t0)
        // calculate base_ptr + offset
        add a0, t2, t1
        // return that
        lw  s0, -4(sp)
        ret

_malloc_init:
        // call mmap2()
        li  a0, 0       // addr = 0, let OS choose address
        li  a1, 4096    // size
        li  a2, 3       // PROT_READ   | PROT_WRITE
        li  a3, 5       // MAP_PRIVATE | MAP_ANONYMOUS
        li  a7, SCALL_MMAP2
        ecall           // invoke syscall
        // check for error code
        li  t0, -1
        beq a0, t0, _malloc_fail
        // if succeeded, load &_malloc_base_ptr
        la  t0, _malloc_base_ptr
        // put value of _malloc_base_ptr into t1
        mv  a0, t1
        // save base ptr to _malloc_base_ptr
        sw  t1, 0(t0)
        // jump to post_init
        j   _malloc_post_init
_malloc_fail:
        li a0, 0
        ret

// free is a nop, that's valid, but not very good^^
free:
        ret



// exit, atexit
.globl exit
.globl atexit

// we can happily use saved registers here because we don't care at all if we
// destroy the calling registers. This is __noreturn__ anyways!
// register layout:
// s0 = &_atexit_count
// s2 = &_atexit_calls
// s1 = updated value of atexit
// s3 = exit code
exit:
        // save exit code to s3
        mv      s3, a0
_exit_start:
        la      s0, _atexit_count       // s0 = &_atexit_count
        lw      s1, 0(s0)               // s1 = *(&_atexit_count)
        // exit if no atexit() calls remain
        beq     s1, zero, _exit
        // decrement
        addi    s1, s1, -4              // s1--
        // save decremented value
        sw      s1, 0(s0)               // _atexit_count = s1
        li      s2, _atexit_calls
        add     s1, s1, s2              // s1 = &_atexit_calls + (s1)
        lw      s1, 0(s1)               // s1 = *s1
        la      ra, _exit_start         // set ra up to point to exit
        jalr    zero, s1, 0             // jump to address in s1
        // jalr will call the other function, which will then return back
        // to the beginning of exit.
_exit:
        mv      a0, s3
        li      a7, 93
        ecall

// atexit a0 = funcptr
atexit:
        sw      t0, -4(sp)
        sw      t2, -8(sp)
        // load _atexit_count
        la      t0, _atexit_count
        lw      t2, 0(t0)
        // if >= 8, fail
        li      t1, 8
        bge     t2, t1, _atexit_fail
        // increment atexit_count by 4 (one word)
        addi    t2, t2, 4
        sw      t2, 0(t0)
        // load address of _atexit_calls
        la      t0, _atexit_calls
        // add new _atexit_count to _atexit_calls
        add     t0, t0, t2
        sw      a0, -4(t0)
        li      a0, 0
        lw      t0, -4(sp)
        lw      t2, -8(sp)
        ret

_atexit_fail:
        li      a0, -1
        lw      s0, -4(sp)
        lw      s1, -8(sp)
        ret






// rand, srand

.globl  rand
.globl  srand

// simple xorshift rand implementation
rand:
        // load seed
        la  t1, _rand_seed
        lw  a0, 0(t1)
        // three rounds of shifts:
        sll a0, t0, 13          // x ^= x << 13;
        srl a0, t0, 17          // x ^= x >> 17;
        sll a0, t0, 5           // x ^= x << 5;
	    sw  a0, 0(t1)
	    ret

srand:
        la  t1, _rand_seed
        sw  a0, 0(t1)
        ret
