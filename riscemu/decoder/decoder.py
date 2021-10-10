from .instruction_table import *
from typing import Tuple, List


def print_ins(ins: int):
    print("  f7      rs2   rs1   f3  rd    op")
    print(
        f"0b{ins >> 25 :07b}_{(ins >> 20) & 0b11111:05b}_{(ins >> 15) & 0b11111:05b}_{(ins >> 12) & 0b111:03b}_{(ins >> 7) & 0b11111:05b}_{ins & 0b1111111:07b}");


STATIC_INSN: Dict[int, Tuple[str, List[int], int]] = {
    0x00000013: ("nop", [], 0x00000013),
    0x00008067: ("ret", [], 0x00008067),
    0xfe010113: ("addi", [2, 2, -32], 0xfe010113),
    0x02010113: ("addi", [2, 2, 32], 0x02010113),
    0x00100073: ("ebreak", [], 0x00100073),
    0x00000073: ("ecall", [], 0x00000073),
    0x30200073: ("mret", [], 0x30200073),
    0x00200073: ("uret", [], 0x00200073),
    0x10200073: ("sret", [], 0x10200073),
    0x10500073: ("wfi", [], 0x10500073),
}


def int_from_ins(insn: bytearray):
    return int.from_bytes(insn, 'little')


def name_from_insn(ins: int):
    opcode = op(ins)
    if opcode not in RV32:
        print_ins(ins)
        raise RuntimeError(f"Invalid opcode: {opcode:0x} in insn {ins:x}")
    dec = RV32[opcode]

    if isinstance(dec, str):
        return dec

    fun3 = funct3(ins)
    if fun3 not in dec:
        print_ins(ins)
        raise RuntimeError(f"Invalid funct3: {fun3:0x} in insn {ins:x}")

    dec = dec[fun3]
    if isinstance(dec, str):
        return dec

    if opcode == 0x1c and fun3 == 0:
        # we have ecall/ebreak
        token = imm110(ins)
        if token in dec:
            return dec[token]
        print_ins(ins)
        raise RuntimeError(f"Invalid instruction in ebreak/ecall region: {ins:x}")

    fun7 = funct7(ins)
    if opcode == 0b1011 and fun3 == 0b10:
        # ignore the two aq/lr bits located in the fun7 block
        # riscemu has no memory reordering, therefore we don't need to look at these bits ever
        fun7 = fun7 >> 2

    if fun7 in dec:
        if opcode == 0x0C or (opcode == 0x04 and fun3 == 5):
            dec = dec[fun7]
            return dec
        print("unknown instruction?!")
        return dec[fun7]

    print_ins(ins)
    raise RuntimeError(f"Invalid instruction: {ins:x}")


def decode(ins: Union[bytearray, bytes]) -> Tuple[str, List[int], int]:
    insn = int_from_ins(ins)

    if insn & 3 != 3:
        print_ins(insn)
        raise RuntimeError("Not a RV32 instruction!")

    if insn in STATIC_INSN:
        return STATIC_INSN[insn]

    opcode = op(insn)
    if opcode not in INSTRUCTION_ARGS_DECODER:
        print_ins(insn)
        raise RuntimeError("No instruction decoder found for instruction")

    return name_from_insn(insn), INSTRUCTION_ARGS_DECODER[opcode](insn), insn
