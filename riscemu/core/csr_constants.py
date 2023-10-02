from typing import Dict, Tuple

MCAUSE_TRANSLATION: Dict[Tuple[int, int], str] = {
    (1, 0): "User software interrupt",
    (1, 1): "Supervisor software interrupt",
    (1, 3): "Machine software interrupt",
    (1, 4): "User timer interrupt",
    (1, 5): "Supervisor timer interrupt",
    (1, 7): "Machine timer interrupt",
    (1, 8): "User external interrupt",
    (1, 9): "Supervisor external interrupt",
    (1, 11): "Machine external interrupt",
    (0, 0): "Instruction address misaligned",
    (0, 1): "Instruction access fault",
    (0, 2): "Illegal instruction",
    (0, 3): "Breakpoint",
    (0, 4): "Load address misaligned",
    (0, 5): "Load access fault",
    (0, 6): "Store/AMO address misaligned",
    (0, 7): "Store/AMO access fault",
    (0, 8): "environment call from user mode",
    (0, 9): "environment call from supervisor mode",
    (0, 11): "environment call from machine mode",
    (0, 12): "Instruction page fault",
    (0, 13): "Load page fault",
    (0, 15): "Store/AMO page fault",
}
"""
Assigns tuple (interrupt bit, exception code) to their respective readable names
"""

CSR_NAME_TO_ADDR: Dict[str, int] = {
    "fflags": 0x001,
    "frm": 0x002,
    "fcsr": 0x003,
    "mstatus": 0x300,
    "misa": 0x301,
    "mie": 0x304,
    "mtvec": 0x305,
    "mepc": 0x341,
    "mcause": 0x342,
    "mtval": 0x343,
    "mip": 0x344,
    "mtimecmp": 0x780,
    "mtimecmph": 0x781,
    "halt": 0x789,
    "cycle": 0xC00,
    "time": 0xC01,
    "instret": 0xC02,
    "cycleh": 0xC80,
    "timeh": 0xC81,
    "instreth": 0xC82,
    "mvendorid": 0xF11,
    "marchid": 0xF12,
    "mimpid": 0xF13,
    "mhartid": 0xF14,
}
"""
Translation for named registers
"""
