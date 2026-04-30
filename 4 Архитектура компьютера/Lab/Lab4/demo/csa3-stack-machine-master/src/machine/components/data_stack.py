from __future__ import annotations

from src.constants import STACK_CAPACITY


class DataStack:
    stack: list[int]
    _top: int
    stack_size: int

    def __init__(self, stack_size: int = STACK_CAPACITY):
        self.stack_size = stack_size
        self.stack = [0 for _ in range(stack_size)]
        self._top = 0

    def push(self, value: int):
        assert self._top < self.stack_size, "data stack overflow"
        self.stack[self._top] = value
        self._top += 1

    def pop(self) -> int:
        assert self._top >= 1, "data stack underflow"
        self._top -= 1
        return self.stack[self._top]

    def top(self) -> int:
        assert self._top >= 1, "data stack underflow"
        return self.stack[self._top - 1]

    def pretop(self) -> int:
        assert self._top >= 2, "data stack underflow"
        return self.stack[self._top - 2]

    def over(self) -> None:
        assert self._top >= 2, "data stack underflow"
        self.push(self.stack[self._top - 2])

    def over3(self) -> None:
        assert self._top >= 3, "data stack underflow"
        self.push(self.stack[self._top - 3])

    def dup(self):
        self.push(self.top())

    def swap(self):
        assert self._top >= 2, "data stack underflow"
        [self.stack[self._top - 1], self.stack[self._top - 2]] = [
            self.stack[self._top - 2],
            self.stack[self._top - 1],
        ]

    def __repr__(self):
        stack_repr = "["
        if 1 <= self._top:
            stack_repr += f"{self.stack[self._top-1]!s}"
        if 2 <= self._top:
            stack_repr += f", {self.stack[self._top - 2]!s}"
        if 3 <= self._top:
            stack_repr += f", {self.stack[self._top - 3]!s}"
        if 4 <= self._top:
            stack_repr += f", {self.stack[self._top - 4]!s}"
        if 5 <= self._top:
            stack_repr += f",... +{self._top - 4}"
        return stack_repr + "]"
