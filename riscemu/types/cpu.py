from abc import ABC, abstractmethod
from typing import List, Type, Callable, Set, Dict, TYPE_CHECKING, Iterable

from ..registers import Registers
from ..config import RunConfig
from ..colors import FMT_NONE, FMT_CPU
from . import T_AbsoluteAddress, Instruction, Program, ProgramLoader

if TYPE_CHECKING:
    from ..MMU import MMU
    from ..instructions import InstructionSet


class CPU(ABC):
    # static cpu configuration
    INS_XLEN: int = 4

    # housekeeping variables
    regs: Registers
    mmu: "MMU"
    pc: T_AbsoluteAddress
    cycle: int
    halted: bool

    # debugging context
    debugger_active: bool

    # instruction information
    instructions: Dict[str, Callable[[Instruction], None]]
    instruction_sets: Set["InstructionSet"]

    # configuration
    conf: RunConfig

    def __init__(
        self,
        mmu: "MMU",
        instruction_sets: List[Type["InstructionSet"]],
        conf: RunConfig,
    ):
        self.mmu = mmu
        self.regs = Registers(conf.unlimited_registers)
        self.conf = conf

        self.instruction_sets = set()
        self.instructions = dict()

        for set_class in instruction_sets:
            ins_set = set_class(self)
            self.instructions.update(ins_set.load())
            self.instruction_sets.add(ins_set)

        self.halted = False
        self.cycle = 0
        self.pc = 0
        self.debugger_active = False

    def run_instruction(self, ins: Instruction):
        """
        Execute a single instruction

        :param ins: The instruction to execute
        """
        if ins.name in self.instructions:
            self.instructions[ins.name](ins)
        else:
            # this should never be reached, as unknown instructions are imparseable
            raise RuntimeError("Unknown instruction: {}".format(ins))

    def load_program(self, program: Program):
        self.mmu.load_program(program)

    def __repr__(self):
        """
        Returns a representation of the CPU and some of its state.
        """
        return "{}(pc=0x{:08X}, cycle={}, halted={} instructions={})".format(
            self.__class__.__name__,
            self.pc,
            self.cycle,
            self.halted,
            " ".join(s.name for s in self.instruction_sets),
        )

    @abstractmethod
    def step(self, verbose: bool = False):
        pass

    @abstractmethod
    def run(self, verbose: bool = False):
        pass

    def launch(self, verbose: bool = False):
        entrypoint = self.mmu.find_entrypoint()

        if entrypoint is None:
            entrypoint = self.mmu.programs[0].entrypoint

        if self.conf.verbosity > 0:
            print(
                FMT_CPU
                + "[CPU] Started running from {}".format(
                    self.mmu.translate_address(entrypoint)
                )
                + FMT_NONE
            )
        self.pc = entrypoint
        self.run(verbose)

    @classmethod
    @abstractmethod
    def get_loaders(cls) -> Iterable[Type[ProgramLoader]]:
        pass

    def get_best_loader_for(self, file_name: str) -> Type[ProgramLoader]:
        return max(self.get_loaders(), key=lambda ld: ld.can_parse(file_name))

    @property
    def sections(self):
        return self.mmu.sections

    @property
    def programs(self):
        return self.mmu.programs
