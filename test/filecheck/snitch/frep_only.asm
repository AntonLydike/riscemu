.text
.globl main
main:
        li          t0, 0
        fcvt.s.w    ft0, t0
        li          t0, 1
        fcvt.s.w    ft1, t0

        printf      "ft0 = {}, ft1 = {}", ft0, ft1
        // repeat 100 times
        li          t0, 99
        frep.i      t0, 1, 0, 0
        fadd.s      ft0, ft0, ft1   // add one
        printf      "100 * 1 = {}", ft1

        li          a0, 0
        ret
