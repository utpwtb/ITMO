# 实验三：模型正则化 / Регуляризация моделей

已完成附件中的 8 项要求，包含实际运行结果及 12 页俄语报告。沿用实验一的 Student Performance 数据和 M1–M4 四组特征，手写无正则化、L1、L2、ElasticNet 线性回归。模型与预处理仅使用 NumPy/Pandas；Matplotlib 只用于绘图。

## 文件

- `model.py`：训练集拟合的预处理、固定划分、近端梯度下降、指标、KKT 最优性残差。
- `experiment.py`：104 组验证实验、16 个最终模型、学习曲线及测试评价。
- `predict.py`：加载模型与预处理参数，对新 CSV 预测。
- `tests/test_core.py`：8 项数值与数据隔离检查。
- `build_report_assets.py`：由结果 CSV 重新生成报告表格。
- `data/Student_Performance.csv`：实验一原始数据的完整副本。
- `references/assignment.docx`、`assignment.md`：本次作业原文件及文本。
- `results/validation_search.csv`：104 组配置的验证误差、权重范数、零系数数量与收敛残差。
- `results/metrics.csv`：16 个最终模型的训练、验证、测试指标和选定参数。
- `results/learning_curves.csv`：16 个模型在 0–15000 次迭代的训练/验证 MSE、R²。
- `results/coefficients.csv`：最终模型的标准化系数、原尺度系数及截距。
- `results/test_predictions.csv`：16 个模型的全部测试预测。
- `results/split.csv`：保留的原始行号与划分；`source_row` 为 CSV 数据区从 0 开始的行索引。
- `results/preprocessing.json`、`models.json`：预处理参数和可加载的模型。
- `results/summary.json`：数据校验值、实验设置与实际环境版本。
- `report/`：完整 LaTeX 源文件、字体、表格、图和最终 `main.pdf`。可独立上传 Overleaf。
- `report-source.zip`：报告源码包，包含所有引用资源。

## 复现

在 `Lab3` 目录打开终端，使用 Python 3.12 或兼容版本：

```powershell
python -m pip install -r requirements.txt
python -B experiment.py
python -B -m unittest discover -s tests -v
python -B build_report_assets.py
```

本次实测环境为 Python 3.12.14、NumPy 2.5.4、Pandas 3.0.1、Matplotlib 3.11.2。数据已包含在项目中，运行实验不需要联网。不同线性代数实现可能产生极小浮点差异。

参数可配置，例如：

```powershell
python -B experiment.py --learning-rate 0.05 --iterations 15000 --lambdas 0.001 0.01 0.1 1 10 --ratios 0.2 0.5 0.8
```

每组实验均使用同一学习率、迭代数及零初始权重。程序检查保守的步长稳定性界限；若自行增大正则化强度，可能需要减小学习率。

新数据需要保留原始五个特征列，目标列可省略：

```powershell
python -B predict.py --input data/Student_Performance.csv --output results/example_predictions.csv --model M3_Baseline
```

此命令演示加载模型的用法，并不产生新的泛化评价。可选择 `M1`–`M4` 与 `Baseline`、`L1`、`L2`、`ElasticNet` 的组合。

## 实验设计

1. 删除 127 条完全重复行后保留 9873 条。去重假设与实验一一致。
2. 完整保留实验一的 1975 条测试记录；其余数据用 seed 43 再分为 5923 条训练、1975 条验证，外层 seed 为 42。
3. 缺失值填充、标准化均只拟合训练集。交互项先构造后标准化，目标不缩放。
4. 目标函数为 `MSE/2 + λ[α ||w||₁ + (1−α)||w||₂²/2]`；截距不受惩罚。L1/ElasticNet 采用近端梯度下降，L2/无惩罚退化为普通全批量梯度下降。
5. λ 取 0.001、0.01、0.1、1、10；ElasticNet 的 α 取 0.2、0.5、0.8。每个特征集 26 组，共 104 组。
6. 仅根据最终验证 MSE 在各正则化家族内选参数，再评价测试集。为保持曲线与最终模型一致，不合并训练和验证集重新拟合。
7. 4 张学习曲线组合图，每张含 4 个坐标面板，每个面板含 4 条曲线，共 16 个任务要求的图。图上 MSE 不含惩罚项。横轴采用 symlog 保留第 0 步并展示早期收敛，MSE 纵轴为对数。
8. 保存所有系数及范数，精确零判断为 `w == 0`；“接近零”定义为标准化系数 `|w| < 0.01`。

## 结论

验证集选出的主模型为 **M3 无正则化**：测试 MSE **4.262393**、R² **0.988621**。M3 的 L2 测试 MSE 为 4.261478，差异很小，不能据此改变验证集选择或宣称稳定提升。

最优参数下没有零系数或接近零的系数。较强的 L1 确实产生稀疏解：M3 在 λ=1 时有 3 个零系数，λ=10 时有 4 个，但验证误差明显上升。M4 的交互项未改善泛化，且相关特征之间会重新分配权重，因此正则化不保证每个系数都单独缩小。

8 项检查已通过：四种惩罚的已知解析解、截距不惩罚、λ=0 等价性、曲线与直接计算指标一致、训练集预处理隔离、分割不交叠且测试集与实验一一致、参数选择与保存预测一致，以及无效参数/过大步长拒绝。

## 编译报告

在 `report` 目录使用 XeLaTeX：

```powershell
xelatex -interaction=nonstopmode main.tex
xelatex -interaction=nonstopmode main.tex
```

也可执行 `tectonic main.tex`。本次使用 Tectonic 0.17.0 的 XeTeX 引擎实际编译，最终 12 页 PDF 已逐页查看；无溢出框或缺字警告。CMU Serif 字体及其许可证随源码提供。Overleaf 编译器选 XeLaTeX，主文件选 `main.tex`。

报告采用 A4、11 pt、左右上边距 2 cm、下边距 3 cm，俄语正文，以“Заключение”结束，没有附录或参考文献。封面沿用既有实验报告的信息。本任务未指定变体号。

重新运行实验会更新结果和图片；运行 `build_report_assets.py` 更新表格。若修改实验设置或得到不同数值，还需同步修改 `report/content.tex` 中的叙述并重新编译。
