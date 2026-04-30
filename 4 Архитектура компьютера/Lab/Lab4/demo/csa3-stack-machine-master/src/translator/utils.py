from __future__ import annotations

COMMENT_SIGN = ";"


def line_without_comment(line: str) -> str:
    """Удаление комментариев в строке."""
    return line.split(COMMENT_SIGN, 1)[0].strip()


def is_number(s: str) -> bool:
    if len(s) <= 1:
        return s.isdigit()
    return s.isdigit() or (s[1::].isdigit() and s[0] in {"+", "-"})


def find_substring_row(text: list[str], substr, not_unique_err_msg) -> int:
    num_str_decl_section: int = -1

    for index, line in enumerate(text):
        if substr in line:
            assert num_str_decl_section == -1, "Sections .data/.text can be declared at most once"
            num_str_decl_section = index

    return num_str_decl_section
