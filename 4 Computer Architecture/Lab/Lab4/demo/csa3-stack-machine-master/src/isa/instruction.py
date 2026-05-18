from __future__ import annotations

import json

from src.constants import MEMORY_SIZE
from src.isa.opcode import Opcode


class Instruction:
    NAME = "INSTRUCTION"

    @staticmethod
    def empty(address: int):
        return Instruction(address, Opcode.NOP)

    def __init__(self, address: int, opcode: Opcode, operand: int | str | None = None) -> None:
        assert 0 <= address < MEMORY_SIZE, f"Instruction '{opcode}'at {address} is out of memory"
        self.address = address
        self.opcode = opcode
        self.operand = operand

    def __str__(self) -> str:
        return f"{(str(self.address) + ":"):<6} {self.opcode.name:<6} " + (
            f"{"'" + self.operand + "'" if isinstance(self.operand, str) else self.operand}"
            if self.operand is not None
            else ""
        )

    def to_json(self) -> str:
        return json.dumps(self, default=vars, sort_keys=True)
