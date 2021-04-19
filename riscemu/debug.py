import typing
if typing.TYPE_CHECKING:
    from . import *


def launch_debug_session(cpu: 'CPU', mmu: 'MMU', reg: 'Registers', prompt=""):
    if not cpu.conf.debug_instruction:
        return
    import code
    import readline
    import rlcompleter

    # setup some aliases
    registers = reg
    regs = reg
    memory = mmu
    mem = mmu
    syscall_interface = cpu.syscall_int

    def dump(what, *args, **kwargs):
        if isinstance(what, Registers):
            regs.dump(*args, **kwargs)
        else:
            mmu.dump(what, *args, **kwargs)

    sess_vars = globals()
    sess_vars.update(locals())

    readline.set_completer(rlcompleter.Completer(sess_vars).complete)
    readline.parse_and_bind("tab: complete")
    code.InteractiveConsole(sess_vars).interact(banner=prompt, exitmsg="Resuming simulation")
