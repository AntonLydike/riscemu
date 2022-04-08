# Changelog

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
