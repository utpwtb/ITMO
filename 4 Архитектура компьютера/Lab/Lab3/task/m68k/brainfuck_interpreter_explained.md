# `brainfuck_interpreter.s` 逐行说明

本文档按源文件行号说明 Wrench M68k 版 Brainfuck 解释器的实现。行为与 [brainfuck_interpreter.py](brainfuck_interpreter.py) 一致：30 个 32 位有符号单元、MMIO `0x80` 输入 / `0x84` 输出、换行结束一行代码、行宽与 `read_line(..., 0x40)` 对齐（最多 63 个非换行字符）等。

---

## 寄存器约定（全程尽量遵守）

| 寄存器 | 用途 |
|--------|------|
| **A0** | 输入端口地址（从流读字） |
| **A1** | 输出端口地址（向流写字） |
| **A3** | 仅用于填充括号表时指向 `bracket_stack` |
| **A4** | 始终指向 `code_buffer`（代码字节区） |
| **A5** | 始终指向 `bf_memory`（数据格，每项 4 字节） |
| **A6** | 临时：读 `bracket_fwd` / `bracket_back` 时的基址 |
| **D0–D1** | 通用临时 / 比较、输入输出 |
| **D2** | **代码指针** `code_ptr`（当前指令在 `code_buffer` 中的下标） |
| **D3** | 临时：字节偏移（`data_ptr×4` 或 `code_ptr×4` 用于 `.word` 表索引） |
| **D4** | 临时：扫描下标（括号校验、填表循环） |
| **D5** | **已读入代码字节数**（读循环中递增；`\0` 写在 `code_buffer[D5]`） |
| **D6** | 括号校验时的深度；填表时暂存匹配的 `[` 下标 |
| **D7** | **数据指针** `data_ptr`（0～29，对应 `bf_memory` 中的字下标） |
| **D1** | 填表阶段专用：**括号栈深度** `sp`（与上面“约定”冲突仅在此阶段，填完即不再使用） |

---

## 数据段（第 1～11 行）

| 行号 | 源码 | 说明 |
|------|------|------|
| 1 | `.data` | 以下为已初始化数据段。 |
| 2 | `.org 0x100` | 数据从 `0x100` 开始，避免与 MMIO `0x80`/`0x84` 及低地址重叠（否则 `code_buffer` 会盖住输入端口）。 |
| 4 | `input_addr: .word 0x80` | 存输入流端口的地址常量。 |
| 5 | `output_addr: .word 0x84` | 存输出流端口的地址常量。 |
| 7 | `bf_memory: .word 0,…`（30 个） | Brainfuck 数据带：30 个 32 位字，初值 0。 |
| 8 | `bracket_fwd: .word 0,…`（64 个） | 对每个可能的代码下标 `i`：`[` 且当前格为 0 时，下一指令下标为 `bracket_fwd[i]`（即匹配 `]` 的下一字节）。仅 `[` 位置有意义。 |
| 9 | `bracket_back: .word 0,…`（64 个） | 对每个 `]` 下标 `j`：当前格非 0 时跳到 `bracket_back[j]`（即匹配 `[` 的下一字节）。仅 `]` 位置有意义。 |
| 10 | `bracket_stack: .word 0,…`（64 个） | 填充跳转表时存放未匹配 `[` 的下标栈（最多 63 字节代码，深度足够）。 |
| 11 | `code_buffer: .byte 0,…` | 从 MMIO 读入的一行 Brainfuck 源码（以 `\0` 结尾）；长度为一长串 0 的预留区。 |

---

## 代码段与启动（第 13～25 行）

| 行号 | 源码 | 说明 |
|------|------|------|
| 13 | `.text` | 以下为指令段。 |
| 15 | `_start:` | 程序入口（Wrench 约定）。 |
| 16 | `movea.l input_addr, A0` | `A0` ← 符号 `input_addr` 的地址（指向那个 `.word 0x80`）。 |
| 17 | `movea.l (A0), A0` | `A0` ← 内存 `[input_addr]`，即 **0x80**，得到输入 MMIO 地址。 |
| 18 | `movea.l output_addr, A1` | `A1` ← `output_addr` 的地址。 |
| 19 | `movea.l (A1), A1` | `A1` ← **0x84**，输出 MMIO 地址。 |
| 21 | `move.l 0, D2` | `code_ptr = 0`。 |
| 22 | `move.l 0, D5` | 已读字符计数 = 0。 |
| 23 | `move.l 0, D7` | `data_ptr = 0`。 |
| 24 | `movea.l code_buffer, A4` | `A4` 固定指向代码缓冲区（避免主循环里反复 `movea`）。 |
| 25 | `movea.l bf_memory, A5` | `A5` 固定指向数据带。 |

---

## 读入一行代码（第 27～40 行）

| 行号 | 源码 | 说明 |
|------|------|------|
| 27 | `read_loop:` | 读循环入口。 |
| 28 | `move.l (A0), D0` | 从输入流取下一个 32 位值（一个字节或 EOF 用 0 表示，依 Wrench 约定）。 |
| 29 | `cmp.l 0, D0` | 与 0 比较。 |
| 30 | `beq read_done` | EOF：结束读入。 |
| 31 | `cmp.b 0x0A, D0` | 是否为换行 `\n`。 |
| 32 | `beq read_done` | 换行：代码行结束，不再写入缓冲区。 |
| 33 | `cmp.l 63, D5` | 若已有 63 个字符，不能再写入第 64 个（与 `0x40` 行缓冲一致）。 |
| 34 | `bge line_overflow_error` | 行过长 → 输出 `0xCCCCCCCC` 并停机。 |
| 35 | `move.b D0, 0(A4,D5)` | `code_buffer[D5] = 当前字节`。 |
| 36 | `add.l 1, D5` | 计数 +1。 |
| 37 | `jmp read_loop` | 继续读。 |
| 39 | `read_done:` | 读结束。 |
| 40 | `move.b 0, 0(A4,D5)` | 在末尾写 `\0`，形成 C 风格字符串。 |

---

## 括号深度校验（第 42～66 行）

| 行号 | 源码 | 说明 |
|------|------|------|
| 42 | `validate_brackets:` | 第一遍：只检查 `[` `]` 是否匹配，不填表。 |
| 43 | `move.l 0, D4` | 扫描下标 `i = 0`。 |
| 44 | `move.l 0, D6` | 深度计数 `depth = 0`。 |
| 46 | `val_bracket_loop:` | 逐字节扫描。 |
| 47 | `move.b 0(A4,D4), D0` | `D0 = code[i]`。 |
| 48 | `beq val_brackets_done` | `\0`：扫描结束。 |
| 49 | `cmp.b '[', D0` | 是否为 `[`。 |
| 50 | `bne val_check_close` | 否：去看是不是 `]`。 |
| 51 | `add.l 1, D6` | 是：`depth++`。 |
| 52 | `jmp val_adv_index` | 下一字符。 |
| 54 | `val_check_close:` | 处理 `]`。 |
| 55 | `cmp.b ']', D0` | 是否为 `]`。 |
| 56 | `bne val_adv_index` | 否：普通字符，深度不变。 |
| 57 | `sub.l 1, D6` | 是：`depth--`。 |
| 58 | `blt error_unmatched_close` | 深度 &lt; 0 → 多余的 `]` → 输出 -1。 |
| 60 | `val_adv_index:` | 前进一字符。 |
| 61 | `add.l 1, D4` | `i++`。 |
| 62 | `jmp val_bracket_loop` | 继续循环。 |
| 64 | `val_brackets_done:` | 扫描正常结束。 |
| 65 | `cmp.l 0, D6` | 深度应为 0。 |
| 66 | `bne error_unmatched_open` | 非 0 → 未闭合的 `[` → 输出 -1。 |

---

## 填充括号跳转表（第 68～112 行）

与 Python 语义一致：`bracket_fwd[open] = close+1`（`[` 处当前格为 0 时跳到 `]` 之后）；`bracket_back[close] = open+1`（`]` 处非 0 时跳到 `[` 之后）。用栈记录每个 `[` 的下标。

| 行号 | 源码 | 说明 |
|------|------|------|
| 68 | `fill_bracket_jumps:` | 第二遍扫描，填两张表。 |
| 69 | `movea.l bracket_stack, A3` | 栈数组基址。 |
| 70 | `move.l 0, D4` | 扫描下标归零。 |
| 71 | `move.l 0, D1` | 栈指针 `sp = 0`（下一个空闲槽）。 |
| 73 | `fill_bfj_loop:` | 填表循环。 |
| 74 | `move.b 0(A4,D4), D0` | 当前字符。 |
| 75 | `beq fill_bfj_done` | `\0`：结束。 |
| 76 | `cmp.b '[', D0` | 是否为 `[`。 |
| 77 | `bne fill_bfj_check_close` | 否：处理 `]` 或其它。 |
| 78 | `cmp.l 64, D1` | 栈是否已满（防御）。 |
| 79 | `bge error_unmatched_open` | 满则报错（正常不会触发）。 |
| 80 | `move.l D1, D3` | 计算栈槽地址 `sp*4`。 |
| 81 | `lsl.l 2, D3` | |
| 82 | `move.l D4, 0(A3,D3)` | `stack[sp] = 当前 `[` 下标`。 |
| 83 | `add.l 1, D1` | `sp++`。 |
| 84 | `jmp fill_bfj_adv` | 下一字符。 |
| 86 | `fill_bfj_check_close:` | |
| 87 | `cmp.b ']', D0` | 是否为 `]`。 |
| 88 | `bne fill_bfj_adv` | 普通字符直接前进。 |
| 89 | `sub.l 1, D1` | `sp--`（弹栈准备）。 |
| 90 | `blt error_unmatched_close` | 栈空还见 `]`（校验已通过，理论上不会）。 |
| 91 | `move.l D1, D3` | 取栈顶槽 `sp*4`。 |
| 92 | `lsl.l 2, D3` | |
| 93 | `move.l 0(A3,D3), D6` | `open = stack[sp]`（弹出的 `[` 下标）。 |
| 94 | `move.l D6, D3` | `open * 4` → 写入 `bracket_fwd`。 |
| 95 | `lsl.l 2, D3` | |
| 96 | `movea.l bracket_fwd, A6` | |
| 97 | `move.l D4, D0` | `D4` 为当前 `]` 下标。 |
| 98 | `add.l 1, D0` | `close+1`。 |
| 99 | `move.l D0, 0(A6,D3)` | `bracket_fwd[open] = close+1`。 |
| 100 | `move.l D4, D3` | `close * 4`。 |
| 101 | `lsl.l 2, D3` | |
| 102 | `movea.l bracket_back, A6` | |
| 103 | `move.l D6, D0` | `open+1`。 |
| 104 | `add.l 1, D0` | （此处 `D6` 是 open，故为 `open+1`） |
| 105 | `move.l D0, 0(A6,D3)` | `bracket_back[close] = open+1`。 |
| 107 | `fill_bfj_adv:` | |
| 108 | `add.l 1, D4` | 下一字节下标。 |
| 109 | `jmp fill_bfj_loop` | |
| 111 | `fill_bfj_done:` | 填表完成。 |
| 112 | `jmp main_loop` | 进入解释主循环（此处不经过 `main_next`，因 `D2` 仍为 0）。 |

---

## 主循环与命令分发（第 114～139 行）

| 行号 | 源码 | 说明 |
|------|------|------|
| 114 | `main_loop:` | 取当前指令并执行。 |
| 115 | `move.b 0(A4,D2), D0` | `D0 = code[code_ptr]`。 |
| 116 | `beq program_end` | `\0`：程序正常结束。 |
| 117～132 | 一串 `cmp.b` / `beq` | 按频率把 `+` `-` `.` `,` 放前面，再 `>` `<` `[` `]`，减少比较次数。 |
| 133～137 | 空格 / TAB(9) / CR(13) | 与 Python 一样忽略空白。 |
| 139 | `jmp error_invalid_cmd` | 非法字符 → 输出 -1。 |

---

## 数据指针与 `+` `-`（第 141～164 行）

| 行号 | 源码 | 说明 |
|------|------|------|
| 141 | `cmd_right:` | `>` |
| 142 | `add.l 1, D7` | `data_ptr++`。 |
| 143 | `cmp.l 30, D7` | 是否 ≥30（只允许 0～29）。 |
| 144 | `bge error_ptr_out` | 越界 → -1。 |
| 145 | `jmp main_next` | 下一指令。 |
| 147 | `cmd_left:` | `<` |
| 148 | `sub.l 1, D7` | `data_ptr--`。 |
| 149 | `blt error_ptr_out` | &lt;0 → -1。 |
| 150 | `jmp main_next` | |
| 152 | `cmd_inc:` | `+` |
| 153 | `move.l D7, D3` | `offset = data_ptr * 4`。 |
| 154 | `lsl.l 2, D3` | |
| 155 | `add.l 1, 0(A5,D3)` | 内存字 `+1`（直接改存储器，少指令）。 |
| 156 | `bvs overflow_error` | 有符号溢出 → `0xCCCCCCCC`。 |
| 157 | `jmp main_next` | |
| 159 | `cmd_dec:` | `-` |
| 160～164 | 同上，用 `sub.l` | 下溢同样 `bvs`。 |

---

## 输入输出（第 166～192 行）

| 行号 | 源码 | 说明 |
|------|------|------|
| 166 | `cmd_output:` | `.` |
| 167～169 | `D3 = data_ptr*4`，读字 | 取当前格 32 位值。 |
| 170 | `and.l 0xFF, D0` | 只保留低 8 位。 |
| 171 | `move.l D0, (A1)` | 写到输出流。 |
| 172 | `jmp main_next` | |
| 174 | `cmd_input:` | `,` |
| 175 | `move.l (A0), D0` | 读输入流一字。 |
| 176 | `cmp.l 0, D0` | EOF？ |
| 177 | `beq input_eof` | 是：只清低字节。 |
| 178～183 | 读格、`and` 高 24 位保留、`or` 输入、`存回` | 与 Python「低字节替换、高位保留」一致。 |
| 184 | `jmp main_next` | |
| 186 | `input_eof:` | |
| 187～191 | `and.l 0xFFFFFF00` | 低字节置 0。 |
| 192 | `jmp main_next` | |

---

## `[` `]` 与 O(1) 跳转（第 194～214 行）

表在填充阶段已写好；执行时不再扫描源码，避免嵌套循环时指令数爆炸。

| 行号 | 源码 | 说明 |
|------|------|------|
| 194 | `cmd_loop_start:` | `[` |
| 195～197 | 读当前格 | `D0 = memory[data_ptr]`。 |
| 198 | `bne main_next` | **非 0**：不跳过，走 `main_next` 越过 `[`。 |
| 199～202 | `D2 = bracket_fwd[D2]` | **为 0**：代码指针跳到「匹配 `]` 的下一字节」。 |
| 203 | `jmp main_loop` | **注意**：不执行 `main_next`，因为 `D2` 已是下一条要执行的绝对下标。 |
| 205 | `cmd_loop_end:` | `]` |
| 206～208 | 读当前格 | |
| 209 | `beq main_next` | **为 0**：不跳回，正常 `code_ptr++`。 |
| 210～213 | `D2 = bracket_back[D2]` | **非 0**：跳回「匹配 `[` 的下一字节」。 |
| 214 | `jmp main_loop` | 同样不经过 `main_next`。 |

---

## 步进与停机、错误出口（第 216～245 行）

| 行号 | 源码 | 说明 |
|------|------|------|
| 216 | `main_next:` | 大多数指令执行完后从这里统一前进代码指针。 |
| 217 | `add.l 1, D2` | `code_ptr++`。 |
| 218 | `jmp main_loop` | 取下一条指令。 |
| 220 | `program_end:` | 正常结束。 |
| 221 | `halt` | 停机。 |
| 223 | `error_ptr_out:` | 数据指针越界。 |
| 224 | `move.l -1, (A1)` | 与 Python 的 `[-1]` 一致。 |
| 225 | `halt` | |
| 227～233 | `error_unmatched_*` | 括号错误（校验或填表异常路径）。 |
| 235 | `overflow_error:` | `+`/`-` 32 位溢出。 |
| 236 | `move.l 0xCCCCCCCC, (A1)` | 与 Python `overflow_error_value` 一致。 |
| 239 | `line_overflow_error:` | 读入行超过 63 字节（不含换行）。 |
| 240 | 同上 | 同样输出 `0xCCCCCCCC`。 |
| 243 | `error_invalid_cmd:` | 非法命令字符。 |
| 244 | `move.l -1, (A1)` | |

---

## 小结

1. **数据布局**：`.org 0x100` 避开 MMIO；`A4`/`A5` 缓存缓冲区基址减少热路径上的 `movea`。  
2. **两阶段括号处理**：先深度校验，再栈扫描填 `bracket_fwd`/`bracket_back`，执行期 `[`/`]` 为常数时间跳转。  
3. **错误码**：`-1` 与 `0xCCCCCCCC` 分工与 Python 相同。  
4. **Wrench 语法**：此处 `cmp`/`add`/`sub`/`move` 的立即数写法按本工具要求（多数不用 `#`）。

如需对照仿真，可在本目录用 Docker 运行：`wrench brainfuck_interpreter.s --isa m68k -c <用例>.yaml`。
