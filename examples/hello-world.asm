; hello-world.asm
; print "hello world" to stdout and exit
        .data
msg:    .ascii "Hello world\n"
        .text
        addi    a0, zero, 1             ; print to stdout
        addi    a1, zero, msg           ; load msg address
        addi    a2, zero, 12            ; write 12 bytes
        addi    a7, zero, SCALL_WRITE   ; write syscall code
        scall
        addi    a0, zero, 0             ; set exit code to 0
        addi    a7, zero, SCALL_EXIT    ; exit syscall code
        scall
