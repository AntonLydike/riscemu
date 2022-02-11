"""
RiscEmu (c) 2021 Anton Lydike

SPDX-License-Identifier: MIT

This file contains the CPU logic (not the individual instruction sets). See instructions/InstructionSet.py for more info
on them.
"""
import sys
from typing import Tuple, List, Dict, Callable, Type

from .types import MemoryFlags
from .syscall import SyscallInterface, get_syscall_symbols
from .exceptions import RiscemuBaseException, LaunchDebuggerException
from .MMU import MMU
from .config import RunConfig
from .registers import Registers
from .debug import launch_debug_session
from .colors import FMT_CPU, FMT_NONE, FMT_ERROR

import riscemu

import typing

if typing.TYPE_CHECKING:
    from . import types, LoadedExecutable, LoadedInstruction
    from .instructions.InstructionSet import InstructionSet


class CPU:
    """
    This class represents a single CPU. It holds references to it's mmu, registers and syscall interrupt handler.

    It is initialized with a configuration and a list of instruction sets.
    """

    INS_XLEN = 4

    def __init__(self, conf: RunConfig, instruction_sets: List[Type['riscemu.InstructionSet']]):
        """
        Creates a CPU instance.

        :param conf: An instance of the current RunConfiguration
        :param instruction_sets: A list of instruction set classes. These must inherit from the InstructionSet class
        """
        # setup CPU states
        self.pc = 0
        self.cycle = 0
        self.exit: bool = False
        self.exit_code: int = 0
        self.conf = conf
        self.active_debug = False  # if a debugging session is currently runnign

        self.stack: typing.Optional['riscemu.LoadedMemorySection'] = None

        # setup MMU, registers and syscall handlers
        self.mmu = MMU(conf)
        self.regs = Registers(conf)
        self.syscall_int = SyscallInterface()

        # load all instruction sets
        self.instruction_sets: List[riscemu.InstructionSet] = list()
        self.instructions: Dict[str, Callable[[LoadedInstruction], None]] = dict()
        for set_class in instruction_sets:
            ins_set = set_class(self)
            self.instructions.update(ins_set.load())
            self.instruction_sets.append(ins_set)

        # provide global syscall symbols if option is set
        if conf.include_scall_symbols:
            self.mmu.global_symbols.update(get_syscall_symbols())

    def continue_from_debugger(self, verbose=True):
        """
        called from the debugger to continue running

        :param verbose: If True, will print each executed instruction to STDOUT
        """
        self._run(verbose)

    def step(self):
        """
        Execute a single instruction, then return.
        """
        if self.exit:
            print(FMT_CPU + "[CPU] Program exited with code {}".format(self.exit_code) + FMT_NONE)
        else:
            try:
                self.cycle += 1
                ins = self.mmu.read_ins(self.pc)
                print(FMT_CPU + "   Running 0x{:08X}:{} {}".format(self.pc, FMT_NONE, ins))
                self.pc += self.INS_XLEN
                self.run_instruction(ins)
            except LaunchDebuggerException:
                print(FMT_CPU + "[CPU] Returning to debugger!" + FMT_NONE)
            except RiscemuBaseException as ex:
                self.pc -= self.INS_XLEN
                print(ex.message())

    def _run(self, verbose=False):
        if self.pc <= 0:
            return False
        ins = None
        try:
            while not self.exit:
                self.cycle += 1
                ins = self.mmu.read_ins(self.pc)
                if verbose:
                    print(FMT_CPU + "   Running 0x{:08X}:{} {}".format(self.pc, FMT_NONE, ins))
                self.pc += self.INS_XLEN
                self.run_instruction(ins)
        except RiscemuBaseException as ex:
            if not isinstance(ex, LaunchDebuggerException):
                print(FMT_ERROR + "[CPU] excpetion caught at 0x{:08X}: {}:".format(self.pc - 1, ins) + FMT_NONE)
                print(ex.message())
                self.pc -= self.INS_XLEN

            if self.active_debug:
                print(FMT_CPU + "[CPU] Returning to debugger!" + FMT_NONE)
                return
            if self.conf.debug_on_exception:
                launch_debug_session(self, self.mmu, self.regs, "Exception encountered, launching debug:")

        if self.exit:
            print()
            print(FMT_CPU + "Program exited with code {}".format(self.exit_code) + FMT_NONE)
            sys.exit(self.exit_code)
        else:
            print()
            print(FMT_CPU + "Program stopped without exiting - perhaps you stopped the debugger?" + FMT_NONE)

    def __repr__(self):
        """
        Returns a representation of the CPU and some of its state.
        """
        return "{}(pc=0x{:08X}, cycle={}, exit={}, instructions={})".format(
            self.__class__.__name__,
            self.pc,
            self.cycle,
            self.exit,
            " ".join(s.name for s in self.instruction_sets)
        )
