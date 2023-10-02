// RUN: riscemu -o libc %s | filecheck %s
.data
.space 8

.globl main
.text

text_start:
.p2align 8
main:
la      a0, main
la      a1, text_start
sub     a0, a0, a1
print   a0
// align to 2**8 bytes, so 256
// we have 8 bytes of padding at the front, so we should see 248 bytes between text_start and main
// CHECK: register a0 contains value 248
li      a0, 0
ret
