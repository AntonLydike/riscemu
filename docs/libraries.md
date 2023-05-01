# Included libraries

I've started to implement some sort of standard library, following closely to [GNU's glibc](https://www.gnu.org/software/libc/).

You can include the libraries by adding them as arguments (before your main assembly file):

```
> python3 -m riscemu examples/lib/libstring.asm example.asm
[MMU] Successfully loaded: LoadedExecutable[examples/lib/libstring.asm](base=0x00000100, size=64bytes, sections=text, run_ptr=0x00000100)
[MMU] Successfully loaded: LoadedExecutable[example.asm](base=0x00000140, size=168bytes, sections=data text, run_ptr=0x000001D0)
[CPU] Allocated 524288 bytes of stack
[CPU] Started running from 0x000001D0 (example.asm)
```

These libraries are no where near a stable state, so documentation will be scarce. Your best bet would be to `grep` for functionality. Sorry!
