import json

from src.isa.data import Data
from src.isa.instruction import Instruction
from src.isa.memory import DataMemory, InstructionMemory, create_data_memory, create_instructions_memory
from src.isa.opcode import Opcode


def instructions_to_json(instructions: InstructionMemory) -> str:
    """Перевести инструкции в JSON."""
    instructions.insert_null_cells()
    return "[\n" + ",\n".join([i.to_json() for i in instructions.values]) + "\n]"


def data_to_json(data: DataMemory) -> str:
    """Перевести данные в JSON."""
    data.insert_null_cells()
    return "[\n" + ",\n".join([d.to_json() for d in data.values]) + "\n]"


def json_to_instructions(instructions_json: str) -> InstructionMemory:
    """Перевести JSON в инструкции."""
    return create_instructions_memory(
        [Instruction(i["address"], Opcode(i["opcode"]), i["operand"]) for i in json.loads(instructions_json)]
    )


def json_to_data(data_json: str) -> DataMemory:
    """Перевести JSON в данные."""
    return create_data_memory([Data(d["address"], d["value"]) for d in json.loads(data_json)])
