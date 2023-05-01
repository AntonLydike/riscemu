.data
my_data:
.word   0x11223344, 0x55667788, 0x9900aabb, 0xccddeeff

.text
main:
        // load base address into t0
        la  t0, my_data
        // begin loading words and printing them
        lw  a0, 0(t0)
        print.uhex a0
        lw  a0, 4(t0)
        print.uhex a0
        lw  a0, 8(t0)
        print.uhex a0
        lw  a0, 12(t0)
        print.uhex a0
        // exit
        li  a7, 93
        ecall
