"""
RiscEmu (c) 2021 Anton Lydike

SPDX-License-Identifier: MIT

This file holds the logic for starting the emulator from the CLI
"""
from riscemu import RiscemuBaseException, __copyright__, __version__
from riscemu.CPU import UserModeCPU

if __name__ == '__main__':
    from .config import RunConfig
    from .instructions import InstructionSetDict
    from .colors import FMT_BOLD, FMT_MAGENTA
    from .parser import AssemblyFileLoader
    import argparse
    import sys

    all_ins_names = list(InstructionSetDict.keys())

    if '--version' in sys.argv:
        print("riscemu version {}\n{}\n\nAvailable ISA: {}".format(
            __version__, __copyright__,
            ", ".join(InstructionSetDict.keys())
        ))
        sys.exit()

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

    parser.add_argument('--instruction-sets', '-is', action=OptionStringAction,
                        help="Instruction sets to load, available are: {}. All are enabled by default"
                        .format(", ".join(all_ins_names)), keys={k: True for k in all_ins_names}, omit_empty=True)

    parser.add_argument('--stack_size', type=int, help='Stack size of loaded programs, defaults to 8MB', nargs='?')

    parser.add_argument('-v', '--verbose', help="Verbosity level (can be used multiple times)", action='count',
                        default=0)

    parser.add_argument('--interactive', help="Launch the interactive debugger instantly instead of loading any "
                                              "programs", action='store_true')

    args = parser.parse_args()

    # create a RunConfig from the cli args
    cfg_dict = dict(
        stack_size=args.stack_size,
        debug_instruction=not args.options['disable_debug'],
        include_scall_symbols=not args.options['no_syscall_symbols'],
        debug_on_exception=not args.options['fail_on_ex'],
        add_accept_imm=args.options['add_accept_imm'],
        scall_fs=args.syscall_opts['fs_access'],
        scall_input=not args.syscall_opts['disable_input'],
        verbosity=args.verbose
    )
    for k, v in dict(cfg_dict).items():
        if v is None:
            del cfg_dict[k]

    cfg = RunConfig(**cfg_dict)

    if not hasattr(args, 'ins'):
        setattr(args, 'ins', {k: True for k in all_ins_names})

    FMT_PRINT = FMT_BOLD + FMT_MAGENTA

    # parse required instruction sets
    ins_to_load = [
        InstructionSetDict[name] for name, b in args.ins.items() if b
    ]

    try:
        cpu = UserModeCPU(ins_to_load, cfg)

        opts = AssemblyFileLoader.get_options(sys.argv)
        for file in args.files:
            loader = AssemblyFileLoader.instantiate(file, opts)
            cpu.load_program(loader.parse())

        # set up a stack
        cpu.setup_stack(cfg.stack_size)

        # launch the last loaded program
        cpu.launch(cpu.mmu.programs[-1], verbose=cfg.verbosity > 1)

    except RiscemuBaseException as e:
        print("Error: {}".format(e.message()))
        e.print_stacktrace()

        sys.exit(1)
