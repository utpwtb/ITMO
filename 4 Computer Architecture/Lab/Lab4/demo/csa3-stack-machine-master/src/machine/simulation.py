from __future__ import annotations

import logging

from src.constants import MEMORY_SIZE
from src.isa import DataMemory, InstructionMemory
from src.machine.components.call_stack import CallStack
from src.machine.components.data_stack import DataStack
from src.machine.components.io import IOController, get_ios
from src.machine.components.memory import Memory
from src.machine.control_unit import ControlUnit
from src.machine.data_path import DataPath


def run(control_unit: ControlUnit, instruction_limit: int) -> tuple[int, ControlUnit]:
    instr_counter = 0
    logging.debug("%s", control_unit)
    try:
        while instr_counter < instruction_limit:
            control_unit.decode_and_execute_instruction()
            instr_counter += 1
            logging.debug("%s", control_unit)
    except EOFError:
        logging.warning("Input buffer is empty!")
    except KeyboardInterrupt:
        pass
    except StopIteration:
        pass

    if instr_counter >= instruction_limit:
        logging.warning(f"Instruction limit {instruction_limit} reached!")

    return instr_counter, control_unit


def simulation(
    instructions: InstructionMemory,
    data: DataMemory,
    input_tokens: list[str],
    stack_capacity: int,
    call_stack_capacity: int,
    instruction_limit: int,
    output_from_ports: list[int],
) -> tuple[str, int, int]:
    io_controller = IOController()
    for port, create_io in get_ios():
        io_controller.add_io(create_io(input_tokens), port)

    data_path = DataPath(DataStack(stack_capacity), Memory(data, MEMORY_SIZE), io_controller)
    control_unit = ControlUnit(instructions, CallStack(call_stack_capacity), data_path)

    instr_counter, control_unit = run(control_unit, instruction_limit)

    output_buffer = []
    logging.debug("memory: %s", data_path.memory.memory)
    for port in output_from_ports:
        out = data_path.io_controller.get_io(port).get_received_data()
        output_buffer.append("".join(out))
        logging.info("output_buffer (port %s): %s", str(port), repr("".join(out)))

    return "\n".join(output_buffer), instr_counter, control_unit.current_tick()
