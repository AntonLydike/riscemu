if __name__ == '__main__':
    import code
    import readline
    import rlcompleter

    from .decoder import *
    from .formats import *
    from .instruction_table import *
    from .regs import RISCV_REGS

    sess_vars = globals()
    sess_vars.update(locals())

    readline.set_completer(rlcompleter.Completer(sess_vars).complete)
    readline.set_completer(rlcompleter.Completer(sess_vars).complete)
    readline.parse_and_bind("tab: complete")
    code.InteractiveConsole(sess_vars).interact(banner="Interaktive decoding session started...", exitmsg="Closing...")
