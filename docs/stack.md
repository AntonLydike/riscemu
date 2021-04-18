# The stack

The stack is a continuous region of memory, located somewhere. The stack grows "downwards", meaning new values are pushed like this:
```asm
    add sp, sp, -4
    sw  a0, sp, 0 

```


