// example of a simple memory allocation
// we use the mmap2 syscall for this

.text
        // call mmap2
        li  a0, 0       // addr = 0, let OS choose address
        li  a1, 4096    // size
        li  a2, 3       // PROT_READ   | PROT_WRITE
        li  a3, 5       // MAP_PRIVATE | MAP_ANONYMOUS
        li  a7, SCALL_MMAP2
        ecall           // invoke syscall

        li  t0, -1      // exit if unsuccessful
        beq a0, t0, _exit

        // print address
        print.uhex a0
        # we can look at the state of the mmu here:
        ebreak
        # > mmu.sections
        # InstructionMemorySection[.text] at 0x00000100
        # BinaryDataMemorySection[.stack] at 0x00000170
        # BinaryDataMemorySection[.data.runtime-allocated] at 0x00080170

        sw  t0, 144(a0)
        sw  t0, 0(a0)
        sw  t0, 8(a0)
        sw  t0, 16(a0)
        sw  t0, 32(a0)
        sw  t0, 64(a0)
        sw  t0, 128(a0)
        sw  t0, 256(a0)
        sw  t0, 512(a0)
        sw  t0, 1024(a0)
        sw  t0, 2048(a0)
        sw  t0, 4000(a0)

        lw  t1, 128(a0)
        print.uhex t0
        ebreak

_exit:
        li a7, 93
        ecall
