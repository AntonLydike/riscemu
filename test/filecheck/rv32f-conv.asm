// RUN: python3 -m riscemu -v %s -o libc | filecheck %s

.text

.globl      main
main:
    // test fcvt.s.wu
    li a1, -2
    fcvt.s.wu fa0, a1
    print.float fa0
// CHECK: register fa0 contains value 4294967296.0
    li a1, 2
    fcvt.s.wu fa0, a1
    print.float fa0
// CHECK-NEXT: register fa0 contains value 2.0

    // test fcvt.s.w
    li a1, -2
    fcvt.s.w fa0, a1
    print.float fa0
// CHECK: register fa0 contains value -2.0
    li a1, 2
    fcvt.s.w fa0, a1
    print.float fa0
// CHECK-NEXT: register fa0 contains value 2.0

    // test fmv.s.x
    li a1, 2
    fcvt.s.w fa0, a1
    fmv.x.w a1, fa0
    print a1
// CHECK-NEXT: register a1 contains value 1073741824
    li a1, -2
    fcvt.s.w fa0, a1
    fmv.x.w a1, fa0
    print a1
// CHECK-NEXT: register a1 contains value 3221225472

    // test fmv.w.x
    li a1, 1073741824
    fmv.w.x fa0, a1
    print.float fa0
// CHECK-NEXT: register fa0 contains value 2.0
    li a1, 3221225472
    fmv.w.x fa0, a1
    print.float fa0
// CHECK-NEXT: register fa0 contains value -2.0

    ret
// CHECK-NEXT: [CPU] Program exited with code 0
