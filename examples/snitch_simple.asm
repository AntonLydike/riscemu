.data

vec0:
.word 0x0, 0x3f800000, 0x40000000, 0x40400000, 0x40800000, 0x40a00000, 0x40c00000, 0x40e00000, 0x41000000, 0x41100000, 0x41200000, 0x41300000, 0x41400000, 0x41500000, 0x41600000, 0x41700000, 0x41800000, 0x41880000, 0x41900000, 0x41980000, 0x41a00000, 0x41a80000, 0x41b00000, 0x41b80000, 0x41c00000, 0x41c80000, 0x41d00000, 0x41d80000, 0x41e00000, 0x41e80000, 0x41f00000, 0x41f80000, 0x42000000, 0x42040000, 0x42080000, 0x420c0000, 0x42100000, 0x42140000, 0x42180000, 0x421c0000, 0x42200000, 0x42240000, 0x42280000, 0x422c0000, 0x42300000, 0x42340000, 0x42380000, 0x423c0000, 0x42400000, 0x42440000, 0x42480000, 0x424c0000, 0x42500000, 0x42540000, 0x42580000, 0x425c0000, 0x42600000, 0x42640000, 0x42680000, 0x426c0000, 0x42700000, 0x42740000, 0x42780000, 0x427c0000, 0x42800000, 0x42820000, 0x42840000, 0x42860000, 0x42880000, 0x428a0000, 0x428c0000, 0x428e0000, 0x42900000, 0x42920000, 0x42940000, 0x42960000, 0x42980000, 0x429a0000, 0x429c0000, 0x429e0000, 0x42a00000, 0x42a20000, 0x42a40000, 0x42a60000, 0x42a80000, 0x42aa0000, 0x42ac0000, 0x42ae0000, 0x42b00000, 0x42b20000, 0x42b40000, 0x42b60000, 0x42b80000, 0x42ba0000, 0x42bc0000, 0x42be0000, 0x42c00000, 0x42c20000, 0x42c40000, 0x42c60000
vec1:
.word 0x0, 0x3f800000, 0x40000000, 0x40400000, 0x40800000, 0x40a00000, 0x40c00000, 0x40e00000, 0x41000000, 0x41100000, 0x41200000, 0x41300000, 0x41400000, 0x41500000, 0x41600000, 0x41700000, 0x41800000, 0x41880000, 0x41900000, 0x41980000, 0x41a00000, 0x41a80000, 0x41b00000, 0x41b80000, 0x41c00000, 0x41c80000, 0x41d00000, 0x41d80000, 0x41e00000, 0x41e80000, 0x41f00000, 0x41f80000, 0x42000000, 0x42040000, 0x42080000, 0x420c0000, 0x42100000, 0x42140000, 0x42180000, 0x421c0000, 0x42200000, 0x42240000, 0x42280000, 0x422c0000, 0x42300000, 0x42340000, 0x42380000, 0x423c0000, 0x42400000, 0x42440000, 0x42480000, 0x424c0000, 0x42500000, 0x42540000, 0x42580000, 0x425c0000, 0x42600000, 0x42640000, 0x42680000, 0x426c0000, 0x42700000, 0x42740000, 0x42780000, 0x427c0000, 0x42800000, 0x42820000, 0x42840000, 0x42860000, 0x42880000, 0x428a0000, 0x428c0000, 0x428e0000, 0x42900000, 0x42920000, 0x42940000, 0x42960000, 0x42980000, 0x429a0000, 0x429c0000, 0x429e0000, 0x42a00000, 0x42a20000, 0x42a40000, 0x42a60000, 0x42a80000, 0x42aa0000, 0x42ac0000, 0x42ae0000, 0x42b00000, 0x42b20000, 0x42b40000, 0x42b60000, 0x42b80000, 0x42ba0000, 0x42bc0000, 0x42be0000, 0x42c00000, 0x42c20000, 0x42c40000, 0x42c60000
dest:
.space 400

.text
.globl main

main:
    // ssr config
    ssr.configure   0, 100, 4
    ssr.configure   1, 100, 4
    ssr.configure   2, 100, 4

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

    ebreak

    ret
