# Changelog

## 2.1.1

 - Bugfix: Fix some errors in the RV32F implementation (thanks @adutilleul)
 - Bugfix: Fix how floats are printed in the register view (thanks @KGrykiel)
 - Bugfix: Fix missing support for infinite registers in load/store ins (thanks @superlopuh)

## 2.1.0

 - Added a very basic libc containing a `crt0.s`, and a few functions
   such as `malloc`, `rand`, and `memcpy`.
 - Added a subset of the `mmap2` syscall (code 192) to allocate new memory
 - Refactored the launching code to improve using riscemu from code
 - Added an option to start with the provided libc: `-o libc`
 - Added floating point support (enabled by default). The RV32F extension is now available

## 2.0.5

 - Added unlimited register mode with `-o unlimited_regs`

## 2.0.4

 - Bugfix: fix a sign issue in instruction parsing for `rd, rs, rs` format
 - Bugfix: respect `conf.debug_instruction` setting

## 2.0.3 - 2022-04-18

 - Syscalls: cleaned up formatting and added instructions for extensions
 - Parser: fixed error when labels where used outside of sections
 - Cleaned up and improved memory dumping code
 - Fixed a bug with hex literal recognition in instruction parse code
 - Fixed bug where wrong parts of section would be printed in mmu.dump()
 - Removed tests for bind_twos_complement as the function is now redundant with the introduction of Int32
 - Fixed address translation error for sections without symbols
 - Changed verbosity level at which start and end of CPU are printed, added prints for start and stack loading

## 2.0.2

 - Added implicit declaration of .text section when a file starts with assembly instructions without declaring a section first
 - Fixed a regression where the cpu's exit code would no longer be the exit code of the emulator. Now the emulator exits with the cpu's exit code
 - Added the changelog

## 2.0.1

 - Fixed type annotations in parser code that prevented running unprivileged code

## 2.0.0

 - Correct handling of 32 bit overflows and underflows
 - Complete revamp of internal data structures
 - Completely reworked how assembly is parsed
