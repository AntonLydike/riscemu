.text

main:
        addi    a0, zero, main
        addi    a1, zero, main
        addi    t0, zero, 1000
        assert  a0, ==, 0x100
1:
        addi    a1, a1, 1
        blt     a1, t0, 1b
        sub     a1, a1, a0
        j       1f
        addi    a1, zero, 0
        fail
1:
        assert  a1, ==, 744
        add     a0, zero, a1            ; set exit code to a1
        addi    a7, zero, SCALL_EXIT    ; exit syscall code
        scall
        fail