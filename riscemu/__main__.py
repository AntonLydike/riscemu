if __name__ == '__main__':
    from . import *
    from .helpers import *
    import argparse
    import sys

    parser = argparse.ArgumentParser(description='RISC-V Userspace parser and emulator', prog='riscemu')
    parser.add_argument('files', metavar='file.asm', type=str, nargs='+',
                        help='The assembly files to load, the last one will be run')

    # RunConfig parameters
    parser.add_argument('--no-color', type=bool, help='no colored output', default=False,
                        nargs='?')
    parser.add_argument('--default_stack_size', type=int, help='Default stack size of loaded programs', default=None,
                        metavar='default-stack-size', nargs='?')
    parser.add_argument('--debug_instruction', type=bool, default=True, metavar='debug-instruction',
                        help='Switches to an interactive python interpreter when ebreak/sbreak instruction '
                             'is encountered. Otherwise these instructions are treated as nop.', nargs='?')

    parser.add_argument('--print_tokens', metavar='print-tokens', type=bool, help='Print tokens after tokenization',
                        default=False, nargs='?')

    args = parser.parse_args()


    cfg = RunConfig(
        color=not args.no_color,
        preffered_stack_size=args.default_stack_size,
        debug_instruction=args.debug_instruction
    )

    if cfg.color:
        FMT_PRINT = FMT_BOLD + FMT_MAGENTA
    else:
        FMT_NONE = ""
        FMT_PRINT = ""

    try:
        cpu = CPU(cfg)
        loaded_exe = None
        for file in args.files:
            tk = RiscVTokenizer(RiscVInput.from_file(file))
            tk.tokenize()

            if args.print_tokens:
                print(FMT_PRINT + "Tokens:" + FMT_NONE)
                for token in tk.tokens:
                    print(token)

            loaded_exe = cpu.load(ExecutableParser(tk).parse())

        # run the last loaded executable
        cpu.run_loaded(loaded_exe)
    except RiscemuBaseException as e:
        print("Error while parsing: {}".format(e.message()))
        import traceback
        traceback.print_exception(type(e), e, e.__traceback__)
        sys.exit(1)


