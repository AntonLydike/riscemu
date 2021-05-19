from .PrivCPU import *

from ..Tokenizer import RiscVInput
from ..ExecutableParser import ExecutableParser

import sys

if __name__ == '__main__':

    files = sys.argv

    cpu = PrivCPU(RunConfig())

    try:
        loaded_exe = None
        for file in files:
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
