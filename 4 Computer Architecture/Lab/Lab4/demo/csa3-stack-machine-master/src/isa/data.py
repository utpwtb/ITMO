import json

from src.constants import MAX_NUMBER, MEMORY_SIZE, MIN_NUMBER


class Data:
    NAME = "DATA"

    @staticmethod
    def empty(address: int):
        return Data(address, 0)

    def __init__(self, address: int, value: int) -> None:
        assert MIN_NUMBER <= value <= MAX_NUMBER, f"Data value '{value}' at {address} is out of bound."
        assert 0 <= address < MEMORY_SIZE, f"Data value '{value}' is out of memory at {address}."
        self.address = address
        self.value = value

    def __str__(self) -> str:
        return f"{(str(self.address) + ":"):<6} {self.value}"

    def to_json(self) -> str:
        return json.dumps(self, default=vars, sort_keys=True)
