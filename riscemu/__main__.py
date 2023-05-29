"""
RiscEmu (c) 2021 Anton Lydike

SPDX-License-Identifier: MIT

This file holds the logic for starting the emulator from the CLI
"""
import sys

from riscemu import RiscemuBaseException
from riscemu.riscemu_main import RiscemuMain

try:
    main = RiscemuMain()
    main.run(sys.argv[1:])
    sys.exit(main.cpu.exit_code if not main.cfg.ignore_exit_code else 0)

except RiscemuBaseException as e:
    print("Error: {}".format(e.message()))
    e.print_stacktrace()

    sys.exit(-1)
