"""
RiscEmu (c) 2021 Anton Lydike

SPDX-License-Identifier: MIT

This file contains the CPU logic (not the individual instruction sets). See instructions/InstructionSet.py for more info
on them.
"""
import sys
from typing import Tuple, List, Dict, Callable, Type

from .Tokenizer import RiscVTokenizer
from .Executable import MemoryFlags
from .Syscall import SyscallInterface, get_syscall_symbols
from .Exceptions import RiscemuBaseException, LaunchDebuggerException
from .MMU import MMU
from .Config import RunConfig
from .Registers import Registers
from .debug import launch_debug_session
from .colors import FMT_CPU, FMT_NONE, FMT_ERROR

import riscemu

import typing

if typing.TYPE_CHECKING:
    from . import Executable, LoadedExecutable, LoadedInstruction
    from .instructions.InstructionSet import InstructionSet


class CPU:
    """
    This class represents a single CPU. It holds references to it's mmu, registers and syscall interrupt handler.

    It is initialized with a configuration and a list of instruction sets.
    """
    def __init__(self, conf: RunConfig, instruction_sets: List[Type['riscemu.InstructionSet']]):
        """
        Creates a CPU instance.

        :param conf: An instance of the current RunConfiguration
        :param instruction_sets: A list of instruction set classes. These must inherit from the InstructionSet class
        """
        # setup CPU states
        self.pc = 0
        self.cycle = 0
        self.exit = False
        self.exit_code = 0
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

    def get_tokenizer(self, tokenizer_input):
        """
        Returns a tokenizer that respects the language of the CPU

        :param tokenizer_input: an instance of the RiscVTokenizerInput class
        """
        return RiscVTokenizer(tokenizer_input, self.all_instructions())

    def load(self, e: riscemu.Executable):
        """
        Load an executable into Memory
        """
        return self.mmu.load_bin(e)

    def run_loaded(self, le: 'riscemu.LoadedExecutable'):
        """
        Run a loaded executable
        """
        self.pc = le.run_ptr

        if self.conf.stack_size > 0:
            self.stack = self.mmu.allocate_section("stack", self.conf.stack_size, MemoryFlags(False, False))
            self.regs.set('sp', self.stack.base + self.stack.size)
            print(FMT_CPU + '[CPU] Allocated {} bytes of stack'.format(self.stack.size) + FMT_NONE)

        print(FMT_CPU + '[CPU] Started running from 0x{:08X} ({})'.format(le.run_ptr, le.name) + FMT_NONE)
        self.__run()

    def continue_from_debugger(self, verbose=True):
        """
        called from the debugger to continue running

        :param verbose: If True, will print each executed instruction to STDOUT
        """
        self.__run(verbose)

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
                self.pc += 1
                self.__run_instruction(ins)
            except LaunchDebuggerException:
                print(FMT_CPU + "[CPU] Returning to debugger!" + FMT_NONE)
            except RiscemuBaseException as ex:
                self.pc -= 1
                print(ex.message())

    def __run(self, verbose=False):
        if self.pc <= 0:
            return False
        ins = None
        try:
            while not self.exit:
                self.cycle += 1
                ins = self.mmu.read_ins(self.pc)
                if verbose:
                    print(FMT_CPU + "   Running 0x{:08X}:{} {}".format(self.pc, FMT_NONE, ins))
                self.pc += 1
                self.__run_instruction(ins)
        except RiscemuBaseException as ex:
            if not isinstance(ex, LaunchDebuggerException):
                print(FMT_ERROR + "[CPU] excpetion caught at 0x{:08X}: {}:".format(self.pc - 1, ins) + FMT_NONE)
                print(ex.message())
                self.pc -= 1

            if self.active_debug:
                print(FMT_CPU + "[CPU] Returning to debugger!" + FMT_NONE)
                return
            if self.conf.debug_on_exception:
                launch_debug_session(self, self.mmu, self.regs,
                                     "Exception encountered, launching debug:")

        if self.exit:
            print()
            print(FMT_CPU + "Program exited with code {}".format(self.exit_code) + FMT_NONE)
            sys.exit(self.exit_code)
        else:
            print()
            print(FMT_CPU + "Program stopped without exiting - perhaps you stopped the debugger?" + FMT_NONE)

    def __run_instruction(self, ins: 'LoadedInstruction'):
        if ins.name in self.instructions:
            self.instructions[ins.name](ins)
        else:
            # this should never be reached, as unknown instructions are imparseable
            raise RuntimeError("Unknown instruction: {}".format(ins))

    def all_instructions(self) -> List[str]:
        """
        Return a list of all instructions this CPU can execute.
        """
        return list(self.instructions.keys())

    def __repr__(self):
        """
        Returns a representation of the CPU and some of its state.
        """
        return "CPU(pc=0x{:08X}, cycle={}, exit={}, instructions={})".format(
            self.pc,
            self.cycle,
            self.exit,
            " ".join(s.name for s in self.instruction_sets)
        )
