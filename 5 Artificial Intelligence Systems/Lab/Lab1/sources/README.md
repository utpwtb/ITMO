# 课程来源核对（2026-09-22）

课程：[AI System](https://sunnysubmarines.notion.site/AI-System-a559a46cddc44363bdf27b77e10b7d85)

实验三标题：**Лабораторная 3. Линейная регрессия**。

要求：

1. 按班级名单序号奇偶选择数据集。用户确认奇数，对应 Student Performance。
2. 计算并图示 count、mean、std、min、max、分位数。
3. 缺失值处理、类别编码、归一化/标准化。
4. 训练集和测试集划分。
5. 自行实现最小二乘法；模型及系数计算只使用 NumPy/Pandas，不调用现成回归库或系数求解器。
6. 三组不同特征，分别计算 R² 并比较。
7. 加分：引入合成特征。

## 实验三附件

[Линейная регрессия. Теоретическая часть (1)](https://sunnysubmarines.notion.site/1-f2323e041d6a435191b76b0bc088f106)

- `linear_regression.pdf`：原文件名 `Линейная_регрессия.pdf`，450164 字节，6 页。
- `linear_regression.docx`：原文件名 `Линейная регрессия.docx`，74445 字节。

两份附件均已读取。内容包括多元线性回归、系数含义、最小二乘目标、正规方程、矩阵解与高斯消元，以及五个家庭收入/财产预测储蓄的数值例题。报告使用手写高斯消元，并在 `verification()` 中复现附件的例题。

附件中的部分行列式和中间数字存在排版/笔误，核验采用原始五条观测数据及最后给出的四位小数回归方程。

## 模块二报告模板

[Модуль 2. Шаблон отчёта](https://sunnysubmarines.notion.site/2-4c3e6faa54b14630a267dbde97843b6d)

线性回归部分原始结构：

- Введение
- Описание метода
- Псевдокод метода
- Результаты выполнения
- Примеры использования метода

整个模块后续有 `Сравнение методов`、`Заключение`、`Приложения [Код]`。
本次报告保留适用结构，比较部分比较线性回归的特征方案。尚未实施的实验 4–6 不写虚构结果。模板的“Лабораторная работа 1”是模块内编号，课程总编号为实验 3。

## 数据集

[Student Performance (Multiple Linear Regression), Nikhil Narayan](https://www.kaggle.com/datasets/nikhil7280/student-performance-multiple-linear-regression)

官方描述明确说明：数据是用于演示的合成数据，变量间关系未必对应真实世界；目标指数取值 10–100，并取整。作者许可说明允许分享和使用数据。

下载地址：`https://www.kaggle.com/api/v1/datasets/download/nikhil7280/student-performance-multiple-linear-regression`

原 CSV 的 SHA-256：`93793b00d9026d0b4907df0ca9f88b3696747c7496679d35833bb0fbf9fb57cf`。
