// RUN: python3 -m riscemu -v %s | filecheck %s
        .data
msg:    .ascii "Hello world\n"
        .text
        addi    x10, x0, 1             ; print to stdout
        addi    x11, x0, msg           ; load msg address
        addi    x12, x0, 12            ; write 12 bytes
        addi    x17, x0, SCALL_WRITE   ; write syscall code
        scall
        addi    x10, x0, 0             ; set exit code to 0
        addi    x17, x0, SCALL_EXIT    ; exit syscall code
        scall

// CHECK: Hello world
// CHECK: [CPU] Program exited with code 
