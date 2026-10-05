# 模拟实验一 / УИР 1 — 变体 263

班级名单编号 13 对应变体 263。原始观测取自 `materials/variants.xlsx` 的 `251-300!M2:M301`，共 300 个值，保留原顺序。

任务要求、理论公式与程序实现的逐项中文解释见[实验一中文讲解](实验一中文讲解.md)。

## 目录

```text
lab1/
├─ report/
│  ├─ report.tex                  俄语 LaTeX 源文件
│  ├─ 3316_Чэнь_Хаолинь_ЛР1.pdf 最终提交版 PDF
│  ├─ code/report_demo.py        报告中收录的完整演示程序
│  ├─ figures/                   报告图表（PDF 和 PNG）
│  ├─ tables/                    LaTeX 表格
│  └─ fonts/                     编译所需 CMU 字体
├─ src/
│  ├─ analyze.py                 完整统计分析与图表生成
│  └─ generator.py               可单独运行的随机变量生成器
├─ data/                         原始观测、生成值与计算结果
├─ materials/                    教师提供的题目、理论和变体表
└─ requirements.txt              Python 依赖
```

报告按照 `russian-latex-report` 技能的版式排版。任务书要求说明程序并在答辩时演示，因此报告第 7.1 节收录了可运行的演示代码、计算流程与控制输出；结论仍是报告最后一节。

## 运行与演示

在 `lab1` 目录执行：

```powershell
python -m pip install -r requirements.txt
python .\report\code\report_demo.py
python .\src\generator.py --n 300 --seed 263
python .\src\analyze.py
```

`report_demo.py` 会输出分布参数、前 5 个生成值、两组样本在 300 个观测时的均值、方差、标准差、变异系数和三个置信半区间，以及一阶自相关、交叉相关和两组频数总和。它还计算报告所用的全部六种样本量及 1--10 阶自相关。演示另一次随机实现时，可以修改程序中的 `seed`；报告使用固定初始状态以便复现。

编译报告时进入 `report` 目录，使用 XeLaTeX（运行两次更新目录）或 Tectonic：

```powershell
cd .\report
xelatex report.tex
xelatex report.tex
# 或：tectonic report.tex
```

编译器默认输出 `report.pdf`；最终提交版保存为 `3316_Чэнь_Хаолинь_ЛР1.pdf`。CMU 字体文件来自 [CTAN cm-unicode](https://ctan.org/pkg/cm-unicode)，已包含在 `report/fonts/`，无需系统安装。

## 计算约定

六种样本量均取原序列前 $n$ 项；方差用 $n-1$ 作分母。置信区间按课程材料采用正态近似。形式 1 的相对偏差以原始 300 项结果为基准，形式 2 以相同 $n$ 的原始结果为基准。三阶段低指数模型匹配样本均值与无偏方差，生成值不作事后缩放。
