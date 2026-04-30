from __future__ import annotations

from src.constants import MEMORY_SIZE
from src.isa import Data, DataMemory, create_data_memory


class Memory:
    memory: DataMemory = None
    memory_size: int = None

    def __init__(self, memory: DataMemory, memory_size: int = MEMORY_SIZE):
        self.memory = memory
        self.memory_size = memory_size

    def signal_read(self, addr: int) -> int:
        assert 0 <= addr <= self.memory_size, f"Reading from not existing address: {addr}"

        if addr < len(self.memory.values):
            return self.memory.values[addr].value

        return 0

    def signal_write(self, addr: int, data: int) -> None:
        assert 0 <= addr < self.memory_size, f"Writing to not existing address: {addr}"

        if addr < len(self.memory.values):
            self.memory.values[addr] = Data(addr, data)
        else:
            new_memory = [*self.memory.values, Data(addr, data)]
            self.memory = create_data_memory(new_memory)
