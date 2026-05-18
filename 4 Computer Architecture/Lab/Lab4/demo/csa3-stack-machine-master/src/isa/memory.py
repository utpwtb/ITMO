from __future__ import annotations

from typing import Generic, TypeVar, Union

from src.constants import MEMORY_SIZE
from src.isa.data import Data
from src.isa.instruction import Instruction

CellType = TypeVar("CellType", bound=Union[Instruction, Data])


class Memory(Generic[CellType]):
    def __init__(self, values: list[CellType], from_creator: bool = False) -> None:
        assert from_creator, "You should create XXMemory only from `create_XX_memory` method."

        assert 1 <= len(values) < MEMORY_SIZE, f"Out of memory for {type(values[0]).__name__}"

        seen = set()
        unique_address_list = [seen.add(obj.address) or obj for obj in values if obj.address not in seen]
        assert len(unique_address_list) == len(
            values
        ), f"Addresses must be unique! ({len(unique_address_list)} - unique, {len(values)} - all)"

        self.values = sorted(values, key=lambda v: v.address)

    def insert_null_cells(self) -> None:
        max_address = max(self.values, key=lambda item: item.address).address
        cell_class = self.__orig_class__.__args__[0]

        vs = []
        for i in range(0, max_address + 1):
            vs.append(next((v for v in self.values if v.address == i), cell_class.empty(i)))

        self.values = sorted(vs, key=lambda v: v.address)

    def __str__(self) -> str:
        return (
            f"{self.__orig_class__.__args__[0].NAME}: [\n  " + "\n  ".join(str(value) for value in self.values) + "\n]"
        )


DataMemory = Memory[Data]
InstructionMemory = Memory[Instruction]


def create_data_memory(values: list[Data]) -> DataMemory:
    memory = DataMemory(values, True)
    memory.insert_null_cells()
    return memory


def create_instructions_memory(values: list[Instruction]) -> InstructionMemory:
    memory = InstructionMemory(values, True)
    memory.insert_null_cells()
    return memory
