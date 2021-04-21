if __name__ == '__main__':
    from . import *
    from .helpers import *
    from .instructions import InstructionSetDict
    import argparse
    import sys

    all_ins_names = list(InstructionSetDict.keys())

    class OptionStringAction(argparse.Action):
        def __init__(self, option_strings, dest, keys=None, omit_empty=False, **kwargs):
            if keys is None:
                raise ValueError('must define "keys" argument')
            if isinstance(keys, dict):
                keys_d = keys
            elif isinstance(keys, (list, tuple)):
                keys_d = {}
                for k in keys:
                    if isinstance(k, tuple):
                        k, v = k
                    else:
                        v = False
                    keys_d[k] = v
            else:
                keys_d = dict()
            super().__init__(option_strings, dest, default=keys_d, **kwargs)
            self.keys = keys_d
            self.omit_empty = omit_empty

        def __call__(self, parser, namespace, values, option_string=None):
            d = {}
            if not self.omit_empty:
                d.update(self.keys)
            for x in values.split(','):
                if x in self.keys:
                    d[x] = True
                else:
                    raise ValueError('Invalid parameter supplied: ' + x)
            setattr(namespace, self.dest, d)


    parser = argparse.ArgumentParser(description='RISC-V Userspace parser and emulator', prog='riscemu')
    parser.add_argument('files', metavar='file.asm', type=str, nargs='+',
                        help='The assembly files to load, the last one will be run')

    parser.add_argument('--options', '-o', action=OptionStringAction,
                        keys=('disable_debug', 'no_syscall_symbols', 'fail_on_ex', 'add_accept_imm'))

    parser.add_argument('--syscall-opts', '-so', action=OptionStringAction,
                        keys=('fs_access', 'disable_input'))

    parser.add_argument('--instruction-sets', '-is', action=OptionStringAction, help="Instruction sets to load, available are: {}. "
                                                                        "All are enabled by default"
                        .format(", ".join(all_ins_names)), keys={k: True for k in all_ins_names}, omit_empty=True)

    parser.add_argument('--default_stack_size', type=int, help='Default stack size of loaded programs', default=None,
                        metavar='default-stack-size', nargs='?')

    args = parser.parse_args()

    cfg = RunConfig(
        preffered_stack_size=args.default_stack_size,
        debug_instruction=not args.options['disable_debug'],
        include_scall_symbols=not args.options['no_syscall_symbols'],
        debug_on_exception=not args.options['fail_on_ex'],
        add_accept_imm=args.options['add_accept_imm'],
        scall_fs=args.syscall_opts['fs_access'],
        scall_input=not args.syscall_opts['disable_input']
    )


    if not hasattr(args, 'ins'):
        setattr(args, 'ins', {k: True for k in all_ins_names})

    FMT_PRINT = FMT_BOLD + FMT_MAGENTA

    # parse required instruction sets
    ins_to_load = [
        InstructionSetDict[name] for name, b in args.ins.items() if b
    ]

    try:
        cpu = CPU(cfg, ins_to_load)
        loaded_exe = None
        for file in args.files:
            tk = cpu.get_tokenizer(RiscVInput.from_file(file))
            tk.tokenize()
            loaded_exe = cpu.load(ExecutableParser(tk).parse())
        # run the last loaded executable
        cpu.run_loaded(loaded_exe)
    except RiscemuBaseException as e:
        print("Error while parsing: {}".format(e.message()))
        import traceback
        traceback.print_exception(type(e), e, e.__traceback__)
        sys.exit(1)


