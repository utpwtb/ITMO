def brainfuck_interpreter(input):
    """Brainfuck 解释器，支持 8 个命令：><+-.,[]

    命令：
    - > : 增加数据指针
    - < : 减少数据指针
    - + : 将数据指针处的 32 位值加 1
    - - : 将数据指针处的 32 位值减 1
    - . : 输出数据指针处 32 位值的低字节
    - , : 将输入字节存入数据指针处 32 位值的低字节
    - [ : 如果数据指针处的值为 0，则向前跳转到匹配的 ] 之后
    - ] : 如果数据指针处的值不为 0，则向后跳转到匹配的 [ 之后

    - 内存：30 个单元，每个单元为 32 位有符号整数，初始值为 0
    - 数据指针起始位置为 0
    - 输入结束符 -- 换行符
    - 错误时（无效命令、指针越界）返回 -1
    - 输入数据来自换行符后的剩余字符

    Python 示例参数：
        input (str): 包含 brainfuck 代码和输入数据的输入字符串。

    返回值：
        tuple: 包含输出字符串和剩余输入的元组。
    """
    line, rest = read_line(input, 0x40)
    if line is None:
        return [overflow_error_value], rest

    try:
        # 初始化 Brainfuck 状态
        memory = [0] * 30  # 30 个 32 位值单元
        data_ptr = 0
        code_ptr = 0
        output = []
        input_data = rest
        input_ptr = 0

        code = line

        # 首先验证括号匹配
        bracket_count = 0
        for c in code:
            if c == "[":
                bracket_count += 1
            elif c == "]":
                bracket_count -= 1
                if bracket_count < 0:
                    return [-1], rest  # 未匹配的闭合括号
        if bracket_count != 0:
            return [-1], rest  # 未匹配的开放括号

        while code_ptr < len(code):
            cmd = code[code_ptr]

            if cmd == ">":
                data_ptr += 1
                if data_ptr >= 30:
                    return [-1], rest
            elif cmd == "<":
                data_ptr -= 1
                if data_ptr < 0:
                    return [-1], rest
            elif cmd == "+":
                memory[data_ptr] = memory[data_ptr] + 1
                # 检查 32 位上溢
                if memory[data_ptr] > 2147483647:
                    return [overflow_error_value], rest
            elif cmd == "-":
                memory[data_ptr] = memory[data_ptr] - 1
                # 检查 32 位下溢
                if memory[data_ptr] < -2147483648:
                    return [overflow_error_value], rest
            elif cmd == ".":
                # 输出 32 位值的低字节
                byte_val = memory[data_ptr] & 0xFF
                output.append(chr(byte_val))
            elif cmd == ",":
                if input_ptr < len(input_data):
                    # 设置低字节，保留高位
                    memory[data_ptr] = (memory[data_ptr] & 0xFFFFFF00) | ord(
                        input_data[input_ptr]
                    )
                    input_ptr += 1
                else:
                    memory[data_ptr] = (
                        memory[data_ptr] & 0xFFFFFF00
                    )  # EOF 时将低字节设为 0
            elif cmd == "[":
                if memory[data_ptr] == 0:
                    # 向前跳转到匹配的 ]
                    bracket_count = 1
                    code_ptr += 1
                    while code_ptr < len(code) and bracket_count > 0:
                        if code[code_ptr] == "[":
                            bracket_count += 1
                        elif code[code_ptr] == "]":
                            bracket_count -= 1
                        code_ptr += 1
                    if bracket_count > 0:
                        return [-1], rest  # 未匹配的开放括号
                    code_ptr -= 1  # 为循环结束时的增量作调整
            elif cmd == "]":
                if memory[data_ptr] != 0:
                    # 向后跳转到匹配的 [
                    bracket_count = 1
                    code_ptr -= 1
                    while code_ptr >= 0 and bracket_count > 0:
                        if code[code_ptr] == "]":
                            bracket_count += 1
                        elif code[code_ptr] == "[":
                            bracket_count -= 1
                        code_ptr -= 1
                    if bracket_count > 0:
                        return [-1], rest  # 未匹配的闭合括号
                    code_ptr += 1  # 为循环结束时的增量作调整
            elif cmd in " \t\n\r":
                pass  # 忽略空白字符
            else:
                return [-1], rest  # 无效命令

            code_ptr += 1

        # 更新 rest 以移除已消耗的输入
        remaining_input = input_data[input_ptr:]

        return "".join(output), remaining_input

    except Exception:
        return [-1], rest


assert brainfuck_interpreter('++.\n') == ('\x02', '')
assert brainfuck_interpreter('++++++++++++++++++++++++++++++++++++++++++++++++++.\n') == ('2', '')
assert brainfuck_interpreter(',.\nA') == ('A', '')
assert brainfuck_interpreter('<\n') == ([-1], '')