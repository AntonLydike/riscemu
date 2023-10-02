from .cpu import CPU
from .memory_section import MemorySection

from typing import List


class Platform:
    """
    This is a wrapper around a given hardware configuration.
    """

    harts: List[CPU]

    memory: List[MemorySection]

    def __init__(self):
        pass

    def step(self):
        performed_step = False

        for cpu in self.harts:
            if not cpu.halted:
                cpu.step(cpu.conf.verbosity > 1)
                performed_step = True

        return performed_step
