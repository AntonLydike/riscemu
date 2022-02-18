from riscemu import AssemblyFileLoader
from riscemu.colors import *

FMT_SUCCESS = FMT_GREEN + FMT_BOLD

def run_test(path: str):
    from riscemu import CPU, UserModeCPU, RunConfig
    from riscemu.instructions import InstructionSetDict
    from test.test_isa import TestIS
    import os

    fname = os.path.basename(path)

    ISAs = list(InstructionSetDict.values())
    ISAs.append(TestIS)

    cpu = UserModeCPU(ISAs, RunConfig())
    try:
        program = AssemblyFileLoader(path, {}).parse()
        cpu.load_program(program)
        cpu.launch(program)
    except Exception as ex:
        print(FMT_ERROR + '[Test] 🔴 failed with exception "{}" ({})'.format(ex, fname) + FMT_NONE)
        raise ex

    if cpu.halted:
        for isa in cpu.instruction_sets:
            if isinstance(isa, TestIS):
                if not isa.failed:
                    print(FMT_SUCCESS + '[Test] 🟢 successful {}'.format(fname) + FMT_NONE)
                return not isa.failed
    return False


if __name__ == '__main__':

    import os
    import glob

    successes = 0
    failures = 0
    ttl = 0

    for path in glob.glob(f'{os.path.dirname(__file__)}/*.asm'):
        print(FMT_BLUE + '[Test] running testcase ' + os.path.basename(path) + FMT_NONE)
        ttl += 1
        if run_test(path):
            successes += 1
        else:
            failures += 1



