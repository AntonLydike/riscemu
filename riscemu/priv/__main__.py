from .PrivCPU import PrivCPU, RunConfig

from ..Tokenizer import RiscVInput
from ..ExecutableParser import ExecutableParser

import sys

if __name__ == '__main__':

    files = sys.argv

    cpu = PrivCPU(RunConfig())

    cpu.run()


