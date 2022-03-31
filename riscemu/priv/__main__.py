from riscemu import RunConfig
from riscemu.types import Program
from .PrivCPU import PrivCPU

import sys

if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser(description='RISC-V privileged architecture emulator', prog='riscemu')

    parser.add_argument('source', type=str,
                        help='Compiled RISC-V ELF file or memory image containing compiled RISC-V ELF files', nargs='+')
    parser.add_argument('--debug-exceptions', help='Launch the interactive debugger when an exception is generated',
                        action='store_true')

    parser.add_argument('-v', '--verbose', help="Verbosity level (can be used multiple times)", action='count',
                        default=0)

    parser.add_argument('--slowdown', help="Slow down the emulated CPU clock by a factor", type=float, default=1)

    args = parser.parse_args()

    cpu = PrivCPU(RunConfig(verbosity=args.verbose, debug_on_exception=args.debug_exceptions, slowdown=args.slowdown))

    for source_path in args.source:
        loader = max((loader for loader in cpu.get_loaders()), key=lambda l: l.can_parse(source_path))
        argv, opts = loader.get_options(sys.argv)
        program = loader.instantiate(source_path, opts).parse()
        if isinstance(program, Program):
            cpu.load_program(program)
        else:
            program_iter = program
            for program in program_iter:
                cpu.load_program(program)

    cpu.launch(verbose=args.verbose > 4)
