// RUN: python3 -m riscemu -v --ignore-exit-code %s || true | filecheck %s
.data
fibs:   .space 1024

        .text
main:
        addi    s1, zero, 0     // storage index
        addi    s2, zero, 1024  // last storage index
        addi    t0, zero, 1     // t0 = F_{i}
        addi    t1, zero, 1     // t1 = F_{i+1}
loop:
        sw      t0, fibs(s1)    // save
        add     t2, t1, t0      // t2 = F_{i+2}
        addi    t0, t1, 0       // t0 = t1
        addi    t1, t2, 0       // t1 = t2
        addi    s1, s1, 4       // increment storage pointer
        blt     s1, s2, loop    // loop as long as we did not reach array length
        // exit gracefully
        add     a0, zero, t2
        addi    a7, zero, 93
        scall                   // exit with code 0

// CHECK: [CPU] Program exited with code 1265227608
