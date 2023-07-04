main:
    li a1, 1084227584
    li a2, 1082130432
    fcvt.s.wu ft0, a1
    fcvt.s.wu ft1, a2
    fmul.s ft6, ft0, ft1
    print.float ft6
    // exit gracefully
    addi    a0, zero, 0
    addi    a7, zero, 93
    scall                   // exit with code 0
