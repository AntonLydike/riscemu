.text

.globl main
main:
// check that less that 1000 ticks passed since start
    csrrs   a0, zero, time
    li      a1, 1000
    bge     a0, a1, fail
    print   a0, "time passed since launch: {1} ticks"
// CHECK: time passed since launch:
// check that timeh is empty
    csrrs   a0, zero, timeh
    bne     a0, zero, fail
// check that some ammount of cycles has passed so far:
    csrrs   a0, zero, cycle
    beq     a0, zero, fail
    print   a0, "cycles passed: {1}"
// CHECK-NEXT: cycles passed:
// check that cycleh is zero
    csrrs   a0, zero, cycleh
    bne     a0, zero, fail
// check instret and instreth
    csrrs   a0, zero, instret
    beq     a0, zero, fail
    print   a0, "instret is: {1}"
// CHECK-NEXT: instret is:
    csrrs   a0, zero, instreth
    bne     a0, zero, fail
// CHECK-NEXT: Success!
    print   a0, "Success!"
    ret

fail:
    li      a0, -1
    print   a0, "Failure!"

ret
