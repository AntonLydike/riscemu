// RUN: python3 -m snitch %s -o libc | filecheck %s

.data

vec0:
.word 0x0, 0x3f800000, 0x40000000, 0x40400000, 0x40800000, 0x40a00000, 0x40c00000, 0x40e00000, 0x41000000, 0x41100000
vec1:
.word 0x0, 0x3f800000, 0x40000000, 0x40400000, 0x40800000, 0x40a00000, 0x40c00000, 0x40e00000, 0x41000000, 0x41100000
dest:
.space 40

.text
.globl main

main:
    // ssr config
    ssr.configure   0, 10, 4
    ssr.configure   1, 10, 4
    ssr.configure   2, 10, 4

    la              a0, vec0
    ssr.read        a0, 0, 0

    la              a0, vec1
    ssr.read        a0, 1, 0

    la              a0, dest
    ssr.write       a0, 2, 0

    ssr.enable

    // set up loop
    li a0, 100
loop:
    fadd.s      ft2, ft0, ft1

    addi a0, a0, -1
    bne  a0, zero, loop

    // end of loop:
    ssr.disable

    ret

//CHECK: stream: got val 0.0 from addr 0x80148, stream StreamDef(base=524616, bound=10, stride=4, mode=<StreamMode.READ: 1>, dim=0, pos=0)
//CHECK_NEXT: stream: got val 0.0 from addr 0x80170, stream StreamDef(base=524656, bound=10, stride=4, mode=<StreamMode.READ: 1>, dim=0, pos=0)
//CHECK_NEXT: stream: wrote val 0.0 into addr 0x80198, stream StreamDef(base=524696, bound=10, stride=4, mode=<StreamMode.WRITE: 2>, dim=0, pos=0)
//CHECK_NEXT: stream: got val 1.0 from addr 0x8014c, stream StreamDef(base=524616, bound=10, stride=4, mode=<StreamMode.READ: 1>, dim=0, pos=1)
//CHECK_NEXT: stream: got val 1.0 from addr 0x80174, stream StreamDef(base=524656, bound=10, stride=4, mode=<StreamMode.READ: 1>, dim=0, pos=1)
//CHECK_NEXT: stream: wrote val 2.0 into addr 0x8019c, stream StreamDef(base=524696, bound=10, stride=4, mode=<StreamMode.WRITE: 2>, dim=0, pos=1)
//CHECK_NEXT: stream: got val 2.0 from addr 0x80150, stream StreamDef(base=524616, bound=10, stride=4, mode=<StreamMode.READ: 1>, dim=0, pos=2)
//CHECK_NEXT: stream: got val 2.0 from addr 0x80178, stream StreamDef(base=524656, bound=10, stride=4, mode=<StreamMode.READ: 1>, dim=0, pos=2)
//CHECK_NEXT: stream: wrote val 4.0 into addr 0x801a0, stream StreamDef(base=524696, bound=10, stride=4, mode=<StreamMode.WRITE: 2>, dim=0, pos=2)
//CHECK_NEXT: stream: got val 3.0 from addr 0x80154, stream StreamDef(base=524616, bound=10, stride=4, mode=<StreamMode.READ: 1>, dim=0, pos=3)
//CHECK_NEXT: stream: got val 3.0 from addr 0x8017c, stream StreamDef(base=524656, bound=10, stride=4, mode=<StreamMode.READ: 1>, dim=0, pos=3)
//CHECK_NEXT: stream: wrote val 6.0 into addr 0x801a4, stream StreamDef(base=524696, bound=10, stride=4, mode=<StreamMode.WRITE: 2>, dim=0, pos=3)
//CHECK_NEXT: stream: got val 4.0 from addr 0x80158, stream StreamDef(base=524616, bound=10, stride=4, mode=<StreamMode.READ: 1>, dim=0, pos=4)
//CHECK_NEXT: stream: got val 4.0 from addr 0x80180, stream StreamDef(base=524656, bound=10, stride=4, mode=<StreamMode.READ: 1>, dim=0, pos=4)
//CHECK_NEXT: stream: wrote val 8.0 into addr 0x801a8, stream StreamDef(base=524696, bound=10, stride=4, mode=<StreamMode.WRITE: 2>, dim=0, pos=4)
//CHECK_NEXT: stream: got val 5.0 from addr 0x8015c, stream StreamDef(base=524616, bound=10, stride=4, mode=<StreamMode.READ: 1>, dim=0, pos=5)
//CHECK_NEXT: stream: got val 5.0 from addr 0x80184, stream StreamDef(base=524656, bound=10, stride=4, mode=<StreamMode.READ: 1>, dim=0, pos=5)
//CHECK_NEXT: stream: wrote val 10.0 into addr 0x801ac, stream StreamDef(base=524696, bound=10, stride=4, mode=<StreamMode.WRITE: 2>, dim=0, pos=5)
//CHECK_NEXT: stream: got val 6.0 from addr 0x80160, stream StreamDef(base=524616, bound=10, stride=4, mode=<StreamMode.READ: 1>, dim=0, pos=6)
//CHECK_NEXT: stream: got val 6.0 from addr 0x80188, stream StreamDef(base=524656, bound=10, stride=4, mode=<StreamMode.READ: 1>, dim=0, pos=6)
//CHECK_NEXT: stream: wrote val 12.0 into addr 0x801b0, stream StreamDef(base=524696, bound=10, stride=4, mode=<StreamMode.WRITE: 2>, dim=0, pos=6)
//CHECK_NEXT: stream: got val 7.0 from addr 0x80164, stream StreamDef(base=524616, bound=10, stride=4, mode=<StreamMode.READ: 1>, dim=0, pos=7)
//CHECK_NEXT: stream: got val 7.0 from addr 0x8018c, stream StreamDef(base=524656, bound=10, stride=4, mode=<StreamMode.READ: 1>, dim=0, pos=7)
//CHECK_NEXT: stream: wrote val 14.0 into addr 0x801b4, stream StreamDef(base=524696, bound=10, stride=4, mode=<StreamMode.WRITE: 2>, dim=0, pos=7)
//CHECK_NEXT: stream: got val 8.0 from addr 0x80168, stream StreamDef(base=524616, bound=10, stride=4, mode=<StreamMode.READ: 1>, dim=0, pos=8)
//CHECK_NEXT: stream: got val 8.0 from addr 0x80190, stream StreamDef(base=524656, bound=10, stride=4, mode=<StreamMode.READ: 1>, dim=0, pos=8)
//CHECK_NEXT: stream: wrote val 16.0 into addr 0x801b8, stream StreamDef(base=524696, bound=10, stride=4, mode=<StreamMode.WRITE: 2>, dim=0, pos=8)
//CHECK_NEXT: stream: got val 9.0 from addr 0x8016c, stream StreamDef(base=524616, bound=10, stride=4, mode=<StreamMode.READ: 1>, dim=0, pos=9)
//CHECK_NEXT: stream: got val 9.0 from addr 0x80194, stream StreamDef(base=524656, bound=10, stride=4, mode=<StreamMode.READ: 1>, dim=0, pos=9)
//CHECK_NEXT: stream: wrote val 18.0 into addr 0x801bc, stream StreamDef(base=524696, bound=10, stride=4, mode=<StreamMode.WRITE: 2>, dim=0, pos=9)
