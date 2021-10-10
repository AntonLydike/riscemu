from collections import defaultdict
from .formats import *

tbl = lambda: defaultdict(tbl)

RV32 = tbl()
RV32[0x1b] = "jal"
RV32[0x0D] = "lui"
RV32[0x05] = "auipc"
RV32[0x19][0] = "jalr"

RV32[0x04][0] = "addi"
RV32[0x04][1] = "slli"
RV32[0x04][2] = "slti"
RV32[0x04][3] = "sltiu"
RV32[0x04][4] = "xori"
RV32[0x04][5][0x00] = "srli"
RV32[0x04][5][0x20] = "srai"
RV32[0x04][6] = "ori"
RV32[0x04][7] = "andi"

RV32[0x18][0] = "beq"
RV32[0x18][1] = "bne"
RV32[0x18][4] = "blt"
RV32[0x18][5] = "bge"
RV32[0x18][6] = "bltu"
RV32[0x18][7] = "bgeu"

RV32[0x00][0] = "lb"
RV32[0x00][1] = "lh"
RV32[0x00][2] = "lw"
RV32[0x00][4] = "lbu"
RV32[0x00][5] = "lhu"

RV32[0x08][0] = "sb"
RV32[0x08][1] = "sh"
RV32[0x08][2] = "sw"

RV32[0x1c][1] = "csrrw"
RV32[0x1c][2] = "csrrs"
RV32[0x1c][3] = "csrrc"
RV32[0x1c][5] = "csrrwi"
RV32[0x1c][6] = "csrrsi"
RV32[0x1c][7] = "csrrci"

RV32[0x1c][0][0] = "ecall"
RV32[0x1c][0][1] = "ebreak"

RV32[0x0C][0][0]  = "add"
RV32[0x0C][0][32] = "sub"
RV32[0x0C][1][0]  = "sll"
RV32[0x0C][2][0]  = "slt"
RV32[0x0C][3][0]  = "sltu"
RV32[0x0C][4][0]  = "xor"
RV32[0x0C][5][0]  = "srl"
RV32[0x0C][5][32] = "sra"
RV32[0x0C][6][0]  = "or"
RV32[0x0C][7][0]  = "and"

# rv32m
RV32[0x0C][0][1] = "mul"
RV32[0x0C][1][1] = "mulh"
RV32[0x0C][2][1] = "mulhsu"
RV32[0x0C][3][1] = "mulhu"
RV32[0x0C][4][1] = "div"
RV32[0x0C][5][1] = "divu"
RV32[0x0C][6][1] = "rem"
RV32[0x0C][7][1] = "remu"

# rv32a
RV32[0b1011][0b10][0b00010] = "lr.w"
RV32[0b1011][0b10][0b00011] = "sc.w"
RV32[0b1011][0b10][0b00001] = "amoswap.w"
RV32[0b1011][0b10][0b00000] = "amoadd.w"
RV32[0b1011][0b10][0b00100] = "amoxor.w"
RV32[0b1011][0b10][0b01100] = "amoand.w"
RV32[0b1011][0b10][0b01000] = "amoor.w"
RV32[0b1011][0b10][0b10000] = "amomin.w"
RV32[0b1011][0b10][0b10100] = "amomax.w"
RV32[0b1011][0b10][0b11000] = "amominu.w"
RV32[0b1011][0b10][0b11100] = "amomaxu.w"
