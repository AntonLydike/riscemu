from typing import Dict, Callable, List, Union
from .regs import RISCV_REGS

def op(ins: int):
    return (ins >> 2) & 31


def rd(ins: int):
    return (ins >> 7) & 31


def funct3(ins: int):
    return (ins >> 12) & 7


def rs1(ins: int):
    return (ins >> 15) & 31


def rs2(ins: int):
    return (ins >> 20) & 31


def funct7(ins: int):
    return ins >> 25


def imm110(ins: int):
    return ins >> 20


def imm3112(ins: int):
    return ins >> 12


def imm_i(ins: int):
    return sign_extend(imm110(ins), 12)


def imm_s(ins: int):
    num = (funct7(ins) << 5) + rd(ins)
    return sign_extend(num, 12)


def imm_b(ins: int):
    lower = rd(ins)
    higher = funct7(ins)

    num = (lower & 0b11110) + ((higher & 0b0111111) << 5) + ((lower & 1) << 11) + ((higher >> 6) << 12)
    return sign_extend(num, 13)


def imm_u(ins: int):
    return sign_extend(imm3112(ins), 20)


def imm_j(ins: int):
    return sign_extend(
        (((ins >> 21) & 0b1111111111) << 1) +
        (((ins >> 20) & 1) << 11) +
        (((ins >> 12) & 0b11111111) << 12) +
        (((ins >> 31) & 1) << 20), 21
    )


def sign_extend(num, bits):
    sign_mask = 1 << (bits - 1)
    return (num & (sign_mask - 1)) - (num & sign_mask)


def decode_i(ins: int) -> List[int]:
    return [rd(ins), rs1(ins), imm_i(ins)]


def decode_b(ins: int) -> List[int]:
    return [rs1(ins), rs2(ins), imm_b(ins)]


def decode_u(ins: int) -> List[int]:
    return [rd(ins), imm_u(ins)]


def decode_r(ins: int) -> List[int]:
    return [rd(ins), rs1(ins), rs2(ins)]


def decode_s(ins: int) -> List[int]:
    return [rs2(ins), rs1(ins), imm_s(ins)]


def decode_j(ins: int) -> List[int]:
    return [rd(ins), imm_j(ins)]


def decode_i_shamt(ins: int) -> List[int]:
    if funct3(ins) in (1, 5):
        return [rd(ins), rs1(ins), rs2(ins)]
    return decode_i(ins)


def decode_i_unsigned(ins: int) -> List[int]:
    return [rd(ins), rs1(ins), imm110(ins)]


INSTRUCTION_ARGS_DECODER: Dict[int, Callable[[int], List[int]]] = {
    0x00: decode_i,
    0x04: decode_i_shamt,
    0x05: decode_u,
    0x08: decode_s,
    0x0C: decode_r,
    0x0D: decode_u,
    0x18: decode_b,
    0x19: decode_i,
    0x1b: decode_j,
    0x1c: decode_i_unsigned,
    0b1011: decode_r
}
