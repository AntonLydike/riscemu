from .formats import INSTRUCTION_ARGS_DECODER, op, decode_i, decode_r, decode_u, decode_b, decode_j, decode_s, \
    decode_i_shamt, decode_i_unsigned
from .regs import RISCV_REGS


def int_to_hex(num: int):
    if num < 0:
        return f"-0x{-num:x}"
    return f"0x{num:x}"


def format_ins(ins: int, name: str, fmt: str = 'int'):
    opcode = op(ins)
    if fmt == 'hex':
        fmt = int_to_hex
    else:
        fmt = str

    if opcode not in INSTRUCTION_ARGS_DECODER:
        return f"{name} <unknown op>"

    decoder = INSTRUCTION_ARGS_DECODER[opcode]
    if name in ('ecall', 'ebreak', 'mret', 'sret', 'uret'):
        return name
    if opcode in (0x8, 0x0):
        r1, r2, imm = decoder(ins)
        return f"{name:<7} {RISCV_REGS[r1]}, {imm}({RISCV_REGS[r2]})"
    elif decoder in (decode_i, decode_i_unsigned, decode_b, decode_i_shamt, decode_s):
        r1, r2, imm = decoder(ins)
        r1, r2 = RISCV_REGS[r1], RISCV_REGS[r2]
        return f"{name:<7} {r1}, {r2}, {fmt(imm)}"
    elif decoder in (decode_r,):
        rd, rs1, rs2 = [RISCV_REGS[x] for x in decoder(ins)]
        return f"{name:<7} {rd}, {rs1}, {rs2}"
    elif decoder in (decode_j, decode_u):
        r1, imm = decoder(ins)
        return f"{name:<7} {RISCV_REGS[r1]}, {fmt(imm)}"

    return f"{name} <unknown decoder>"
