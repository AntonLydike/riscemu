import typing
from .Registers import Registers
from .colors import FMT_DEBUG, FMT_NONE

if typing.TYPE_CHECKING:
    from . import *


def launch_debug_session(cpu: 'CPU', mmu: 'MMU', reg: 'Registers', prompt=""):
    if not cpu.conf.debug_instruction or cpu.active_debug:
        return
    import code
    import readline
    import rlcompleter

    cpu.active_debug = True

    # setup some aliases:
    registers = reg
    regs = reg
    memory = mmu
    mem = mmu
    syscall_interface = cpu.syscall_int

    # setup helper functions:
    def dump(what, *args, **kwargs):
        if isinstance(what, Registers):
            regs.dump(*args, **kwargs)
        else:
            mmu.dump(what, *args, **kwargs)

    def ins():
        print("Current instruction at 0x{:08X}:".format(cpu.pc))
        return mmu.read_ins(cpu.pc)

    def cont(verbose=True):
        cpu.continue_from_debugger(verbose)

    def step():
        cpu.step()

    sess_vars = globals()
    sess_vars.update(locals())

    readline.set_completer(rlcompleter.Completer(sess_vars).complete)
    readline.parse_and_bind("tab: complete")
    code.InteractiveConsole(sess_vars).interact(banner=FMT_DEBUG + prompt + FMT_NONE, exitmsg="Exiting debugger")
    cpu.active_debug = False
