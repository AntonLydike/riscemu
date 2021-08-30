from .PrivCPU import PrivCPU, RunConfig
from .ImageLoader import MemoryImageMMU
from .PrivMMU import LoadedElfMMU
from .ElfLoader import ElfExecutable

from ..Tokenizer import RiscVInput
from ..ExecutableParser import ExecutableParser

import sys

if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser(description='RISC-V privileged architecture emulator', prog='riscemu')

    parser.add_argument('--kernel', type=str, help='Kernel elf loaded with user programs', nargs='?')
    parser.add_argument('--image', type=str, help='Memory image containing kernel', nargs='?')

    parser.add_argument('-v', '--verbose', help="Verbose output", action='store_true')

    args = parser.parse_args()
    mmu = None

    if args.kernel is not None:
        mmu = LoadedElfMMU(ElfExecutable(args.kernel))
    elif args.image is not None:
        mmu = MemoryImageMMU(args.image)

    if mmu is None:
        print("You must specify one of --kernel or --image for running in privilege mode!")
        sys.exit(1)

    cpu = PrivCPU(RunConfig(), mmu)
    cpu.run(args.verbose)



