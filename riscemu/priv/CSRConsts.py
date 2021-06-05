from typing import Dict, Tuple

MCAUSE_TRANSLATION: Dict[Tuple[int, int], str]= {
    (1, 0): 'User software interrupt',
    (1, 1): 'Supervisor software interrupt',
    (1, 3): 'Machine software interrupt',
    (1, 4): 'User timer interrupt',
    (1, 5): 'Supervisor timer interrupt',
    (1, 7): 'Machine timer interrupt',
    (1, 8): 'User external interrupt',
    (1, 9): 'Supervisor external interrupt',
    (1, 11): 'Machine external interrupt',
    (0, 0): 'Instruction address misaligned',
    (0, 1): 'Instruction access fault',
    (0, 2): 'Illegal instruction',
    (0, 3): 'Breakpoint',
    (0, 4): 'Load address misaligned',
    (0, 5): 'Load access fault',
    (0, 6): 'Store/AMO address misaligned',
    (0, 7): 'Store/AMO access fault',
    (0, 8): 'environment call from user mode',
    (0, 9): 'environment call from supervisor mode',
    (0, 11): 'environment call from machine mode',
    (0, 12): 'Instruction page fault',
    (0, 13): 'Load page fault',
    (0, 15): 'Store/AMO page fault',
}
"""
Assigns tuple (interrupt bit, exception code) to their respective readable names
"""

MSTATUS_OFFSETS: Dict[str, int] = {
    'uie': 0,
    'sie': 1,
    'mie': 3,
    'upie': 4,
    'spie': 5,
    'mpie': 7,
    'spp': 8,
    'mpp': 11,
    'fs': 13,
    'xs': 15,
    'mpriv': 17,
    'sum': 18,
    'mxr': 19,
    'tvm': 20,
    'tw': 21,
    'tsr': 22,
    'sd': 31
}
"""
Offsets for all mstatus bits
"""

MSTATUS_LEN_2 = ('mpp', 'fs', 'xs')
"""
All mstatus parts that have length 2. All other mstatus parts have length 1
"""

CSR_NAME_TO_ADDR: Dict[str, int] = {
    'mstatus': 0x300,
    'misa': 0x301,
    'mie': 0x304,
    'mtvec': 0x305,
    'mepc': 0x341,
    'mcause': 0x342,
    'mtval': 0x343,
    'mip': 0x344,
    'mvendorid': 0xF11,
    'marchid': 0xF12,
    'mimpid': 0xF13,
    'mhartid': 0xF14,
    'time': 0xc01,
    'timeh': 0xc81,
    'halt': 0x789,
    'mtimecmp': 0x780,
    'mtimecmph': 0x781,
}
"""
Translation for named registers
"""