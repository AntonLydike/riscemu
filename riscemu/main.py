if __name__ == '__main__':
    from . import *
    from .helpers import *
    import argparse

    parser = argparse.ArgumentParser(description='RISC-V Userspace parser and emulator')
    parser.add_argument('file', metavar='file.asm', type=str, help='The assembly file to interpret and run')

    # RunConfig parameters
    parser.add_argument('color', type=bool, help='Colored output', default=True)
    parser.add_argument('default_stack_size', type=int, help='Default stack size of loaded programs', default=None,
                        metavar='default-stack-size')
    parser.add_argument('debug_instruction', type=bool, default=True, metavar='debug-instruction',
                        help='Switches to an interactive python interpreter when ebreak/sbreak instruction '
                             'is encountered. Otherwise these instructions are treated as nop.')

    parser.add_argument('print_tokens', metavar='print-tokens', type=bool, help='Print tokens after tokenization',
                        default=False)

    args = parser.parse_args()

    cfg = RunConfig(
        color=args.color,
        preffered_stack_size=args.default_stack_size,
        debug_instruction=args.debug_instruction
    )

    if cfg.color:
        FMT_PRINT = FMT_BOLD + FMT_MAGENTA
    else:
        FMT_NONE = ""
        FMT_PRINT = ""

    with open(args.file, 'r') as f:
        asm = f.read()

    tk = RiscVTokenizer(RiscVInput(asm))
    tk.tokenize()

    if args.print_tokens:
        print(FMT_PRINT + "Tokens:" + FMT_NONE)
        for token in tk.tokens:
            print(token)

    executable = ExecutableParser(tk).parse().get_execuable()

    print(FMT_PRINT + "Executable:" + FMT_NONE, executable)

    cpu = CPU(cfg)
    le = cpu.load(executable)
    cpu.run_loaded(le)

