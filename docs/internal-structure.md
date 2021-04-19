# The internal structure of RISCemu

## Loading assembly files:
In order to load an assembly file, you need to instantiate a CPU with the capabilities you want. Loading an assembly 
file is the done in multiple steps:


* An `RiscVInput` is created, this represents the file internally
* An `RiscVTokenizer` is created by calling `cpu.get_tokenizer()`.
* The input is tokenized by calling `.tokenize()` on the tokenizer.
* The tokens can then be converted to an Executable, this will then 
  hold all the information such as name, sections, symbols, etc.
  This is done by creating an `ExecutableParser(tk: RiscVTokenizer)`
  and the calling `parse()`.
* Now you have a representation of the assembly file that can be loaded
  into memory by calling `cpu.load(executable)`, this will internally 
  construct a `LoadedExecutable`, which represents the actual memory
  regions the executable contains (and some meta information such as
  symbols).
* You can load as many executables as you want into memory. If you want
  to run one, you pass it to `run_loaded(loaded_bin)` method of the cpu.

You shouldn't have to do this manually, as the `riscemu/__main__.py` has all the necessary code.

## Instruction sets
Each instruction set is in a separate file in `riscemu/instructions/`. All instruction sets have to inherit from the
`InstructionSet` class that sets up all the relevant helpers and loading code.

Creating a cpu with certain instruction sets is done by passing the CPU constructor a list of instruction set classes:
```
cpu = CPU(config, [RV32I, RV32M])
```

