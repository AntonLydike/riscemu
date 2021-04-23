# Syscalls

Performing a syscall is quite simple:
```risc-v asm
    ; set syscall code:
    addi a7, zero, 93   ; or SCALL_EXIT if syscall symbols are mapped
    ; set syscall args:
    addi a0, zero, 1    ; exit with code 1
    ; invode syscall handler
    scall               
```

The global symbols (e.g. `SCALL_READ`) are loaded by default. If you specify the option `no_syscall_symbols`, they will be omitted.


## Read (63) `SCALL_READ`
* `a0`: source file descriptor
* `a1`: addr in which to read
* `a2`: number of bytes to read (at most)
* `return: a0` number of bytes read or -1

## Write (64) `SCALL_WRITE`
* `a0`: target file descriptor
* `a1`: addr from which to read
* `a2`: number of bytes to read
* `return: a0`: number of bytes written or -1

## Exit (93) `SCALL_EXIT`
* `a0`: exit code

## Open (1024) `SCALL_OPEN`
* `a0`: open mode:
    - `0`: read
    - `1`: write (truncate)
    - `2`: read/write (no truncate)
    - `3`: only create
    - `4`: append
* `a1`: addr where path is stored
* `a2`: length of path
* `return: a0`: file descriptor of opened file or -1

Requires flag `--scall-fs` to be set to True

## Close (1025) `SCALL_CLOSE`
* `a0`: file descriptor to close
* `return: a0`: 0 if closed correctly or -1

