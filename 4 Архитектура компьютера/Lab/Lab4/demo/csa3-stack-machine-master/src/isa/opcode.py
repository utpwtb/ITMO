from __future__ import annotations

from enum import StrEnum, unique


@unique
class Opcode(StrEnum):
    NOP = "nop"
    HALT = "halt"

    # Binary operators
    ADD = "add"
    SUB = "sub"
    MUL = "mul"
    DIV = "div"
    MOD = "mod"
    CMP = "cmp"
    AND = "and"
    OR = "or"
    XOR = "xor"

    # Unary operators
    INC = "inc"
    DEC = "dec"
    NEG = "neg"
    NOT = "not"

    JMP = "jmp"
    JZ = "jz"
    JNZ = "jnz"
    JS = "js"
    JNS = "jns"

    CALL = "call"
    RET = "ret"

    INPUT = "input"
    OUTPUT = "output"

    PUSH = "push"
    POP = "pop"
    SWAP = "swap"
    DUP = "dup"
    OVER = "over"
    OVER3 = "over3"

    LOAD = "load"
    STORE = "store"

    DEBUG = "debug"

    def __init__(self, mnemonic: str):
        self.mnemonic = mnemonic

    def __str__(self):
        return str(self.value)

    @classmethod
    def from_string(cls, value: str):
        value = value.lower()
        for opcode in cls:
            if opcode.mnemonic == value:
                return opcode
        return None
