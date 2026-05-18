from __future__ import annotations

import logging
from abc import ABC, abstractmethod
from typing import Callable


class IO(ABC):
    @abstractmethod
    def signal_in(self) -> int:
        pass

    @abstractmethod
    def signal_out(self, data: int):
        pass


class IOController:
    def __init__(self):
        self.io_list: dict[int:IO] = {}

    def add_io(self, io: IO, port: int) -> None:
        self.io_list.update({port: io})

    def get_io(self, port: int) -> IO:
        return self.io_list.get(port)

    def remove_io(self, port: int) -> None:
        self.io_list.pop(port)

    def signal_read(self, port: int) -> int:
        assert port in self.io_list.keys(), f"no such i/o device: {port}"

        try:
            return self.io_list.get(port).signal_in()
        except EOFError:
            logging.warning("Input buffer is empty at IO %s!", port)
            return -1

    def signal_write(self, data: int, port: int) -> None:
        assert port in self.io_list.keys(), f"no such i/o device: {port}"

        self.io_list.get(port).signal_out(data)


# INPUT 0
class IO0(IO):
    def __init__(self, data_in: list):
        self.data_in = data_in

    def signal_in(self) -> int:
        if len(self.data_in) == 0:
            raise EOFError()

        return ord(self.data_in.pop(0))

    def signal_out(self, _data: int):
        raise NotImplementedError()


# OUTPUT 1
class IO1(IO):
    """Выводит переданное слово как символ."""

    def __init__(self, _data_in: list):
        self.data_out = []

    def signal_in(self) -> int:
        raise NotImplementedError()

    def signal_out(self, data: int):
        self.data_out.append(chr(data))

    def get_received_data(self) -> list:
        return self.data_out


# OUTPUT 2
class IO2(IO):
    """Выводит переданное слово как число."""

    def __init__(self, _data_in: list):
        self.data_out = []

    def signal_in(self) -> int:
        raise NotImplementedError()

    def signal_out(self, data: int):
        self.data_out.append(str(data))

    def get_received_data(self) -> list:
        return self.data_out


# INPUT 8
class IO8(IO):
    """Отдает числа от 0 до 9."""

    def __init__(self, _data_in: list):
        self.data_in = None
        self.counter = 0

    def signal_in(self) -> int:
        self.counter += 1
        self.counter %= 10
        return ord(str(self.counter))

    def signal_out(self, _data: int):
        raise NotImplementedError()


def get_ios() -> list[tuple[int, Callable[[list[str]], int]]]:
    return {
        (0, lambda inp: IO0(inp)),
        (1, lambda _inp: IO1(None)),
        (2, lambda _inp: IO2(None)),
        (8, lambda _inp: IO8(None)),
    }


def log_io(symbol: int, name: str):
    if symbol == 0:
        logging.debug("%s: \\0", name)
    elif symbol == -1:
        logging.debug("%s: EOF", name)
    elif symbol == 10:
        logging.debug("%s: \\n", name)
    else:
        try:
            logging.debug("%s: %s", name, chr(symbol))
        except ValueError:
            logging.debug("%s: %s", name, str(symbol))
