from typing import List, Optional, Set

from ..colors import FMT_RED, FMT_BOLD, FMT_NONE, FMT_MEM
from ..helpers import get_section_base_name
from . import InstructionContext, T_AbsoluteAddress, MemorySection


class Program:
    """
    This represents a collection of sections which together form an executable program

    When you want to create a program which can be located anywhere in memory, set base to None,
    this signals the other components, that this is relocatable. Set the base of each section to
    the offset in the program, and everything will be taken care of for you.

    """
    name: str
    context: InstructionContext
    global_labels: Set[str]
    relative_labels: Set[str]
    sections: List[MemorySection]
    base: Optional[T_AbsoluteAddress]
    is_loaded: bool

    @property
    def size(self):
        if len(self.sections) == 0:
            return 0
        if self.base is None:
            return self.sections[-1].base + self.sections[-1].size
        return (self.sections[-1].base - self.base) + self.sections[-1].size

    def __init__(self, name: str, base: Optional[int] = None):
        self.name = name
        self.context = InstructionContext()
        self.sections = []
        self.global_labels = set()
        self.relative_labels = set()
        self.base = base
        self.is_loaded = False

    def add_section(self, sec: MemorySection):
        # print a warning when a section is located before the programs base
        if self.base is not None:
            if sec.base < self.base:
                print(
                    FMT_RED + FMT_BOLD + "WARNING: memory section {} in {} is placed before program base (0x{:x})".format(
                        sec, self.name, self.base
                    ) + FMT_NONE)

        self.sections.append(sec)
        # keep section list ordered
        self.sections.sort(key=lambda section: section.base)

    def __repr__(self):
        return "{}(name={},sections={},base={})".format(
            self.__class__.__name__, self.name, self.global_labels,
            [s.name for s in self.sections], self.base
        )

    @property
    def entrypoint(self):
        if '_start' in self.context.labels:
            return self.context.labels.get('_start')
        if 'main' in self.context.labels:
            return self.context.labels.get('main')
        for sec in self.sections:
            if get_section_base_name(sec.name) == '.text' and sec.flags.executable:
                return sec.base

    def loaded_trigger(self, at_addr: T_AbsoluteAddress):
        """
        This trigger is called when the binary is loaded and its final address in memory is determined

        This will do a small sanity check to prevent programs loading twice, or at addresses they don't
        expect to be loaded.

        Then it will finalize all relative symbols defined in it to point to the correct addresses.

        :param at_addr: the address where the program will be located
        """
        if self.is_loaded:
            if at_addr != self.base:
                raise RuntimeError("Program loaded twice at different addresses! This will probably break things!")
            return

        if self.base is not None and self.base != at_addr:
            print(FMT_MEM + 'WARNING: Program loaded at different address then expected! (loaded at {}, '
                            'but expects to be loaded at {})'.format(at_addr, self.base) + FMT_NONE)

        # check if we are relocating
        if self.base != at_addr:
            offset = at_addr if self.base is None else at_addr - self.base

            # move all sections by the offset
            for sec in self.sections:
                sec.base += offset

            # move all relative symbols by the offset
            for name in self.relative_labels:
                self.context.labels[name] += offset

        self.base = at_addr
        self.context.base_address = at_addr
