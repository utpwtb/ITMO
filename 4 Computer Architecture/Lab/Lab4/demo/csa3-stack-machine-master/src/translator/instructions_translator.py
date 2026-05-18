from __future__ import annotations

from src.constants import IO_PORTS, OPERAND_SIZE
from src.isa import Instruction, Opcode
from src.translator.utils import find_substring_row, is_number, line_without_comment


def translate_without_operands(text: list[str]) -> tuple[dict[str, int], list[Instruction]]:
    code: list[Instruction] = []
    labels: dict[str, int] = {}

    # В 0 ячейке переход на метку `_start`
    code.append(Instruction(0, Opcode.JMP, "_start"))

    text_section_start_index: int = find_substring_row(text, ".text", "Sections .text can be declared at most once")

    for text_line in range(text_section_start_index + 1, len(text)):
        token = line_without_comment(text[text_line])

        if ".data" in token:
            break
        if not token:
            continue

        pc = len(code)

        # Токен содержит метку
        if ":" in token:
            label, other = token.split(":", 1)
            assert label not in labels, "Redefinition of label: {}".format(label)
            labels[label] = pc

            if token.endswith(":"):
                continue
            token = other.strip()

        # Токен содержит инструкцию с операндом (отделены пробелом)
        if " " in token:
            sub_tokens = token.split(" ")
            assert len(sub_tokens) == 2, "Invalid instruction: {}".format(token)

            mnemonic, arg = sub_tokens
            opcode = Opcode.from_string(mnemonic)
            assert opcode, f"There is no '{token}' Opcode"
            assert opcode in cmd_with_args(), "{} must have 0 argument".format(Opcode(opcode).name)

            code.append(Instruction(pc, opcode, arg))

        # Токен содержит инструкцию без операндов
        else:
            opcode = Opcode.from_string(token)
            assert opcode, f"There is no '{token}' Opcode"
            assert opcode not in cmd_with_args(), "{} must have 1 argument".format(Opcode(opcode).name)
            code.append(Instruction(pc, opcode))

    return labels, code


def cmd_with_args() -> set[Opcode]:
    return {
        Opcode.PUSH,
        Opcode.JMP,
        Opcode.JZ,
        Opcode.JNZ,
        Opcode.JS,
        Opcode.JNS,
        Opcode.CALL,
        Opcode.INPUT,
        Opcode.OUTPUT,
    }


def get_labels_to_num(labels2data: dict[str, list[int]]) -> dict[str, int]:
    labels2num: dict[str, int] = {}
    cur_num = 0
    for label, data in labels2data.items():
        labels2num[label] = cur_num
        cur_num += len(data)
    return labels2num


def translate_operands(labels: dict[str, int], code: list[Instruction], labels2data: dict[str, list[int]]):
    labels2num: dict[str, int] = get_labels_to_num(labels2data)
    for instruction in code:
        if instruction.operand:
            if instruction.opcode in {Opcode.INPUT, Opcode.OUTPUT}:
                instruction.operand = int(instruction.operand)
                assert (
                    0 <= instruction.operand <= IO_PORTS - 1
                ), f"Number of port must take values in [0; {IO_PORTS - 1}]"
                continue
            if instruction.opcode is Opcode.PUSH:
                if not is_number(instruction.operand):
                    instruction.operand = labels2num[instruction.operand]
                else:
                    instruction.operand = int(instruction.operand)
                    assert (
                        -(1 << OPERAND_SIZE) <= instruction.operand <= (1 << OPERAND_SIZE) - 1
                    ), f"Integer in operand must take values in [-2^{OPERAND_SIZE}; 2^{OPERAND_SIZE} - 1]"
                continue

            label = instruction.operand
            assert label in labels, "Label not defined: " + label
            instruction.operand = labels[label]
    return code


def translate_code(text: list[str], labels2data: dict[str, list[int]]) -> list[Instruction]:
    labels, code = translate_without_operands(text)
    instructions = translate_operands(labels, code, labels2data)
    for instruction in instructions:
        assert not isinstance(instruction.operand, str), f"ERR: Shouldn't be any strings in operands in {instruction}"
    return instructions
