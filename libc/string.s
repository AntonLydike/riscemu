// string operations in RISC-V Assembly
//
// Copyright (c) 2023 Anton Lydike
// SPDX-License-Identifier: MIT

// Create NullPtr constant
.equ        NULL, 0x00
.global     NULL


.global     strlen
// size_t libstr_strlen(char* str)
// return the length of str


.global     strncpy
// char *strncpy(char *dest, const char *src, size_t n)
// copy n bytes from source into dest. If source ends before n bytes, the rest is filled with null-bytes
// returns pointer to dest


.global     strcpy
// char *strncpy(char *dest, const char *src)
// copy string src into dest, including null terminator
// returns pointer to dest


.global     memchr
// void *memchr(const void *str, char c, size_t n)
// search vor the first occurrence of c in str
// returns a pointer to the first occurrence, or NULL


.global     memset
// void *memset(void *str, char c, size_t n)
// copies the character c to the first n characters of  str.


// missing implementations
//.global     memcmp
//.global     memcpy
//.global     strcat


.text
strlen:
// size_t strlen(char* str)
            // push s1, s2 to the stack
            sw   s1, sp, -4
            sw   s2, sp, -8
            // since no subroutines are called, we don't need to increment or decrement the sp
            addi s2, zero, -1   // length (since null byte is counted by this method, we return len - 1)
__strlen_loop:
            lb   s1, a0, 0      // read character
            addi s2, s2, 1      // increment number bytes read
            addi a0, a0, 1
            bne  s1, zero, __strlen_loop
            // we are done, set return value in a0
            add  a0, zero, s2
            // pop s1, s2, from stack
            lw   s1, sp, -4
            lw   s2, sp, -8
            ret

strncpy:
// char *strncpy(char *dest, const char *src, size_t n)
// copy size bytes from source to dest
            sw   s1, sp, -4     // push s1 to the stack
            sw   s2, sp, -8     // push s1 to the stack
            add  s1, a0, zero   // save dest pointer for return
__strncpy_loop:
            beq  a2, zero, __strncpy_end
            // copy byte
            lb   s2, a1, 0      // read first byte from src
            sb   s2, a0, 0      // write first byte to dest
            // increment pointers
            addi a0, a0, 1
            addi a1, a1, 1
            // one less byte to copy
            addi a2, a2, -1
            // if we read the terminating byte, jump to fill code
            beq  s2, zero, __strncpy_fill
            // otherwise continue copying
            j    __strncpy_loop
__strncpy_fill:
            // fill remaining space with 0 bytes
            // if no bytes left, stop filling
            beq  a2, zero, __strncpy_end
            sb   zero, a0, 0
            addi a0, a0, 1
            addi a2, a2, -1
            j    __strncpy_fill
__strncpy_end:
            // set return value
            add  a0, zero, s1
            // pop s1, s2 from stack
            lw   s1, sp, -4
            lw   s2, sp, -8
            ret


strcpy:
// char *strcpy(char *dest, const char *src)
            sw   s1, sp, -4     // push s1 to the stack
            sw   s2, sp, -8     // push s1 to the stack
            add  s1, a0, zero   // save dest pointer for return
__strcpy_loop:
            // copy byte
            lb   s2, a1, 0      // read first byte from src
            sb   s2, a0, 0      // write first byte to dest
            // increment pointers
            addi a0, a0, 1
            addi a1, a1, 1
            bne  s2, zero, __strcpy_loop
            // we are done copying, return
            // set return value
            add  a0, zero, s1
            // pop s1, s2 from stack
            lw   s1, sp, -4
            lw   s2, sp, -8
            ret

memchr:
// void *memchr(const void *str, char c, size_t n)
            sw   s1, sp, -4     // push s1 to the stack
            andi a1, a1, 0xff   // trim a1 to be byte-sized
__memchr_loop:
            beq  a2, zero, __memchr_ret_null
            lb   s1, a0, 0
            addi a0, a0, 1  // let a0 point to the next byte
            addi a2, a2, -1 // decrement bytes to copy by 1
            bne  s1, a1, __memchr_loop
            // return pointer to prev byte (as the prev byte actually matched a1)
            addi a0, a0, -1
            // pop s1, from stack
            lw   s1, sp, -4
            ret
__memchr_ret_null:
            // nothing found, return nullptr
            addi a0, zero, NULL
            lw   s1, sp, -4
            ret


memset:
// void *memset(void *str, char c, size_t n)
__memset_loop:
            beq  a2, zero, __memset_ret
            sb   a1, a0, 0
            addi a0, a0, 1
            addi a2, a2, -1
            j    __memset_loop
__memset_ret:
            ret
