from src.isa import Instruction, Opcode
from src.machine.components.alu import ALU
from src.machine.components.data_stack import DataStack
from src.machine.components.io import IOController, log_io
from src.machine.components.memory import Memory


class DataPath:
    """Тракт данных (пассивный), включая: ввод/вывод, память и арифметику."""

    def __init__(self, stack: DataStack, memory: Memory, io_controller: IOController):
        self.alu = ALU()
        self.stack = stack
        self.memory = memory
        self.io_controller = io_controller
        self.data_addr = 0
        self.zero_flag = False
        self.negative_flag = False

    def latch_tos(self, instr: Instruction) -> None:
        opcode = instr.opcode

        if opcode == Opcode.LOAD:
            self.stack.push(self.memory.signal_read(self.data_addr))
            self.signal_set_flags()

        elif opcode in {
            Opcode.ADD,
            Opcode.SUB,
            Opcode.MUL,
            Opcode.DIV,
            Opcode.MOD,
            Opcode.AND,
            Opcode.OR,
        }:
            self.stack.push(self.alu.perform(opcode, self.stack.pop(), self.stack.pop()))
            self.signal_set_flags()

        elif opcode == Opcode.CMP:
            self.stack.push(self.alu.perform(opcode, self.stack.top(), self.stack.pretop()))
            self.signal_set_flags()
            self.stack.pop()

        elif opcode in {Opcode.INC, Opcode.DEC, Opcode.NOT, Opcode.NEG}:
            self.stack.push(self.alu.perform(opcode, self.stack.pop(), 0))
            self.signal_set_flags()

        elif opcode == Opcode.INPUT:
            symbol = self.io_controller.signal_read(instr.operand)
            self.stack.push(symbol)
            log_io(symbol, "INPUT")

        elif opcode == Opcode.PUSH:
            self.stack.push(instr.operand)
            self.signal_set_flags()

    def latch_data_addr(self):
        self.data_addr = self.stack.top()

    def signal_set_flags(self):
        self.zero_flag = self.stack.top() == 0
        self.negative_flag = self.stack.top() < 0
