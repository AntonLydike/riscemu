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
* `a1`: addr at which to write the input
* `a2`: number of bytes to read (at most)
* `return in a0`: number of bytes read or -1

## Write (64) `SCALL_WRITE`
* `a0`: target file descriptor
* `a1`: addr at which the data to be written is located
* `a2`: number of bytes to write
* `return in a0`: number of bytes written or -1

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
* `return in a0`: file descriptor of opened file or -1

Requires flag `--scall-fs` to be set to True

## Close (1025) `SCALL_CLOSE`
* `a0`: file descriptor to close
* `return in a0`: 0 if closed correctly or -1

# Extending these syscalls

You can implement your own syscall by adding its code to the `SYSCALLS` dict in the [riscemu/syscalls.py](../riscemu/syscall.py) file, creating a mapping of a syscall code to a name, and then implementing that syscall name in the SyscallInterface class further down that same file. Each syscall method should have the same signature: `read(self, scall: Syscall)`. The `Syscall` object gives you access to the cpu, through which you can access registers and memory. You can look at the `read` or `write` syscalls for further examples. 
