# Assembly

Assembly tokenization should be workiung completely. It knows what instructions the CPU implementation supports and parses based on them.

## Pseudo-ops
The following pseudo-ops are implemented as of yet:
* `.space <len>` reverse <len> bytes of zero
* `.ascii 'text'` put text into memory
* `.asciiz 'text'` put text into memory (null terminated)
* `.sextion .<name>` same as `.<name>` see sections:

## Sections: 
Currently only these three sections are supported: 
* `data` read-write data (non-executable)
* `rodata` read-only data (non-executable)
* `.text` executable data (read-only)

## Allocating stack
another pseudo-op is recognized: `.stack <len>`. This marks the executable as requesting at least `<len>` bytes of stack. 
If the loader repsects this wish, the sp is initialized pointing to the end of the stack.

 

