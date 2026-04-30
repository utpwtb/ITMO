# Lab4 实验详细指南

## 你的变体分析

你的变体是：**`alg | cisc | harv | hw | tick | binary | trap | port | cstr | prob1 | cache`**

这个变体意味着你需要实现：

| 特性 | 值 | 含义 |
|------|-----|------|
| **编程语言语法** | `alg` | Algol风格（类似Java/JavaScript/Lua），支持数学表达式 |
| **架构** | `cisc` | 复杂指令集，支持变长指令、特殊寄存器 |
| **内存架构** | `harv` | 哈佛架构（指令存储器与数据存储器分离） |
| **控制单元** | `hw` | 硬连线控制单元 |
| **模型精度** | `tick` | 精确到时钟周期的模拟 |
| **机器码表示** | `binary` | 二进制格式（非JSON文本） |
| **输入输出** | `trap` | 中断/陷阱方式的I/O |
| **I/O ISA** | `port` | 端口映射I/O（专用I/O指令） |
| **字符串类型** | `cstr` | C风格空终止字符串 |
| **算法** | `prob1` | 欧拉问题4：寻找两个三位数乘积的最大回文数 |
| **复杂化** | `cache` | 缓存memory组织 |

---

## 实验目标概述

本实验的核心任务是构建一个完整的**编译器和处理器模拟器系统**：

```
源代码(你的语言) 
      ↓ 翻译器(编译器)
机器码
      ↓ 加载到处理器
处理器模型 ← 输入数据
      ↓
输出结果 + 运行日志
```

你需要交付：
1. **编程语言**及其语法描述
2. **指令系统(ISA)**设计
3. **处理器模型**（DataPath + ControlUnit）
4. **翻译器**（源代码 → 机器码）
5. **Golden测试**

---

## 你的变体详解

### 1. 编程语言：`alg` (Algol风格)

**要求**：
- 语法类似Java/JavaScript/Lua
- 必须支持**数学表达式**（如 `a + b * c`, `(a + b) * d`）
- 表达式应映射到寄存器/内存
- 在测试中验证**AST（抽象语法树）**，且必须**人类可读**

**你需要实现**：
- 词法分析器（Tokenization）
- 语法分析器（生成AST）
- 语义分析
- 代码生成

**示例语法**（参考Java/JS风格）：
```c
// 变量声明
int a = 5;
int b = 10;
int c = a + b * 2;

// 条件语句
if (a > b) {
    output(1, a);
} else {
    output(1, b);
}

// 循环
while (a < 100) {
    a = a + 1;
}

// 函数
int add(int x, int y) {
    return x + y;
}
```

### 2. 架构：`cisc` (复杂指令集)

**要求**：
- 支持**变长指令**（一条指令可能占用多个机器字）
- 算术指令可以在**一个操作中**同时操作寄存器和内存
- 使用**特殊寄存器**
- 示例：多项式计算 `c₀ + c₁x₁ + c₂x₂ + ...` 需要可变操作数

**关键点**：
- 指令长度不固定
- 需要处理指令提取时的字切换
- 需要更多寄存器（如索引寄存器、基址寄存器）

### 3. 内存架构：`harv` (哈佛架构)

**要求**：
- **指令存储器**和**数据存储器分离**
- 测试中必须展示/验证两者是独立的

**内存模型**：
```
    指令存储器 (Program Memory)
+------------------------------+
| 00 : jmp n                   |
|   ...                        |
|  n : _start: instruction1    |
|   ...                        |
+------------------------------+

    数据存储器 (Data Memory)
+------------------------------+
| 00  : 常量 1                 |
| 01  : 变量 1                 |
| n   : 数组                   |
+------------------------------+
```

### 4. 控制单元：`hw` (硬连线)

**要求**：
- 使用硬件逻辑实现控制
- 不使用微程序存储
- 适合CISC架构

### 5. 模型精度：`tick` (时钟周期精度)

**要求**：
- 精确到**每个时钟周期**的模拟
- 模拟过程可以在**任何时钟周期暂停**
- 日志必须包含每条指令的tick数

**日志格式示例**：
```
TICK:  70,  PC:   8,  AR:   7,  MEM_OUT:  32,  TOS: [32, 7, 7]  |  pop
TICK:  71,  PC:   9,  AR:   7,  MEM_OUT:  32,  TOS: [7, 7]      |  swap
```

### 6. 机器码表示：`binary`

**要求**：
- 生成**真正的二进制文件**（不是文本0/1或JSON）
- 调试输出到**文本文件**，格式如下：
```
<地址> - <HEXCODE> - <助记符>
20 - 03340301 - add #01 <- 34 + #03
```

### 7. 输入输出：`trap` (陷阱/中断方式)

**要求**：
- I/O通过**中断系统**进行
- 处理器具有**中断机制**
- 中断处理程序用你的语言实现
- 日志中必须清楚显示是否在中断中工作

**中断工作原理**：
- 模型启动时有输入时间表：`[(1, 'h'), (10, 'e'), ...]`
- 数字表示调用中断的时钟周期
- 字符表示该周期开始可用的数据
- 必须实现中断处理程序

### 8. I/O ISA：`port` (端口映射)

**要求**：
- I/O端口有**专门的寻址**
- 使用**专用I/O指令**

### 9. 字符串：`cstr` (C风格空终止)

**要求**：
- 字符串以`\0`结尾
- 静态字符串存储在数据段
- 字符串操作作为过程/函数实现

**示例**：
```
"Hello!" 存储为: [72, 101, 108, 108, 111, 33, 0]
```

### 10. 算法：`prob1` (欧拉问题4)

**问题描述**：
> 一个与3位数相关的回文数：找出两个两位数乘积的最大回文数。
> 等等，这是问题4的标准描述。让我确认：欧拉问题4是找**两个三位数乘积的最大回文数**。

**回文数**：从左到右和从右到左读是相同的数字。

**示例**：
```
三位数: 999 * 999 = 998001 (不是回文)
三位数: 995 * 583 = 580295 (不是回文)
...
```

**你需要**：
1. 遍历所有可能的两个三位数组合
2. 计算它们的乘积
3. 检查乘积是否是回文数
4. 找出最大的回文数

### 11. 复杂化：`cache` (缓存memory)

**要求**：
- 缓存访问：**1个时钟周期**
- 内存访问：**10个时钟周期**
- 实现算法展示缓存工作原理
- 日志中能看到缓存命中/未命中

---

## 你需要实现什么

### 1. 编程语言 → 翻译器

```
source_code.txt → [Lexer] → Tokens → [Parser] → AST → [Code Generator] → binary_code.bin
```

**关键文件结构**：
```
src/
├── lexer.py        # 词法分析
├── parser.py       # 语法分析 → AST
├── ast.py          # AST节点定义
├── codegen.py      # 代码生成
└── translator.py  # 主程序
```

### 2. 处理器模型

```
src/
├── isa/
│   ├── opcode.py      # 指令定义
│   ├── instruction.py # 指令类
│   └── memory.py      # 哈佛架构：单独的程序/数据存储器
├── machine/
│   ├── data_path.py   # 数据通路（ALU、寄存器、缓存）
│   ├── control_unit.py # 控制单元（硬连线）
│   ├── cache.py       # 缓存实现（这是你的新要求）
│   └── main.py        # 主程序
└── components/
    ├── alu.py         # 算术逻辑单元
    ├── registers.py   # 寄存器文件
    └── io.py          # I/O控制器
```

### 3. 必须实现的算法

| 算法 | 输入 | 输出 |
|------|------|------|
| **Hello World** | 无 | "Hello, world!" |
| **Cat** | 任意长度字符串 | 原样输出 |
| **Hello User** | 用户名 | "Hello, [用户名]!" |
| **Sort** | 数字列表 | 排序后的列表 |
| **双精度算术** | 两个大数 | 和/积等 |
| **Prob1** | 无（内置100-999） | 最大回文数 |

---

## Python知识要求

### 必须掌握

#### 1. **类定义与OOP**
```python
from dataclasses import dataclass
from enum import Enum, auto

class Opcode(Enum):
    ADD = auto()
    SUB = auto()
    # ...

@dataclass
class Instruction:
    opcode: Opcode
    operand: int | None = None
```

#### 2. **文件I/O**
```python
# 读取文本
with open("source.txt", "r", encoding="utf-8") as f:
    content = f.read()

# 写入二进制
with open("output.bin", "wb") as f:
    f.write(bytes([0x01, 0x02, 0x03]))

# 读取二进制
with open("input.bin", "rb") as f:
    data = f.read()
```

#### 3. **位运算**
```python
# 打包32位指令
opcode_bin = (opcode << 28) | (operand & 0x0FFFFFFF)

# 解包
opcode = (word >> 28) & 0xF
operand = word & 0x0FFFFFFF
```

#### 4. **字典/Dict操作**
```python
labels = {"start": 0, "loop": 10}
address = labels.get("loop", 0)
```

#### 5. **Logging**
```python
import logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)
logger.debug("TICK: %d, PC: %d", tick, pc)
```

### 推荐掌握

#### 1. **typing模块**
```python
from typing import NamedTuple, Optional

class Instruction(NamedTuple):
    opcode: Opcode
    operand: Optional[int]
```

#### 2. **迭代器/生成器**
```python
def tokenize(code: str):
    for i, char in enumerate(code):
        yield Token(char, i)
```

#### 3. **结构体字节打包**
```python
import struct
binary = struct.pack(">I", value)  # 大端32位
```

---

## 项目结构建议

```
lab4/
├── pyproject.toml          # 项目配置
├── src/
│   ├── __init__.py
│   ├── lexer.py            # 词法分析
│   ├── parser.py          # 语法分析
│   ├── ast.py             # AST定义
│   ├── translator.py      # 代码生成/翻译器
│   ├── isa/
│   │   ├── __init__.py
│   │   ├── opcode.py
│   │   ├── instruction.py
│   │   └── memory.py
│   ├── machine/
│   │   ├── __init__.py
│   │   ├── data_path.py
│   │   ├── control_unit.py
│   │   ├── cache.py
│   │   └── simulation.py
│   └── components/
│       ├── __init__.py
│       ├── alu.py
│       ├── registers.py
│       └── io.py
├── examples/
│   ├── hello_world.alg
│   ├── cat.alg
│   └── prob1.alg
└── tests/
    ├── golden/
    │   ├── hello_world.yml
    │   ├── cat.yml
    │   └── prob1.yml
    └── test_translator.py
```

---

## 开始工作的步骤

### 第一步：设计你的指令集

对于你的`cisc`变体，需要设计：
- 指令格式（变长）
- 寄存器组
- 寻址模式
- 特殊指令（如字符串处理）

**示例（32位固定格式，但CISC风格）**：
```
[opcode(8bit) | reg(4bit) | addr_mode(4bit) | operand...]
```

### 第二步：实现翻译器

1. 编写`alg`语言的词法分析器
2. 实现AST生成
3. 编写代码生成器
4. 生成二进制机器码

### 第三步：实现处理器模型

1. 实现**哈佛架构**（程序/数据分离存储器）
2. 实现**缓存系统**（1周期命中，10周期未命中）
3. 实现**硬连线控制单元**
4. 实现**中断/trap系统**
5. 实现**端口I/O**

### 第四步：实现Golden测试

每个测试包含：
```yaml
- source_file: examples/hello.alg
  instructions_binary: output/hello.bin
  data_binary: output/hello_data.bin
  input: ""
  output: "Hello, world!"
  log: |
    TICK: 1, PC: 0, ...
    TICK: 2, PC: 1, ...
```

### 第五步：配置CI

```yaml
# .github/workflows/python.yml
name: Python CI
on: [push, pull_request]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: '3.12'
      - run: pip install poetry
      - run: poetry install
      - run: poetry run ruff check src/
      - run: poetry run mypy src/
      - run: poetry run pytest
```

---

## 评分要点

根据你的变体特点，特别注意以下扣分项：

1. **CISC但没有变长指令** → 0分
2. **中断系统但没有中断处理程序** → 0分
3. **有缓存但日志看不出缓存工作** → 0分
4. **数据是代码的一部分**（如字符串用指令序列存储）→ 0分
5. **示意图不可读** → 0分

**高分要求**：
- 出色完成所有基础功能
- 正确实现缓存并展示性能影响
- golden测试覆盖完整
- 报告结构清晰，示意图专业

---

## 参考资料

### Brainfuck示例（基础理解）
`Lab/Lab4/demo/brainfuck-master/python/` - 简单的累加器架构

### 堆栈机示例（完整参考）
`Lab/Lab4/demo/csa3-stack-machine-master/` - 完整实现，包含：
- 哈佛架构
- 端口I/O
- 字符串处理
- 缓存（需添加）

### 关键API参考

**翻译器**：
```bash
poetry run translator <source.alg> <instructions.bin> <data.bin>
```

**处理器模拟**：
```bash
poetry run machine <instructions.bin> <data.bin> <input.txt> --log_level DEBUG
```

---

## 下一步行动

1. **首先**精读`csa3-stack-machine-master`的代码结构
2. **然后**修改为适配你的`alg|cisc|harv|...|cache`变体
3. **重点**实现：
   - alg语言的词法/语法分析
   - 变长指令的CISC设计
   - 哈佛架构
   - 缓存系统
   - trap中断I/O
4. **最后**实现prob1算法和完整测试

有问题请查阅示例代码！