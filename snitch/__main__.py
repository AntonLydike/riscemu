"""
RiscEmu (c) 2021 Anton Lydike

SPDX-License-Identifier: MIT

This file holds the logic for starting the emulator from the CLI
"""
import sys

from .regs import StreamingRegs
from .xssr import RV32_Xssr_pseudo
from riscemu.riscemu_main import RiscemuMain


class SnitchMain(RiscemuMain):
    def configure_cpu(self):
        super().configure_cpu()
        self.cpu.regs = StreamingRegs(self.cpu.mmu)

    def register_all_isas(self):
        super().register_all_isas()
        self.available_ins_sets.update({"Xssr": RV32_Xssr_pseudo})


if __name__ == "__main__":
    SnitchMain().run_from_cli(sys.argv)
