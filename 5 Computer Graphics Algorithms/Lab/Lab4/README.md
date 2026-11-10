# Lab4：从 RGB 重建光谱

仅实现任务 A/B/C。GUI 沿用 lab3 的左侧参数分组、右侧结果标签页，报告沿用 lab3 的俄文 LaTeX 结构。

## 启动

在 PyCharm 中直接打开 `C:\develop\NOTE_UTP\StudyNote\5 Computer Graphics Algorithms\Lab\Lab4\lab4_spectrum`，选择已安装依赖的 Python 解释器，然后右键运行 `__main__.py` 即可打开 GUI。无需配置模块启动，也不依赖工作目录。

唯一程序入口为 `lab4_spectrum/__main__.py`，也可以双击上一级目录的 `run_lab4.cmd` 启动 GUI。计算、查看结果和导出均通过界面完成，不再提供命令行计算模式。命令行启动 GUI 的示例：

```powershell
Set-Location "C:\develop\NOTE_UTP\StudyNote\5 Computer Graphics Algorithms\Lab\Lab4"
.\.venv\Scripts\python.exe .\lab4_spectrum\__main__.py
```

依赖清单位于上一级目录的 `requirements.txt`。换电脑时新建 Python 3.12+ 环境，再在 Lab4 目录执行 `python -m pip install -r requirements.txt`。Tkinter 由 Windows 官方 Python 安装器提供。

## 实验边界

- 输入是绝对 **CIE RGB 1931**，不是 PNG 的 sRGB 0～255。光源 RGB 为单位积分光谱的颜色，I₀ 单独表示可见波段总强度 W/sr。
- 光源按讲义三基谱法恢复。取 F₁=x̄、F₂=ȳ、F₃=z̄，建立 Cᵢₖ=∑wⱼc̄ᵢ(λⱼ)Fₖ(λⱼ)，解 C a=M RGB，再计算 S=F a。恢复函数只接收 RGB，不读取原 D65。若选定基谱给出负光谱则报错，不裁剪、不换算法。
- 讲义只约束 XYZ/RGB，不约束能量积分。**重建谱不再归一化**。输入 I₀ 是原场景的积分强度，在重建计算中作为原有幅值尺度，实际重建积分强度为 I₀×∑wS，已记录在 results.json。
- lab4 要求白色漫反射球，因此固定 `kd(λ)=1`，RGB 反射系数 `(1,1,1)`。未添加彩色材质、彩光模式、额外反射模型、JSON 编辑器。
- **lab3 白光结果实际使用绿色球。** `results/image_1.png`、`image_2.png` 是将 lab3 的光谱与 RGB 两条计算序列按相同白球、教材照明模型、统一显示方式重算的受控基准。`reference_lab3` 保存真正的原 lab3 图片和参数，另作直接对照，不把重算图冒充原图。
- 按教材公式 (3.4.5.1) 计算 L=kd·E/π，接收余弦只出现一次。旧版余弦平方模式已删除。
- 380～780 nm，步长 10 nm，41 通道，梯形积分。毫米输入在平方反比公式中转换为米。绝对光谱和 RGB 始终用浮点数，只有显示输出归一到 0～255。
- 三图共享最大通道归一化，按讲义 5 使用 γ=2.2 的显示近似。背景用独立 mask 排除统计。整球极值是 181×360 网格的离散估计，不声称是连续极值。

## 教材与实现对应

先读取并核对以下本地材料，再实现算法。报告引用了相同的书名、章节、页码和公式。

| 内容 | 教材位置 | 实现 |
|---|---|---|
| 三基谱、C a=M RGB、负光谱限制 | `../Lecture/mis_lect04_11.pdf` PDF 第 35～42 页 | `reconstruction.py` |
| D65 由标准观察者曲线重建、同色异谱 | `../Lecture/3281.pdf` 印刷第 64～66 页，图 4.6 | 选定 XYZ 观察者三基谱 |
| L=kd·E/π | `3281.pdf` 印刷第 47 页，式 (3.4.5.1) | `core/geometry.py` |
| CIE RGB→XYZ 数值矩阵 | `3281.pdf` 印刷第 70 页 | `core/color_conversion.py`，逆矩阵由同一矩阵求逆 |
| XYZ→线性 sRGB 矩阵 | `3281.pdf` 印刷第 77 页 | `core/color_conversion.py` |
| 线性空间计算，显示 γ=2.2 | `mis_lect05_11.pdf` PDF 第 43～46 页 | `monitor_encode` |

`3281.pdf` 的 PDF 页码比印刷页码大 1。基谱具体选型与梯形积分是依据任务采样网格落实的选择，不声称教材指定了唯一基谱。讲义 4 第 41 页的矩阵图有重复的波长下标，代码按前一页的积分定义形成矩阵。显示采用讲义 5 明示的 γ=2.2，不使用教材第 77 页排版有误的分段传递公式。

## 输出和报告

`results` 中包含：

- `image_A.png`：恢复光谱后计算的结果。
- `image_1.png`、`image_2.png`：同一白球的 lab3 光谱与 RGB 路径。
- `spectra_comparison.csv` 和 `.png`：41 波长原始和恢复谱、差值，以及材料曲线。
- `three_points.csv`：三点坐标、绝对辐亮度、光度亮度、XYZ/RGB。
- `results.json`：场景、RGB 输入、误差、可见/整球采样极值、单位和显示约定。
- `absolute_data.npz`：float64 `spectral_A[H,W,41]`、绝对 XYZ/RGB、mask、辐亮度、光度亮度、恢复谱和输入 RGB。

`overleaf/main.tex` 是手写维护的主报告。`lab4_overleaf.zip` 可上传 Overleaf，选择 **XeLaTeX** 编译。姓名、组号、教师沿用 lab3。更改场景后应同步更新报告的静态表格、图片和数字。

原始要求写 Word 或 PowerPoint，本次按用户要求交付 LaTeX。当前机器未找到 LaTeX 编译器，未声称 PDF 编译通过。

## 验证与实测

原有交付结果使用 600×600 场景。核对算法时，应检查 RGB 保持、线性缩放、非负光谱限制、重建能量不强制归一化、单入射余弦和辐射量/光度量的单位关系；界面应能完成计算、查看结果、光源增删和导出。

默认光谱 RMSE 约 0.0014188447 /nm，RGB 最大重建误差约 1.11e-16，重建谱积分约 0.62955566。三张受控 PNG 像素一致。这是同色异谱，不表示恢复了真实 D65。

## 代码来源

代码按职责放入 `lab4_spectrum` 包，没有新增管理类或继承层：

```text
lab4_spectrum/
  __main__.py               唯一启动入口，直接运行打开 GUI
  reconstruction.py         RGB → 光谱重建
  experiment.py             场景与实验计算、对照
  output.py                 图表、摘要与文件导出
  gui.py                    App 界面类
  core/                     相机、几何、渲染、颜色转换及 CSV 数据
    data/
results/                    实验数据
overleaf/                   LaTeX 报告
reference_lab3/              原 lab3 白光结果快照
```

`lab4_spectrum/core` 复用 lab3 的相机、求交和校验，照明、光谱尺度及颜色转换已按教材修正。旧版求解器、双余弦模式、彩色材质预设、JSON/光谱编辑加载器和重复导出代码已删除。只保留这一个包版本，外层 `lab4.py` 已删除，直接运行包内的 `__main__.py` 启动 GUI。lab1～lab3 未修改，运行不依赖原 lab3 源码目录。

CIE XYZ 表由 lab3 从教师 XLS 抽样得到，D65 表来自 [CIE 数据](https://cie.co.at/datatable/cie-standard-illuminant-d65)，DOI `10.25039/CIE.DS.hjfjmt59`，继承 [CC BY-SA 4.0](https://creativecommons.org/licenses/by-sa/4.0/)。保留来源并按相同许可共享数据。
