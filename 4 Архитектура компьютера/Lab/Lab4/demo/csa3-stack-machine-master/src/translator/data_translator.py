from __future__ import annotations

from itertools import chain

from constants import MAX_NUMBER, MIN_NUMBER
from src.translator.utils import find_substring_row, line_without_comment

RESERVATION_KEYWORD = "res"


def make_reservation(data: list[str]) -> list[str | list[int]]:
    """Все `res x` заменить на x нулей"""
    for i in range(len(data)):
        if RESERVATION_KEYWORD in data[i]:
            reserved_words = int(data[i].replace("res", "").strip())
            data[i] = [0 for _ in range(reserved_words)]

    return data


def remove_double_comma(s: str) -> str:
    """После удаления могут появиться две запятые подряд - их нужно почистить."""
    new_s = ""
    last_is_comma: bool = False
    for x in s:
        if x == "," and not last_is_comma:
            new_s += x
            last_is_comma = True
        elif x != ",":
            new_s += x
            last_is_comma = False

    return new_s


def remove_chars_by_indexes(s: str, indexes: list[int]) -> str:
    """Удаляет из строки символы, индексы которых находятся в списке `indexes`."""
    new_s: str = ""
    for ind, x in enumerate(s):
        if ind not in indexes:
            new_s += x

    return remove_double_comma(new_s)


def get_integers(data: str, ind_chars_in_quotes: list[int]) -> list[list[int] | int]:
    int_data = remove_chars_by_indexes(data, ind_chars_in_quotes)
    int_data = line_without_comment(int_data)
    int_data = make_reservation(int_data.split(","))

    int_data = list(filter(lambda s: s != " " and s != "", int_data))
    int_data = [x if isinstance(x, list) else int(x) for x in int_data]

    for x in int_data:
        if not isinstance(x, list):
            assert MIN_NUMBER <= x <= MAX_NUMBER, "Integer must take values in the segment [-2^31; 2^31 - 1]"

    return int_data


def str2list_int(data: str) -> tuple[list[list[int]], list[int]]:
    in_quotes: bool = False

    # Массив, в котором хранятся индексы элементов, взятых в кавычки (включая кавычки)
    # Нужен, чтобы после первого прохода по данным в метке, очистить данные от строк
    ind_chars_in_quotes: list[int] = []

    # Массив, в котором на i-ой позиции пустой массив, если на i-ой позиции в data
    # был одиночный байт или резервация, иначе там была строка и этот массив
    # -- последовательность байт строки
    list_codes: list[list[int]] = [[]]

    for index, x in enumerate(data):
        if x == '"':
            in_quotes = not in_quotes
            ind_chars_in_quotes.append(index)
        elif in_quotes:
            list_codes[-1].append(ord(x))
            ind_chars_in_quotes.append(index)
        elif x == ",":
            list_codes.append([])

    # Вставляем длину строки в начало (у нас Pascal Strings)
    for lst in list_codes:
        if lst:
            lst.insert(0, len(lst))

    return list_codes, ind_chars_in_quotes


def get_codes_from_data(data_str: str) -> list[int]:
    """Из asm строки с меткой извлекает ячейки данных"""
    list_codes, ind_chars_in_quotes = str2list_int(data_str)
    int_data = get_integers(data_str, ind_chars_in_quotes)
    ind_list_codes = 0

    for x in int_data:
        cur_list = list_codes[ind_list_codes]
        while cur_list:
            ind_list_codes += 1
            cur_list = list_codes[ind_list_codes]

        if isinstance(x, list):
            for el in x:
                cur_list.append(el)
        else:
            cur_list.append(x)

    return list(chain.from_iterable(list_codes))


def get_data(lines: list[str]) -> dict[str, list[int]]:
    """Читает .data пока не встретит .text, извлекает данные."""
    num_str_decl_section: int = find_substring_row(lines, ".data", "Section .data can be declared at most once")
    label2data: dict[str, list[int]] = dict()

    for i in range(num_str_decl_section + 1, len(lines)):
        line: str = lines[i].strip()

        if ".text" in line:
            break
        if not line:
            continue

        label, data = line.split(":", 1)

        assert label.strip() not in label2data, 'Redefinition label: "{}"'.format(label.strip())
        label2data[label.strip()] = get_codes_from_data(data)

    return label2data
