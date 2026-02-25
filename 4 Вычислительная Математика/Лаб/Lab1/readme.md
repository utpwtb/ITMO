实验报告 No.1 《求解线性代数方程组》

1. 选项编号由ISU系统中的小组名单序号决定。
2. 编程语言的选择取决于实践指导教师。
3. 程序中，数值方法必须作为一个独立的子程序/方法/类来实现，输入/输出数据应作为参数传递。
4. 矩阵维度 n ≤ 20 （由最终用户选择：从文件读取或键盘输入）。
5. 必须实现两种矩阵系数输入方式：键盘输入与文件读取（由最终用户选择）。

**对于直接法，必须实现：**

* 基于三角矩阵计算行列式
* 输出三角矩阵（包括变换后的常数列B）
* 输出未知向量：𝑥₁, 𝑥₂, … , 𝑥ₙ
* 输出残差向量：𝑟₁, 𝑟₂, … , 𝑟ₙ
* 使用现成库求解问题并计算行列式。对比所得结果，解释其相似性/差异性。解释需在报告中体现。

**对于迭代法，必须实现：**

* 精度由键盘/文件输入
* 检查对角占优（若原始矩阵不具备对角占优，则进行行/列置换直至达到占优。若无法实现对角占优，则输出相应信息。）
* 输出矩阵范数（可任选一种）
* 输出未知向量：𝑥₁, 𝑥₂, … , 𝑥ₙ
* 输出求解所用的迭代次数
* 输出误差向量：|𝑥ᵢ⁽ᵏ⁾ − 𝑥ᵢ⁽ᵏ⁻¹⁾|

**报告内容：**

* 实验目的
* 方法描述及计算公式
* 程序清单（至少包含方法实现部分）
* 程序运行示例及结果
* 结论
* 报告需提交电子版/纸质版。

**任务方案**

| 方法              | 方案编号                     |
| ----------------- | ---------------------------- |
| 高斯消元法        | 2, 11, 17, 21, 25, 27, 28    |
| 列主元高斯消元法  | 5, 8, 13, 19, 22, 24, 26, 30 |
| 简单迭代法        | 1, 4, 7, 9, 15, 23, 29       |
| 高斯-赛德尔迭代法 | 3, 6, 10, 12, 14, 16, 18, 20 |

**实验答辩思考题：**

1. 什么是线性代数方程组的解？
2. 阐述线性代数方程组无根的判别条件。
3. 评价直接法求解线性代数方程组的优缺点。
4. 评价迭代法求解线性代数方程组的优缺点。
5. 使用高斯消元法求解线性代数方程组时，如何计算行列式？
6. 简述列主元/行主元高斯消元法的核心思想。
7. 什么是迭代法的收敛性？
8. 迭代法求解线性代数方程组收敛的充分条件是什么？
9. 简单迭代法与高斯-赛德尔迭代法的区别是什么？
10. 简述高斯-赛德尔迭代法的核心思想。
11. 在什么情况下应采用列主元高斯消元法？
12. 如何确定高斯消元法求解线性代数方程组的误差？
13. 简述简单迭代法迭代过程的终止准则。
14. 若变换后矩阵的范数大于1，这意味着什么？
15. 若对角元素为零，是否可以使用高斯消元法？

graph TD
    Start([开始]) --> Init[构造增广矩阵 Augmented Matrix<br/>初始化 swapCount = 0, EPSILON = 1e-12]
    
    Init --> OuterLoop{遍历每一列<br/>i = 0 to n-1}
    
    subgraph "前向消元 (Forward Elimination)"
        OuterLoop -- 循环结束 --> BackSub
        OuterLoop -- 进行中 --> FindMax[寻找第 i 列的主元行 l<br/>使得 |a_li| 最大]
        
        FindMax --> CheckSingular{ |a_li| < EPSILON ? }
        CheckSingular -- 是 --> SingularEnd([矩阵奇异，无唯一解])
        
        CheckSingular -- 否 --> CheckSwap{ l != i ? }
        CheckSwap -- 是 --> SwapRows[交换第 i 行与第 l 行<br/>swapCount++]
        CheckSwap -- 否 --> ElimInit
        
        SwapRows --> ElimInit[准备消元<br/>k = i + 1]
        
        ElimInit --> InnerLoop{k < n ?}
        InnerLoop -- 是 --> CalcFactor[计算因子 factor = a_ki / a_ii<br/>a_ki = 0.0]
        CalcFactor --> RowUpdate[遍历 j = i + 1 to n<br/>a_kj = a_kj - factor * a_ij]
        RowUpdate --> NextK[k++] --> InnerLoop
        InnerLoop -- 否 --> NextI[i++] --> OuterLoop
    end

    subgraph "回代求解 (Back Substitution)"
        BackSub[计算最后一个变量<br/>x_n-1 = a_n-1,n / a_n-1,n-1]
        BackSub --> BackLoopInit[逆序遍历变量<br/>i = n-2 down to 0]
        BackLoopInit --> BackLoop{i >= 0 ?}
        BackLoop -- 是 --> CalcSum[计算累加项 sum = Σ a_ij * x_j<br/>j 从 i+1 到 n-1]
        CalcSum --> SolveX[x_i =  a_in - sum / a_ii]
        SolveX --> NextBackI[i--] --> BackLoop
    end

    BackLoop -- 否 --> FinalCalc[计算行列式 det = -1^swapCount * Π a_ii<br/>计算残差 r = Ax - b]
    FinalCalc --> End([返回 SolutionResult, 结束])