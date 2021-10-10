"""
RiscEmu (c) 2021 Anton Lydike

SPDX-License-Identifier: MIT

The priv Module holds everything necessary for emulating privileged risc-v assembly


Running priv is only preferable to the normal userspace emulator, if you actually want to emulate the whole system.

Syscalls will have to be intercepted by your assembly code.


The PrivCPU Implements the Risc-V M/U Model, meaning there is machine mode and user mode. No PMP or paging is available.
"""