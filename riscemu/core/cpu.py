from abc import ABC, abstractmethod
from typing import List, Type, Callable, Set, Dict, TYPE_CHECKING

from ..config import RunConfig
from ..colors import FMT_NONE, FMT_CPU
from . import (
    T_AbsoluteAddress,
    Instruction,
    Program,
    PrivModes,
    MMU,
    UInt32,
    Registers,
    CSR,
    RTClock,
    csr_constants,
)

if TYPE_CHECKING:
    # from core.mmu import MMU
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

    # control and status things:
    hart_id: int
    mode: PrivModes
    csr: CSR
    rtclock: RTClock

    def __init__(
        self,
        mmu: "MMU",
        instruction_sets: List[Type["InstructionSet"]],
        conf: RunConfig,
    ):
        self.mmu = mmu
        self.regs = Registers(conf.unlimited_registers, conf.flen)
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
        self.hart_id = 0
        self.debugger_active = False
        self.csr = CSR()
        self.rtclock = RTClock(conf.rtclock_tickrate)

    def run_instruction(self, ins: Instruction):
        """
        Execute a single instruction

        :param ins: The instruction to execute
        """
        try:
            self.instructions[ins.name](ins)
        except KeyError as ex:
            raise RuntimeError("Unknown instruction: {}".format(ins)) from ex

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

    def initialize_registers(self):
        # set a0 to the hartid
        self.regs.set("a0", UInt32(self.hart_id))

    def launch(self, verbose: bool = False):
        entrypoint = self.mmu.find_entrypoint()

        if entrypoint is None:
            entrypoint = self.mmu.programs[0].entrypoint

        self.initialize_registers()
        self.setup_csr()

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

    @property
    def sections(self):
        return self.mmu.sections

    @property
    def programs(self):
        return self.mmu.programs

    def setup_csr(self):
        """
        Set up standard CSR registers, can be hooked into when subclassing to provide
        more information.
        """

        self.csr.set(CSR.name_to_addr("mhartid"), UInt32(self.hart_id))
        self.csr.register_callback(
            CSR.name_to_addr("time"),
            getter=self.rtclock.get_low32,
        )
        self.csr.register_callback(
            CSR.name_to_addr("timeh"),
            getter=self.rtclock.get_hi32,
        )
        self.csr.register_callback(
            CSR.name_to_addr("instret"),
            getter=(lambda csr, _: UInt32(self.cycle)),
        )
        self.csr.register_callback(
            CSR.name_to_addr("instreth"),
            getter=(lambda csr, _: UInt32(self.cycle >> 32)),
        )
        self.csr.register_callback(
            CSR.name_to_addr("cycle"),
            getter=(lambda csr, _: UInt32(self.cycle)),
        )
        self.csr.register_callback(
            CSR.name_to_addr("cycleh"),
            getter=(lambda csr, _: UInt32(self.cycle >> 32)),
        )
