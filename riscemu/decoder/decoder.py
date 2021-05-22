from .instruction_table import *
from typing import Tuple, List


def print_ins(ins: int):
    print("  f7      rs2   rs1   f3  rd    op")
    print(
        f"0b{ins >> 25 :07b}_{(ins >> 20) & 0b11111:05b}_{(ins >> 15) & 0b11111:03b}_{(ins >> 12) & 0b111:03b}_{(ins >> 7) & 0b11111:05b}_{ins & 0b1111111:07b}");


STATIC_INSN = {
    0x00000013: ("nop", []),
    0x00008067: ("ret", []),
    0xfe010113: ("addi", ["sp", "sp", -32]),
    0x02010113: ("addi", ["sp", "sp", 32]),
    0x00100073: ("ebreak", []),
    0x00000073: ("ecall", [])
}


def int_from_ins(insn: bytearray):
    return (insn[3] << (8 * 3)) + \
           (insn[2] << (8 * 2)) + \
           (insn[1] << 8) + \
           insn[0]


def name_from_insn(ins: int):
    opcode = op(ins)
    if opcode not in RV32:
        print_ins(ins)
        raise RuntimeError(f"Invalid opcode: {opcode:0x} in insn {ins:x}")
    dec = RV32[opcode]

    if isinstance(dec, str):
        return dec

    fun = funct3(ins)
    if fun not in dec:
        print_ins(ins)
        raise RuntimeError(f"Invalid funct3: {fun:0x} in insn {ins:x}")

    dec = dec[fun]
    if isinstance(dec, str):
        return dec

    if opcode == 0x1c and fun == 0:
        # we have ecall/ebreak
        token = imm110(ins)
        if token in dec:
            return dec[token]
        print_ins(ins)
        raise RuntimeError(f"Invalid instruction in ebreak/ecall region: {ins:x}")

    fun = funct7(ins)
    if fun in dec:
        if opcode == 0x0C or (opcode == 0x04 and fun == 5):
            mode = imm110(ins)
            dec = dec[fun]
            if mode in dec:
                return dec[mode]
            print_ins(ins)
            raise RuntimeError("Unknown instruction!")

        return dec[fun]

    print_ins(ins)
    raise RuntimeError(f"Invalid instruction: {ins:x}")


def decode(ins: bytearray) -> Tuple[str, List[Union[str, int]]]:
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

    return name_from_insn(insn), INSTRUCTION_ARGS_DECODER[opcode](insn)
