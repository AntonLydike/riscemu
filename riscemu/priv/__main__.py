from .PrivCPU import PrivCPU
from .ElfLoader import ElfBinaryFileLoader
from .ImageLoader import MemoryImageLoader

import sys

if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser(description='RISC-V privileged architecture emulator', prog='riscemu')

    parser.add_argument('--kernel', type=str, help='Kernel elf loaded with user programs', nargs='?')
    parser.add_argument('--image', type=str, help='Memory image containing kernel', nargs='?')
    parser.add_argument('--debug-exceptions', help='Launch the interactive debugger when an exception is generated', action='store_true')

    parser.add_argument('-v', '--verbose', help="Verbosity level (can be used multiple times)", action='count', default=0)

    args = parser.parse_args()
    mmu = None

    if args.kernel is not None:
        mmu = LoadedElfMMU(ElfExecutable(args.kernel))
    elif args.image is not None:
        mmu = MemoryImageMMU(args.image)

    if mmu is None:
        print("You must specify one of --kernel or --image for running in privilege mode!")
        sys.exit(1)

    cpu = PrivCPU(RunConfig(verbosity=args.verbose, debug_on_exception=args.debug_exceptions), mmu)
    cpu.run()



