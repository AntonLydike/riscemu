from .PrivCPU import PrivCPU, RunConfig

from ..Tokenizer import RiscVInput
from ..ExecutableParser import ExecutableParser

import sys

if __name__ == '__main__':
    import argparse

    #parser = argparse.ArgumentParser(description='RISC-V privileged architecture emulator', prog='riscemu')

    #parser.add_argument('--kernel', type=str, help='Kernel elf loaded with user programs', nargs='?')
    #parser.add_argument('--image', type=str, help='Memory image containing kernel', nargs='?')

    #args = parser.parse_args()

    cpu = PrivCPU(RunConfig())

    cpu.run()



