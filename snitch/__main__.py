"""
RiscEmu (c) 2021 Anton Lydike

SPDX-License-Identifier: MIT

This file holds the logic for starting the emulator from the CLI
"""
import sys

from .regs import StreamingRegs
from .xssr import Xssr_pseudo
from .frep import FrepEnabledCpu, Xfrep
from riscemu.riscemu_main import RiscemuMain


class SnitchMain(RiscemuMain):
    def instantiate_cpu(self):
        self.cpu = FrepEnabledCpu(self.selected_ins_sets, self.cfg)
        self.cpu.regs = StreamingRegs(self.cpu.mmu)
        self.configure_cpu()

    def register_all_isas(self):
        super().register_all_isas()
        self.available_ins_sets.update({"Xssr": Xssr_pseudo, "Xfrep": Xfrep})


if __name__ == "__main__":
    SnitchMain().run_from_cli(sys.argv)
