from __future__ import annotations

import logging

from src.isa import Instruction, InstructionMemory, Opcode
from src.machine.components.call_stack import CallStack
from src.machine.components.io import log_io
from src.machine.data_path import DataPath

STACK_OPS = {
    Opcode.POP: lambda stack: stack.pop(),
    Opcode.DUP: lambda stack: stack.dup(),
    Opcode.OVER: lambda stack: stack.over(),
    Opcode.OVER3: lambda stack: stack.over3(),
    Opcode.SWAP: lambda stack: stack.swap(),
}


class ControlUnit:
    """Блок управления процессора. Выполняет декодирование инструкций и
    управляет состоянием модели процессора, включая обработку данных (DataPath).
    """

    program: InstructionMemory = None
    "Память команд."

    pc: int = None
    "Счётчик команд. Инициализируется нулём."

    call_stack: CallStack = None
    "Стек вызовов."

    data_path: DataPath = None
    "Блок обработки данных."

    _tick: int = None
    "Текущее модельное время процессора (в тактах). Инициализируется нулём."

    def __init__(self, program: InstructionMemory, call_stack: CallStack, data_path: DataPath):
        self.program = program
        self.pc = 0
        self.call_stack = call_stack
        self.data_path = data_path
        self._tick = 0

    def tick(self) -> None:
        """Продвинуть модельное время процессора вперёд на один такт."""
        self._tick += 1

    def current_tick(self) -> int:
        """Текущее модельное время процессора (в тактах)."""
        return self._tick

    def signal_latch_pc(self, sel_next: bool = True) -> None:
        """Защёлкнуть новое значение счётчика команд.
        Если `sel_next` равен `True`, то счётчик будет увеличен на единицу,
        иначе -- будет установлен в значение аргумента текущей инструкции.
        """
        if sel_next:
            self.pc += 1
        else:
            instr = self.program.values[self.pc]
            assert instr.operand is not None, "internal error, operand is None"
            self.pc = instr.operand

    def decode_and_execute_control_flow_instruction(self, instr: Instruction) -> bool:
        """Декодировать и выполнить инструкцию управления потоком исполнения. В
        случае успеха -- вернуть `True`, чтобы перейти к следующей инструкции.
        """
        opcode = instr.opcode

        if opcode == Opcode.HALT:
            raise StopIteration()

        sel_next = True
        if (
            opcode == Opcode.JMP
            or (opcode == Opcode.JZ and self.data_path.zero_flag)
            or (opcode == Opcode.JNZ and not self.data_path.zero_flag)
            or (opcode == Opcode.JS and self.data_path.negative_flag)
            or (opcode == Opcode.JNS and not self.data_path.negative_flag)
        ):
            sel_next = False
        elif opcode == Opcode.CALL:
            self.call_stack.push(self.pc + 1)
            sel_next = False
        elif opcode == Opcode.RET:
            instr.operand = self.call_stack.pop()
            sel_next = False

        if opcode in {
            Opcode.JMP,
            Opcode.JNZ,
            Opcode.JZ,
            Opcode.JNS,
            Opcode.JS,
            Opcode.CALL,
            Opcode.RET,
        }:
            self.signal_latch_pc(sel_next)
            self.tick()
            return True

        return False

    def decode_and_execute_instruction(self):
        instr = self.program.values[self.pc]
        opcode = instr.opcode

        if self.decode_and_execute_control_flow_instruction(instr):
            return

        if opcode == Opcode.DEBUG:
            logging.debug("DEBUG: %s", repr(self.data_path))
            logging.debug("DEBUG: %s", self.data_path.memory.memory.values)
            # Breakpoint
            input()

        if opcode in {Opcode.LOAD, Opcode.STORE}:
            self.data_path.latch_data_addr()
            self.tick()

        if opcode == Opcode.STORE:
            self.data_path.memory.signal_write(self.data_path.stack.pretop(), self.data_path.stack.top())
            self.signal_latch_pc()
            self.tick()

        elif opcode == Opcode.OUTPUT:
            symbol = self.data_path.stack.top()
            self.data_path.io_controller.signal_write(symbol, instr.operand)
            log_io(symbol, "OUTPUT")
            self.signal_latch_pc()
            self.tick()

        elif opcode in STACK_OPS.keys():
            STACK_OPS[opcode](self.data_path.stack)
            self.signal_latch_pc()
            self.tick()

        else:
            self.data_path.latch_tos(instr)
            self.signal_latch_pc()
            self.tick()

    def __repr__(self):
        if self.data_path.data_addr < len(self.data_path.memory.memory.values):
            mem_out = self.data_path.memory.memory.values[self.data_path.data_addr].value
        else:
            mem_out = 0
        state_repr = "TICK: {:3},  PC: {:3},  AR: {:3},  MEM_OUT: {:3},  TOS: {:22},".format(
            self.current_tick(),
            self.pc,
            self.data_path.data_addr,
            mem_out,
            str(self.data_path.stack),
        )

        instr = self.program.values[self.pc]
        instr_repr = instr.opcode + (" {}".format(instr.operand) if instr.operand is not None else "")
        return "{}    {:10}|".format(state_repr, instr_repr)
