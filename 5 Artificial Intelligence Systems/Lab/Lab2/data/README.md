# Titanic 数据

- 任务指定数据集：https://www.kaggle.com/c/titanic
- 文件：`raw/train.csv`，891 行、12 列，含真实 `Survived` 标签。
- 下载使用公开的原始数据镜像：https://raw.githubusercontent.com/wesm/pydata-book/3rd-edition/datasets/titanic/train.csv
- 原始字节 SHA-256：`4a437fde05fe5264e1701a7387ac6fb75393772ba38bb2c9c566405af5af4bd7`。
- 类别数：未生还 549，生还 342。缺失值：Age 177、Cabin 687、Embarked 2。无完整重复行。

这里保留原始数据，不提前填充或缩放。所有预处理由程序在划分后拟合，防止验证/测试信息泄漏。Kaggle 的竞赛 `test.csv` 没有公开真实标签，因此本实验从带标签的 `train.csv` 划分独立测试集，以计算作业要求的四项指标。
