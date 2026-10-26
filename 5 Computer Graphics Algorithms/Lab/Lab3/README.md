# 实验三 光谱球面与 RGB 对照

程序按模块组织，报告直接维护为 LaTeX，可上传 Overleaf。数值计算使用 NumPy、Pillow，图形界面使用 Tkinter 和 Matplotlib。

```text
Lab3/
├── lab3_color_sphere/
│   ├── __init__.py
│   ├── main.py
│   ├── geometry.py
│   ├── spectral.py
│   ├── color_conversion.py
│   ├── rendering.py
│   ├── gui.py
│   ├── data/
│   │   ├── cie_xyz_1931.csv
│   │   ├── light_spectra.csv
│   │   └── reflectance.csv
│   └── results/
│       ├── white/
│       └── colored/
├── overleaf/
│   ├── main.tex
│   ├── figures/
│   └── results/
├── lab3_overleaf.zip
├── lab3_report.pdf
├── requirements.txt
├── run_lab3.cmd
├── test_lab3.py
├── test_gui.py
├── lab3_study_defense_zh_ru.md
└── validation_results.json
```

原始任务书和老师提供的两份 Excel 数据保留在本目录。`__init__.py` 使程序成为正常 Python 包。中俄对照学习与答辩材料见 `lab3_study_defense_zh_ru.md`。

## 运行

在 Lab3 目录执行：

```text
python -m pip install -r requirements.txt
python -m lab3_color_sphere.main
```

也可运行 `python lab3_color_sphere/main.py`，或双击 `run_lab3.cmd`。Windows 启动器优先使用本项目的 `.venv`，也支持环境变量 `LAB3_PYTHON` 指定解释器。当前机器已在独立 `.venv` 中补齐 Matplotlib，计算模块复用已有的 NumPy、Pillow。普通 Python 环境需要先安装上述依赖。Linux 若未安装 Tkinter，需安装发行版的 `python3-tk` 才能使用界面，命令行计算不需要 Tkinter 或 Matplotlib。

在其他机器建立独立环境可执行：

```text
python -m venv .venv
.venv\Scripts\python -m pip install -r requirements.txt
.venv\Scripts\python -m lab3_color_sphere.main
```

重算报告中的白光和彩光场景：

```text
python -m lab3_color_sphere.main --no-gui --case both
```

结果默认写入包内的 `results/white` 和 `results/colored`。指定场景、独立光谱表和输出目录：

```text
python -m lab3_color_sphere.main --no-gui --config scene.json --output my_results
python -m lab3_color_sphere.main --no-gui --config scene.json --spectra spectra.csv --output my_results
python -m lab3_color_sphere.main --no-gui --case colored --model lambert --output lambert_results
python test_lab3.py
python test_gui.py
```

场景 JSON 可在界面中编辑并保存，也可直接使用已有 `results.json`，其中包含完整输入。`--case both` 计算两个内置场景，不与 `--config` 或 `--spectra` 同用。

## 模块职责

| 模块 | 职责 |
| --- | --- |
| `geometry.py` | Light、Parameters 数据类，实验二相机、透视求交、视锥验证、光照几何 |
| `spectral.py` | 41 波长积分权重、三份 CSV、光谱归一化、场景与编辑表读写 |
| `color_conversion.py` | Spectrum → XYZ → CIE RGB，D65 材质转换，共同曝光与 sRGB 显示 |
| `rendering.py` | 光谱与 RGB 两条路径、控制点、统计和结果保存 |
| `gui.py` | 左侧分组表单，右侧显示当前场景的两路彩图、灰度、光谱曲线和绝对亮度 |
| `main.py` | 图形界面与命令行入口 |

界面左侧按几何、观察者、光源和反射光谱分组。光源可以新增、选择、编辑和删除，可使用内置光谱或自定义表格。完整 JSON 编辑移至高级设置，需要明确应用后同步到普通表单。JSON 加载和保存保留。

光源光谱统一在每盏灯的“Спектр источника”中设置，界面不再提供批量覆盖光谱的“照明条件”预设。白光实验将各灯设为 D65，彩光实验分别设为红、蓝，也可任意混合内置光谱与自定义表格。

右侧并排显示当前场景的 `image_1`、`image_2`。可切换RGB、灰度、光谱曲线以及三采样点绝对亮度。光谱图例标明每盏灯实际使用的光谱。计算图由 Matplotlib 的 `FigureCanvasTkAgg` 嵌入。

修改参数后点击“Рассчитать”才执行计算，直接使用各灯当前的光谱。键盘输入只标记参数发生变化，切换结果视图只绘制缓存。计算在工作线程进行，Tk控件更新在主线程进行。结果导出到所选目录；需要比较白光和彩光时分别设置、计算并保存到不同目录，或使用命令行 `--no-gui --case both`。

## 计算约定

默认 `reference_diagram` 严格保留题图的 `E=I cosσ/r²`、`f=kd cosσ` 与外部 `1/π`，因此接收余弦出现两次。`lambert` 是单余弦对照模式。接收方向用表面指向光源的向量，外法线与其点积截断到非负，发射方向与光源轴单独计算。

每盏光输入的 I0 是可见波段总轴向强度 W/sr，相对谱先按梯形积分归一到1。几何单位为 mm，平方反比衰减使用 m。光谱范围380～780 nm、步长10 nm。光谱辐亮度为 W/(m²·sr·nm)，积分辐亮度为 W/(m²·sr)，光度亮度为 `683Y` cd/m²。

题给 XYZ→CIE RGB 矩阵予以保留，反向矩阵用数值逆，使题目中尺度不一致的两矩阵不会混用。绝对 CIE RGB 允许负值。显示时先转为线性 sRGB，两张图共用同一个最大值与曝光，再裁剪色域并做 sRGB 编码。灰度由实际得到的8位彩图反解线性值、计算Y并重新编码。

`height_px` 自动按物理比例计算，并严格校验方形像素。屏幕100～10000 mm，横纵分辨率200～800。允许负Z光源、球心Z=0、任意多盏光源、斜向和从下方观察。水平观察时设置正的 `screen_distance_mm`，其余情况也可用 `screen_z_mm`。球体必须完整位于视锥中，观察者和光源必须在球外。

## 必要输出

每个场景只保存以下七个文件：

- `image_1.png` 和 `image_2.png`：两条路径的彩图。
- `image_1_gray.png` 和 `image_2_gray.png`：对应灰度图。
- `three_points.csv`：三个精确可见球面点的坐标、绝对辐亮度、光度亮度、XYZ和两路CIE RGB。
- `results.json`：完整场景、输入光谱、单位、可见极值、整球采样极值、共同曝光和两图误差。
- `radiance_data.npz`：完整 float64 光谱立方体、绝对XYZ/RGB、物理亮度、坐标和独立掩码。

背景不计入球面统计。三控制点直接代入公式，不取最近像素。整球181×360角度网格的极值为离散估计。800×800×41的float64谱立方体本身约210 MB，这部分数据按任务要求保留。两条路径的白光PNG完全相同，彩光平均通道差约8.517839。

## Overleaf 报告

在 Overleaf 中选择 **New Project → Upload Project**，上传 `lab3_overleaf.zip`，主文件选 `main.tex`，编译器选 **XeLaTeX**。报告直接用 LaTeX 编写，不需要 Python 生成器。`overleaf` 中的八张必要PNG是独立上传所需的报告资源，完整NPZ不上传Overleaf。

报告已填写确认的姓名 Чжун Ц. Чэнь Х.、组号 P3310 / P3316、教师 Потемин Игорь Станиславович。更改场景后需更新报告中的图和实测数字。

## 表格来源

`cie_xyz_1931.csv` 来自老师的 `CIE_XYZ_1931_10nm.xls` 工作表XYZ的D:G列。原表实际为5 nm，精确选取每10 nm一行，保留原精度。

`light_spectra.csv` 包含 D65、红光、蓝光及老师的6500 K黑体。黑体不是D65。D65来自 [CIE 官方数据](https://cie.co.at/datatable/cie-standard-illuminant-d65)，DOI `10.25039/CIE.DS.hjfjmt59`。原始1 nm文件SHA-256为 `e76f210bffff3d552ef7113025da5f325d5dfec200dd4b878b1a2f3a507032cb`，选取380～780 nm的41行后合并到新表，无插值。CIE及本次D65抽样数据遵循 [CC BY-SA 4.0](https://creativecommons.org/licenses/by-sa/4.0/)。红蓝光为报告所列高斯谱，`reflectance.csv` 为报告采用的绿色材质。

`validation_results.json` 和 `gui_validation.json` 保留先前版本的数值与界面验证记录，其中四图预设模式已从当前 GUI 移除。当前界面使用真实 Tk 事件循环核对自定义光谱、两路结果、视图缓存与结果导出。
