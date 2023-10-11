// RUN: python3 -m snitch %s -o libc -v| filecheck %s

.text
.globl main
main:
        // load constants
        li          t0, 0
        fcvt.s.w    ft0, t0
        li          t0, 1
        fcvt.s.w    ft1, t0

        // repeat 100 times
        li          t0, 99
        frep.i      t0, 1, 0, 0
        fadd.s      ft0, ft0, ft1   // add one

        // print result to stdout
        printf      "100 * 1 = {}", ft0
// CHECK: 100 * 1 = 100.0
        // return 0
        li          a0, 0
        ret

// CHECK-NEXT: [CPU] Program exited with code 0
