from src.isa.json_utils import data_to_json, instructions_to_json, json_to_data, json_to_instructions
from src.isa.memory import DataMemory, InstructionMemory


def write_instructions(instructions_filename: str, instructions: InstructionMemory) -> None:
    """Записать инструкции в файл."""
    with open(instructions_filename, "w", encoding="utf-8") as f:
        f.write(instructions_to_json(instructions))


def write_data(data_filename: str, data: DataMemory) -> None:
    """Записать данные в файл."""
    with open(data_filename, "w", encoding="utf-8") as f:
        f.write(data_to_json(data))


def read_instructions(instructions_filename: str) -> InstructionMemory:
    """Прочесть инструкции из файла."""
    with open(instructions_filename, encoding="utf-8") as f:
        instructions_json = f.read()
    return json_to_instructions(instructions_json)


def read_data(data_filename: str) -> DataMemory:
    """Прочесть данные из файла."""
    with open(data_filename, encoding="utf-8") as f:
        data_json = f.read()
    return json_to_data(data_json)
