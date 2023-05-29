# RiscEmu LibC

This is a very basic implementation of libc in risc-v assembly, meant specifically for the riscemu emulator.

This is currently very incomplete, only a handful of methods are implemented, and most of them pretty basic.

## Contents:

### `stdlib.s`

Basic implementations of:

 - `malloc`/`free` (that leaks memory)
 - `rand`/`srand` (using xorshift)
 - `exit`/`atexit` (supporting up to 8 exit handlers)

### `string.s`

Somewhat nice implementations of:

 - `strlen`
 - `strncpy`
 - `strcpy`
 - `memchr`
 - `memset` (very basic byte-by-byte copy)

## Correctness:

This library is only lightly tested, so be careful and report bugs when you find them!
