# 实验六：逻辑回归 / Лабораторная №6

已按课程 Notion 的实验六要求实现。俄语报告按 `russian-latex-report` skill 的版式重做，沿用模块二模板中逻辑回归的五个主体部分，并以结论结束。参考资料和代码保存在项目内，不嵌入报告正文。

## 文件

- `report/main.tex`、`report/title.tex`、`report/content.tex`：俄语 LaTeX 报告源文件。
- `report/main.pdf`：编译后的报告。
- `report/figures`、`report/tables`、`report/fonts`：报告所需图片、结果表和字体。
- `model.py`：NumPy/Pandas 手写 sigmoid、log loss、梯度下降、牛顿法、预处理、分层划分及指标。
- `run_experiment.py`：完整实验，21 组配置，自动保存所有结果。
- `test_model.py`：6 项检查，包含有限差分检验梯度/海森矩阵和两种优化器的收敛一致性。
- `make_figures.py`：从真实结果生成 6 张图和 5 张表，Matplotlib 仅用于绘图。
- `predict.py`：读取保存的模型进行预测。
- `data/pima-indians-diabetes.csv`：768 行原始数据，无标题行；程序添加列名。
- `references`：已下载并查看的实验三 PDF、DOCX，实验六 DOCX，课程与模板页面快照和数据说明。
- `results`：统计、完整参数比较、划分索引、测试预测、模型参数与校验记录。

## 运行

需要 Python 3.12 或兼容版本。在本目录执行：

```powershell
python -m pip install -r requirements.txt
python test_model.py
python run_experiment.py
python make_figures.py
python predict.py --row-id 0
```

实验数据已随项目提供，运行无需联网下载。`.deps` 是本机绘图库的临时安装目录，不属于提交包；正常安装 requirements 后不需要它。

预测另一个含列标题的 CSV：

```powershell
python predict.py --input new_samples.csv
```

输入列名必须为：`Pregnancies, Glucose, BloodPressure, SkinThickness, Insulin, BMI, DiabetesPedigreeFunction, Age`。可选 `Outcome` 只用于输出对照，不参与预测。

## 实验设计和结果

- 外层分层划分：614 train / 154 test，seed 42。
- train 内划分为 491 fit / 123 validation，seed 43。
- 预处理参数仅从对应训练部分估计：五列的无效零值转换为空值、训练中位数填充、标准化。
- GD：学习率 0.001/0.01/0.1/1，迭代 100/1000/5000。
- Newton：步长 0.1/0.5/1，迭代 3/10/30。
- 先按 validation log loss 选择配置，再在完整 train 上训练。按任务要求，全部 21 组都报告 test 指标；不根据 test 重新选择参数。
- 选中 GD，学习率 0.1，100 次迭代：Accuracy 0.779221，Precision 0.738095，Recall 0.574074，F1 0.645833。
- 混淆矩阵按真实行/预测列、类别 0/1：`[[89, 11], [23, 31]]`。
- 固定阈值 0.5；未使用 scikit-learn、SciPy 或现成机器学习算法。

结果来自一次固定划分，不能据此宣称该参数组合普遍最优。较多迭代降低 log loss，并不一定提高阈值分类指标。

## 编译报告

```powershell
cd report
xelatex main.tex
xelatex main.tex
```

也可以运行 `tectonic main.tex`。字体已附带。上传到 Overleaf 时，上传整个 `report` 目录，选择 XeLaTeX，并将 `main.tex` 设为主文件。报告封面沿用实验一信息：Чэнь Хаолинь，P3316，407960；教师 Болдырева Елена Александровна。

## 来源与参考资料

- [课程任务](https://sunnysubmarines.notion.site/AI-System-a559a46cddc44363bdf27b77e10b7d85)
- [模块二模板](https://sunnysubmarines.notion.site/2-4c3e6faa54b14630a267dbde97843b6d)
- [实验三理论附件](https://sunnysubmarines.notion.site/1-f2323e041d6a435191b76b0bc088f106)
- [课程指定数据集](https://www.kaggle.com/datasets/uciml/pima-indians-diabetes-database)：本次 API 返回 403。
- [实际使用的同一 Pima 数据集公开镜像](https://github.com/jbrownlee/Datasets/blob/master/pima-indians-diabetes.data.csv)
- [镜像附带原始说明](https://github.com/jbrownlee/Datasets/blob/master/pima-indians-diabetes.names)

实验三两份资料讨论多元线性回归、最小二乘和系数解释；报告第 2.1 节明确说明与逻辑回归的关系，不将线性回归的正态误差假设或正规方程套用到逻辑回归。实验六附件存在混合语言和公式提取不完整的情况，报告采用完整数学公式进行说明。

本项目只包含实验六的执行结果。模板内其他实验的方法比较为定性比较，不声称完成实验三至五。原始数据 SHA-256：`6bfe5d0f379d17a0e0819b996407e3c09bf80febd4287f2ed212190dfff154af`。
