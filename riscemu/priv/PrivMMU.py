from .types import ElfMemorySection
from ..MMU import *
from abc import abstractmethod

import typing

if typing.TYPE_CHECKING:
    from .PrivCPU import PrivCPU


class PrivMMU(MMU):

    def get_sec_containing(self, addr: T_AbsoluteAddress) -> MemorySection:
        # try to get an existing section
        existing_sec = super().get_sec_containing(addr)

        if existing_sec is not None:
            return existing_sec

        # get section preceding empty space at addr
        sec_before = next((sec for sec in reversed(self.sections) if sec.end < addr), None)
        # get sec succeeding empty space at addr
        sec_after = next((sec for sec in self.sections if sec.base > addr), None)

        # calc start end end of "free" space
        prev_sec_end = 0 if sec_before is None else sec_before.end
        next_sec_start = 0x7FFFFFFF if sec_after is None else sec_after.base

        # start at the end of the prev section, or current address - 0xFFFF (aligned to 16 byte boundary)
        start = max(prev_sec_end, align_addr(addr - 0xFFFF, 16))
        # end at the start of the next section, or address + 0xFFFF (aligned to 16 byte boundary)
        end = min(next_sec_start, align_addr(addr + 0xFFFF, 16))

        sec = ElfMemorySection(bytearray(end - start), '.empty', self.global_instruction_context(), '', start, MemoryFlags(False, True))
        self.sections.append(sec)
        self._update_state()

        return sec

    def global_instruction_context(self) -> InstructionContext:
        context = InstructionContext()
        context.global_symbol_dict = self.global_symbols
        return context