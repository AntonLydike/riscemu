"""
RiscEmu (c) 2021-2022 Anton Lydike

SPDX-License-Identifier: MIT

This file contains the CPU logic (not the individual instruction sets). See instructions/instruction_set.py for more info
on them.
"""
import typing
from typing import List, Type

from ..config import RunConfig
from ..colors import FMT_CPU, FMT_NONE, FMT_ERROR, FMT_GRAY, FMT_CYAN
from ..debug import launch_debug_session
from ..syscall import SyscallInterface, get_syscall_symbols
from . import (
    CPU,
    Int32,
    BinaryDataMemorySection,
    MMU,
    RiscemuBaseException,
    LaunchDebuggerException,
    PrivModes,
    Instruction,
    SimpleInstruction,
)

if typing.TYPE_CHECKING:
    from ..instructions import InstructionSet


class UserModeCPU(CPU):
    """
    This class represents a single CPU. It holds references to it's mmu, registers and syscall interrupt handler.

    It is initialized with a configuration and a list of instruction sets.
    """

    def __init__(self, instruction_sets: List[Type["InstructionSet"]], conf: RunConfig):
        """
        Creates a CPU instance.

        :param instruction_sets: A list of instruction set classes. These must inherit from the InstructionSet class
        """
        # setup CPU states
        super().__init__(MMU(), instruction_sets, conf)

        self.exit_code = 0

        # setup syscall interface
        self.syscall_int = SyscallInterface()

        # add global syscall symbols, but don't overwrite any user-defined symbols
        syscall_symbols = get_syscall_symbols()
        syscall_symbols.update(self.mmu.global_symbols)
        self.mmu.global_symbols.update(syscall_symbols)
        self.mode = PrivModes.USER

    def step(self, verbose: bool = False):
        """
        Execute a single instruction, then return.
        """
        launch_debugger = False

        try:
            self.cycle += 1
            ins = self.mmu.read_ins(self.pc)
            if verbose:
                if self.conf.verbosity > 2:
                    ins_str = self._format_ins(ins)
                else:
                    ins_str = str(ins)
                print(FMT_CPU + "   0x{:08X}:{} {}".format(self.pc, FMT_NONE, ins_str))
            self.pc += self.INS_XLEN
            self.run_instruction(ins)
        except RiscemuBaseException as ex:
            if isinstance(ex, LaunchDebuggerException):
                # if the debugger is active, raise the exception to
                if self.debugger_active:
                    raise ex

                print(FMT_CPU + "[CPU] Debugger launch requested!" + FMT_NONE)
                launch_debugger = True
            else:
                print(ex.message())
                ex.print_stacktrace()
                print(FMT_CPU + "[CPU] Halting due to exception!" + FMT_NONE)
                self.halted = True

        if launch_debugger:
            launch_debug_session(self)

    def run(self, verbose: bool = False):
        while not self.halted:
            self.step(verbose)

        if self.conf.verbosity > 0:
            print(
                FMT_CPU
                + "[CPU] Program exited with code {}".format(self.exit_code)
                + FMT_NONE
            )

    def setup_stack(self, stack_size: int = 1024 * 4) -> bool:
        """
        Create program stack and populate stack pointer
        :param stack_size: the size of the required stack, defaults to 4Kib
        :return:
        """
        stack_sec = BinaryDataMemorySection(
            bytearray(stack_size),
            ".stack",
            None,  # FIXME: why does a binary data memory section require a context?
            "",
            0,
        )

        if not self.mmu.load_section(stack_sec, fixed_position=False):
            print(FMT_ERROR + "[CPU] Could not insert stack section!" + FMT_NONE)
            return False

        self.regs.set("sp", Int32(stack_sec.base + stack_sec.size))

        if self.conf.verbosity > 1:
            print(
                FMT_CPU
                + "[CPU] Created stack of size {} at 0x{:x}".format(
                    stack_size, stack_sec.base
                )
                + FMT_NONE
            )

        return True

    def _format_arg(self, arg: str, ins: Instruction) -> str:
        if arg in self.regs.vals or arg in self.regs.valid_regs:
            return "{}{}=0x{:x}{}".format(
                arg, FMT_GRAY, self.regs.get(arg, False), FMT_NONE
            )
        elif arg in self.regs.float_vals or arg in self.regs.float_regs:
            return "{}{}={}{}".format(arg, FMT_GRAY, self.regs.get_f(arg), FMT_NONE)
        elif isinstance(ins, SimpleInstruction):
            val = ins.context.resolve_label(arg)
            if val is None:
                val = ins.context.resolve_numerical_label(arg, ins.addr)
            if val is None:
                return FMT_CYAN + arg + FMT_NONE
            return "{}{}=0x{:x}{}".format(arg, FMT_GRAY, val, FMT_NONE)

    def _format_ins(self, ins: Instruction) -> str:
        args = ", ".join(self._format_arg(arg, ins) for arg in ins.args)
        return "{}\t{}".format(ins.name, args)
