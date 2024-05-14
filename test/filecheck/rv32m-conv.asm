// RUN: python3 -m riscemu -v %s -o libc | filecheck %s

.text

.globl      main
main:
    // test mulh
    li a1, -1
    mulh a0, a1, a1
    print a0
// CHECK: register a0 contains value 0
    li a2, 2
    mulh a0, a1, a2
    print.uhex a0
// CHECK-NEXT: register a0 contains value 0xffffffff

    // test mulhu
    mulhu a0, a1, a2
    print a0
// CHECK: register a0 contains value 1

    mulhu a0, a1, a1
    print.uhex a0
// CHECK-NEXT: register a0 contains value 0xfffffffe

    // test mulhsu
    mulhsu a0, a1, a2
    print.uhex a0
// CHECK: register a0 contains value 0xffffffff

    mulhsu a0, a2, a1
    print a0
// CHECK-NEXT: register a0 contains value 1

    li a0, 0
    ret
// CHECK-NEXT: [CPU] Program exited with code 0
