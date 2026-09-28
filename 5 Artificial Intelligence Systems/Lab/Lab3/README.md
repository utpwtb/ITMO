# 实验三：线性回归 / Линейная регрессия

已按 [Notion 实验三要求](https://sunnysubmarines.notion.site/AI-System-a559a46cddc44363bdf27b77e10b7d85) 完成，使用用户确认的奇数序号数据集 Student Performance。报告内容按 [模块二模板](https://sunnysubmarines.notion.site/2-4c3e6faa54b14630a267dbde97843b6d) 组织。

## 交付文件

- `report/main.pdf`：俄语报告。
- `report/main.tex`、`content.tex`、`title.tex`：LaTeX 源文件；表格、图片和字体全部包含在 `report` 内，可单独上传 Overleaf。
- `实验三任务与实现讲解.md`：对照课程任务和理论附件的中文讲解，说明公式、代码实现和运行结果。
- `experiment.py`：完整可复现实验，手写高斯消元求解正规方程；没有调用 sklearn、SciPy 或 `numpy.linalg`。
- `data/Student_Performance.csv`：原始数据，未经修改。
- `results/`：实际运行产生的指标、系数、完整测试预测、划分索引、统计数据和四幅图。
- `sources/linear_regression.pdf`、`sources/linear_regression.docx`：从 Notion 实验三理论页面下载并读取的两个原始附件。来源与要求见 `sources/README.md`。
- `build_report_assets.py`：从实际结果生成 LaTeX 表格并同步图片，避免手填数据不一致。

## 运行实验

需要 Python 3.12 或更新的兼容版本。在 `Lab3` 目录执行：

```powershell
python -m pip install -r requirements.txt
python experiment.py
python build_report_assets.py
```

脚本启动时会运行已知线性解、主元交换、奇异矩阵、R²、训练集独立预处理及课程附件例题检查；每个模型还检查正规方程残差。Matplotlib 仅用于绘图，模型计算仅用 NumPy/Pandas。

首次下载的数据已包含在项目内，之后运行实验不需要网络。若当前机器有 `Lab3/.deps`，脚本会优先读取其中的本地依赖；交付 ZIP 不包含该缓存，安装 `requirements.txt` 即可。

## 实际结果

原始数据 10,000 行；无缺失值；删除 127 条完全重复行，剩余 9,873 行。使用 `default_rng(42)`，训练 7,898 行，测试 1,975 行。三种基本特征方案及一项加分实验使用相同划分。

| 模型 | 特征 | 测试 R² | 测试 RMSE |
|---|---|---:|---:|
| M1 | 学习时长 | 0.143777 | 17.9088 |
| M2 | 学习时长、历史成绩 | 0.985810 | 2.3055 |
| M3 | 全部五个原始特征 | 0.988620 | 2.0647 |
| M4（加分） | M3 + 学习时长 × 历史成绩 | 0.988619 | 2.0648 |

M3 在本次测试中最好，合成特征没有改善结果。数据作者明确说明这是合成教学数据，不应将模型系数解释为真实教育因果关系。

预处理顺序：去重 → 划分 → Yes/No 编码 → 用训练集的中位数/众数补缺失 → 构造合成特征 → 用训练集均值与标准差进行标准化。原数据无缺失，补缺失分支通过人为缺失的小样本检查。目标值不缩放，也不截断预测。

删除完全重复行是一项明确的实验假设；数据没有学生 ID，不能证明这些重复记录一定代表同一个人。报告说明了这一限制。所有训练/测试索引均保存，不会悄悄更改划分。

## 编译报告

```powershell
cd report
xelatex main.tex
xelatex main.tex
```

也可 `tectonic main.tex`。将整个 `report` 文件夹上传 Overleaf，编译器选 **XeLaTeX**，主文件选 `main.tex`。字体已随报告附带，无需系统安装。

封面沿用实验一已填写的信息：Чэнь Хаолинь，P3316，407960；教师 Болдырева Елена Александровна。需要调整时编辑 `report/title.tex`。

可选排版检查脚本 `qa_report.py` 需要 PyMuPDF 和 Pillow，不属于实验算法依赖。输出保存在 `tmp/qa/`。
