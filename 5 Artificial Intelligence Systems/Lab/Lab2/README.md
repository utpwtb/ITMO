# 实验二：Titanic 逻辑回归 / Лабораторная 2

使用 Titanic 的 891 条带标签乘客数据，完成缺失值处理、类别编码、描述统计、可视化、手写逻辑回归和 21 组超参数实验。程序仅依赖 **NumPy、Pandas 和 Python 标准库**；不使用 scikit-learn、SciPy 或 Matplotlib。SVG 绘图由标准库直接输出。

## 目录

```text
Lab2/
├── data/
│   ├── README.md                 # 数据来源和校验值
│   └── raw/train.csv             # 原始 891 条带标签数据
├── src/titanic/
│   ├── data.py                   # 训练集拟合的预处理、分层划分
│   ├── model.py                  # sigmoid、log loss、GD、Newton
│   ├── metrics.py                # 四项指标和混淆矩阵
│   ├── experiment.py             # 完整实验入口
│   ├── visualization.py          # 可复现的统计图和实验图
│   └── predict.py                # 加载模型进行预测
├── tests/test_core.py            # 数值正确性和数据隔离检查
├── results/
│   ├── statistics/               # 数值统计、类别频次、缺失值
│   ├── metrics/                  # 全部配置的验证/测试指标、损失历史
│   ├── predictions/              # 每组配置和选定模型的测试预测
│   ├── model/                    # 保存的预处理参数、模型、系数
│   ├── figures/                  # 5 张 SVG 实验图
│   ├── split.csv                 # 每条记录所属的划分
│   └── summary.json              # 实验摘要和运行环境
├── references/
│   ├── assignment.md             # 本次作业要求
│   └── logistic_regression.docx  # 用户提供的理论材料
├── report/
│   ├── main.pdf                  # 最终俄语报告
│   ├── main.tex                  # LaTeX 入口
│   ├── title.tex                 # 封面
│   ├── content.tex               # 正文和代码附录
│   ├── fonts/                    # 字体及许可证
│   ├── figures/                  # 报告实际引用的矢量图
│   └── tables/                   # 报告引用的结果表
├── requirements.txt
└── pyproject.toml                # 代码格式规范
```

原始数据、程序、计算结果、报告素材均属于交付内容。目录内不包含报告生成脚本、检查用预览图、编译日志、缓存或旧 Pima 实验。

## 运行

在 `Lab2` 下打开 PowerShell。建议使用 Python 3.12；此次实际版本为 Python 3.12.14、NumPy 2.3.5、Pandas 3.0.1。可在项目外的虚拟环境安装依赖。

```powershell
python -m pip install -r requirements.txt
$env:PYTHONPATH = Join-Path (Get-Location) 'src'
python -B -m titanic.experiment
python -B -m unittest discover -s tests -v
```

实验入口重新计算结果并更新 `results/` 中的 CSV、JSON 和 SVG。`-B` 防止生成字节码缓存。固定种子控制分层划分；极小浮点差异可能随 NumPy/底层线性代数库而变化。

如已安装 Ruff，可检查格式；Ruff 是开发工具，不是程序运行依赖：

```powershell
ruff format --check --no-cache src tests
ruff check --no-cache src tests
```

预测入口支持具有相同字段的新 CSV。若另行下载了 Kaggle 无标签测试文件并保存为 `data/raw/test.csv`，可运行：

```powershell
python -B -m titanic.predict --input data/raw/test.csv --output results/predictions/kaggle_test.csv
```

这个可选文件未包含在交付中。输出包含 PassengerId、probability 和 Survived；不是自动提交到 Kaggle 的操作。

## 设计与结果

- 输入：Age、SibSp、Parch、Fare，以及 Sex、Pclass、Embarked 的参照组编码；共 9 个特征，加截距共 10 个参数。
- 训练/测试：713/178，分层、种子 42；训练内再分成拟合 570 条和验证 143 条，种子 43。
- 年龄以训练部分中位数填充，登船港口以众数填充；只有数值特征标准化。验证和测试数据不参与估计填充值或缩放参数。
- GD：学习率 0.001、0.01、0.1、1；迭代 100、1000、5000，共 12 组。
- Newton：学习率/阻尼系数 0.1、0.5、1；迭代 3、10、30，共 9 组。
- 先按验证 log loss 选参，再在全部训练数据上重训；按任务要求对每一组计算测试指标。测试集不用于重新选参。
- 选定 Newton，学习率 1、10 次迭代。测试 accuracy **0.7921**、precision **0.7541**、recall **0.6765**、F1 **0.7132**；TN=95、FP=15、FN=22、TP=46。
- 验证结果中多个充分收敛配置实际上等价；数值级差异不能证明优越性。测试最高 F1 为 0.7424（Newton，0.5，3），它仅用于描述比较，不替代验证选参结果。

8 项检查覆盖极端 sigmoid/log loss、有限差分梯度和 Hessian、已知解析解、四项指标、分层划分、训练统计隔离、类别编码/模型反序列化，以及保存模型与测试预测一致性。

## 报告

采用用户最新指定的结构：Введение → Описание метода → Псевдокод метода → Результаты выполнения → Примеры использования метода → Сравнение методов（含两个指定小节）→ Заключение → Приложения（代码）。

报告附录直接引用 `../src/titanic/model.py`、`data.py` 和 `metrics.py`，因此应保留整个 `Lab2` 结构。源码、图、表、字体均已提供；需要 XeLaTeX/LuaLaTeX 和通常的 TeX 宏包。`report/fonts/OFL.txt` 是字体许可证。

编译时在 `report` 目录执行以下命令，将中间文件放在系统临时目录，不污染实验目录：

```powershell
$taskTexBuild = Join-Path $env:TEMP 'titanic-report-build'
New-Item -ItemType Directory -Force -Path $taskTexBuild | Out-Null
xelatex -interaction=nonstopmode "-output-directory=$taskTexBuild" main.tex
xelatex -interaction=nonstopmode "-output-directory=$taskTexBuild" main.tex
Copy-Item -LiteralPath (Join-Path $taskTexBuild 'main.pdf') -Destination main.pdf
```

报告表格和 PDF 图对应本次已验证的计算结果。重新运行实验会更新 CSV/JSON/SVG；如果修改实验设置，还应同步更新报告表格、插图和结论。按要求未保留报告生成辅助脚本。
