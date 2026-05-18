from __future__ import annotations

from src.constants import MAX_NUMBER, MIN_NUMBER, WORD_SIZE
from src.isa import Opcode

ALU_OPCODE_BINARY_HANDLERS = {
    Opcode.ADD: lambda left, right: left + right,
    Opcode.SUB: lambda left, right: left - right,
    Opcode.MUL: lambda left, right: left * right,
    Opcode.DIV: lambda left, right: left // right,
    Opcode.MOD: lambda left, right: left % right,
    Opcode.CMP: lambda left, right: left - right,
    Opcode.AND: lambda left, right: left & right,
    Opcode.OR: lambda left, right: left | right,
    Opcode.XOR: lambda left, right: left ^ right,
}


ALU_OPCODE_SINGLE_HANDLERS = {
    Opcode.INC: lambda left: left + 1,
    Opcode.DEC: lambda left: left - 1,
    Opcode.NEG: lambda left: -left,
    Opcode.NOT: lambda left: left ^ ((1 << WORD_SIZE) - 1),
}


class ALU:
    z_flag = None

    def __init__(self):
        self.z_flag = 0

    def perform(self, opcode: Opcode, left: int, right: int) -> int:
        assert (
            opcode in ALU_OPCODE_BINARY_HANDLERS or opcode in ALU_OPCODE_SINGLE_HANDLERS
        ), f"Unknown ALU command {opcode.mnemonic}"

        if opcode in ALU_OPCODE_BINARY_HANDLERS:
            value = ALU_OPCODE_BINARY_HANDLERS[opcode](left, right)
        else:
            value = ALU_OPCODE_SINGLE_HANDLERS[opcode](left)

        value = self.handle_overflow(value)
        self.set_flags(value)

        return value

    def handle_overflow(self, value: int) -> int:
        if value > MAX_NUMBER:
            value %= MAX_NUMBER
        elif value < MIN_NUMBER:
            value %= abs(MIN_NUMBER)
        return value

    def set_flags(self, value) -> None:
        if value == 0:
            self.z_flag = True
        else:
            self.z_flag = False
