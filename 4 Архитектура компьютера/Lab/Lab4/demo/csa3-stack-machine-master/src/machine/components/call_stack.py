from __future__ import annotations

from src.constants import CALL_STACK_CAPACITY


class CallStack:
    stack: list[int]
    _top: int
    stack_size: int

    def __init__(self, stack_size: int = CALL_STACK_CAPACITY):
        self.stack_size = stack_size
        self.stack = [0 for _ in range(stack_size)]
        self._top = 0

    def push(self, value: int):
        assert self._top < self.stack_size, "call stack overflow"
        self.stack[self._top] = value
        self._top += 1

    def pop(self) -> int:
        assert self._top >= 1, "call stack underflow"
        self._top -= 1
        return self.stack[self._top]
