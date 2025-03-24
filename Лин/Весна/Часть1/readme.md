# 线性空间中的映射  

本节专门讨论线性空间中的映射。在本课程的前面部分，我们已经涉及了线性空间中的映射问题，特别是在讨论同构线性空间时。在本节中，我们将看到还存在其他几种类型的映射，这些映射具有线性性质或与之相似的性质。主要目标之一是找出适用于此类映射的通用研究方法。  

# 第一讲：线性泛函  

## §1. 引言  

设 \( V \) 是域 \( K \) 上的线性空间。  

**定义 1.1.** 空间 \( V \) 上的线性泛函是指一个函数 \( f: V \rightarrow K \)，对于所有 \( v, v_1, v_2 \in V \) 和所有 \( \lambda \in K \)，满足以下条件：  

(a) 可加性：\( f(v_1 + v_2) = f(v_1) + f(v_2) \)。  

(b) 齐次性：\( f(\lambda v) = \lambda f(v) \)。  

**注 1.1.** 对于任意线性映射 \( f: V \to U \)，以下性质成立：任意向量 \( v_i \in V \) 的线性组合的像等于这些向量的像的线性组合：

\[
f \left( \sum_i \alpha_i v_i \right) = \sum_i \alpha_i f(v_i)
\]

**例 1.1.** 设 \( E \) 是几何向量空间（平面或空间中）并定义了内积 \(\langle x, y \rangle\)。线性形式 \( f(v) \) 可以表示为

\[
f(v) = \langle a, v \rangle
\]

其中 \( a \in E \) 是一个固定向量。

**例 1.2.** 设 \( V = M_n(\mathbb{K}) \) 是域 \( \mathbb{K} \) 上 \( n \) 阶方阵的空间。线性形式可以表示为

\[
f(A) = \operatorname{tr} A, \quad A \in M_n(\mathbb{K})
\]

**例 1.3.** 设 \( V = \mathbb{R}^{\leq n}[x] \) 是次数不超过 \( n \) 的多项式空间。线性形式可以表示为

\[
f(p) = p(x) \bigg|_{x=x_0}
\]

**例 1.4.** 设 \( V = \mathbb{K}^n \) 是元素 \( v = (v_1, v_2, \ldots, v_n) \) 的算术空间。线性形式可以表示为

\[
f(v) = \sum_{i=1}^{n} \alpha_i v_i
\]

**注 1.2.** 最后一个例子的重要性在于，任何线性形式都可以表示为这种形式。  

假设 \( V \) 是一个有限维线性空间。在 \( V \) 中固定一个基 \(\{e_i\}_{i=1}^n\)，其中 \( n = \dim V \)。  

**定义 1.2.** 线性形式 \( f \) 的系数 \(\varphi_i\) 称为该线性形式在空间基向量上的值。

\[
f(e_i) = \varphi_i
\]

**定理 1.1.** _给定线性形式等价于给定其在基形式上的值，即给定其系数。_ 

**证明.** 设在线性空间 \( V \) 的选定基 \(\{e_i\}_{i=1}^n\) 中，线性形式 \( f \) 由一组系数 \(\{\varphi_i\}_{i=1}^n\) 给定。则对于任意向量 \( v = \sum_{i=1}^n v^i e_i \in V \)，有：

\[
f(v) = f\left(\sum_{i=1}^n v^i e_i\right) = \sum_{i=1}^n f(v^i e_i) = \sum_{i=1}^n v^i f(e_i) = \sum_{i=1}^n v^i \varphi_i
\]

因此，我们得到任意向量的像由该向量的坐标和线性形式的系数唯一确定，其中这两组数都是在同一基中求得的。

## §2. 对偶空间  

考虑在线性空间 \( V \) 中定义的线性形式的集合。

**定义 2.1.** 线性形式 \( f \) 和 \( g \) 称为**相等**，如果  
\[
f = g \quad \Leftrightarrow \quad f(v) = g(v), \quad \forall v \in V
\]

**定义 2.2.** 线性形式 \( \theta \) 称为**零形式**，如果  
\[
\theta(v) = 0, \quad \forall v \in V
\]

显然，我们可以在形式的集合上定义运算。  

**定义 2.3.** 线性形式 \( f \) 和 \( g \) 的**和**称为映射 \( h = f + g \)，其满足

\[
h(v) = f(v) + g(v), \quad \forall v \in V
\]

**引理 2.1.** _映射 \( h \) 是一个线性形式。_

**证明.** 我们首先证明加性性质：

\[
h(v_1 + v_2) = f(v_1 + v_2) + g(v_1 + v_2) = f(v_1) + f(v_2) + g(v_1) + g(v_2) = 
\]
\[
= (f(v_1) + g(v_1)) + (f(v_2) + g(v_2)) = h(v_1) + h(v_2)
\]

齐次性质的证明类似。

**定义 2.4.** 线性形式 \( f \) 与数 \(\alpha \in \mathbb{K}\) 的**积**称为映射 \( l = \alpha f \)，其满足

\[
l(v) = \alpha \cdot f(v), \quad \forall v \in V
\]

**证明.** 类似于线性形式和的引理。

根据上述定义和引理，可以得出以下结论的正确性。

**定理 2.1.** _定义在线性空间 \( V \) 上的**线性形式==集合==** \( V^* \) 构成一个线性（对偶）空间。_

考虑空间 \( V \) 中的一个基 \(\{e_i\}_{i=1}^n\)。我们引入一组线性形式 \(\{f^j\}_{j=1}^n\)，定义如下：

\[
f^j(v) = v_j,
\]

其中 \( f^j \) 返回向量 \( v \in V \) 在基 \(\{e_i\}_{i=1}^n\) 中的第 \( j \) 个坐标。

显然，对于这组线性形式，以下性质成立：

\[
f^j(e_i) = \delta_i^j = 
\begin{cases} 
1, & \text{如果 } i = j, \\
0, & \text{如果 } i \neq j 
\end{cases}
\]

**引理 2.2.** _线性形式集合 \(\{f^{j}\}_{j=1}^{n}\) 是对偶空间 \(V^{*}\) 的一个基。_

**证明.** 为了证明这一结论，需要证明该集合的完备性和线性无关性。首先证明完备性：

对于任意线性形式 \( f \in V^{*} \)，可以表示为：

\[
f(v) = \sum_{i=1}^{n} \phi_i v^i = \sum_{i=1}^{n} \phi_i f^i(v) = \left( \sum_{i=1}^{n} \phi_i f^i \right)(v)
\]

类似地，证明线性无关性。假设存在一组系数 \(\alpha_i\)，使得线性组合等于零形式：

\[
\sum_{i=1}^{n} \alpha_i f^i = \theta
\]

将这个零形式作用于任意基向量 \( e_k \)，得到：

\[
\left( \sum_{i=1}^{n} \alpha_i f^i \right)(e_k) = \theta(e_k) = 0
\]

根据线性形式的定义和性质，有：

\[
\sum_{i=1}^{n} \alpha_i f^i(e_k) = 0 \Rightarrow \alpha_k f^k(e_k) = 0 \Rightarrow \alpha_k = 0
\]

因此，集合 \(\{f^{j}\}_{j=1}^{n}\) 是线性无关的，并且是 \(V^{*}\) 的一个基。

**注 2.1.** 对于空间 \( V \) 中的每一个基，都可以找到唯一一个与之关联的对偶基，其关系如上所述。

现在，我们来看当空间 \( X \) 的基发生变换时，对偶基如何变换。

**定理 2.2.** 设 \(\{f^{i}\}_{i=1}^{n}\) 和 \(\{\widetilde{f}^{l}\}_{l=1}^{n}\) 分别是与基 \(\{e^{j}\}_{j=1}^{n}\) 和 \(\{\widetilde{e}^{k}\}_{k=1}^{n}\) 对偶的基。则

\[
\widetilde{f}^{l} = \sum_{i=1}^{n}\sigma_{i}^{l}f^{i}
\]

其中 \((\sigma_{i}^{l}) = S\) 是过渡矩阵的逆矩阵的元素，设 \((\tau_{k}^{j}) = T\) 是从 \(\{e^{j}\}_{j=1}^{n}\) 到 \(\{\widetilde{e}^{k}\}_{k=1}^{n}\) 的过渡矩阵。

**证明.** 根据对偶基的定义，我们有

\[
\vec{f}^{l}(\vec{e}_{k}) = \sum_{i=1}^{n}\sigma_{i}^{l}f^{i}\left(\sum_{j=1}^{n}\tau_{k}^{j}e_{j}\right) = \sum_{i=1}^{n}\sum_{j=1}^{n}\sigma_{i}^{l}\tau_{k}^{j}f^{i}(e_{j})= 
\]
\[
= \sum_{i=1}^{n}\sum_{j=1}^{n}\sigma_{i}^{l}\tau_{k}^{j}\delta_{j}^{i}=\sum_{i=1}^{n}\sigma_{i}^{l}\tau_{k}^{i}=\delta_{k}^{l}
\]

由此可知，由 \(\sigma_{i}^{l}\) 组成的矩阵与由 \(\tau_{k}^{j}\) 组成的过渡矩阵的乘积必须等于单位矩阵。这正是逆矩阵的定义。

**定理 2.3.** _当从基 \(\{f^{i}\}_{i=1}^{n}\) 转换到基 \(\{\widetilde{f}^{i}\}_{i=1}^{n}\) 时，形式在 \(V^{*}\) 中的坐标变换为_

\[
\widetilde{\eta_{l}} = \sum_{i=1}^{n} \tau_{l}^{i} \eta_{i} \qquad (\widetilde{\eta}^{1}, \widetilde{\eta}^{2}, \ldots, \widetilde{\eta}^{n}) = (\eta^{1}, \eta^{2}, \ldots, \eta^{n}) \cdot T
\]

**证明.**

\[
\widetilde{\eta_{l}} = f(\widetilde{e_{l}}) = \sum_{i=1}^{n} \eta_{i} f^{i} \left( \sum_{j=1}^{n} \tau_{l}^{j} e_{j} \right) = \sum_{i=1}^{n} \sum_{j=1}^{n} \eta_{i} \tau_{l}^{j} f^{i}(e_{j}) = 
\]
\[
= \sum_{i=1}^{n} \sum_{j=1}^{n} \eta_{i} \tau_{l}^{j} \delta_{j}^{i} = \sum_{i=1}^{n} \tau_{l}^{i} \eta_{i}
\]

**注 2.2.** 线性形式的坐标变换规律与空间 \(V\) 的基变换规律完全相同。因此，它们也被称为**协变向量**。

## §3. 对偶空间的同构性

根据已证明的对偶空间基的性质，我们有以下结论：

**引理 3.1.** _空间 \( V \) 与其对偶空间 \( V^* \) 是同构的。_

**证明**：这一结论的成立基于以下事实：
\[
\dim V = \dim V^*
\]
（基的维数相同），因此有
\[
V \simeq \mathbb{K}^n \simeq V^*
\]

同构关系通过建立空间 \( V \) 和 \( V^* \) 基之间的对应关系来实现。

值得注意的是，求对偶空间的操作可以迭代进行。

**定义3.1** 第二对偶空间定义为V** = (V*)*。

第二对偶空间的元素是对线性形式进行运算的线性函数。

**定理3.1** 在空间V和V**之间存在不依赖于基选择的同构关系（典范同构）。

**证明** 考虑第二对偶空间的元素v̂, û ∈ V**：

$\hat{v}: V^* \to \mathbb{K}$, 其中 $\hat{v}(f) \in \mathbb{K}$ 满足：

$$
\begin{aligned}
\hat{v}(f + g) &= \hat{v}(f) + \hat{v}(g) \\
\hat{v}(\alpha f) &= \alpha \hat{v}(f) \\
(\hat{v} + \hat{u})(f) &= \hat{v}(f) + \hat{u}(f) \\
(\alpha \hat{v})(f) &= \alpha \hat{v}(f)
\end{aligned}
$$

典范同构通过以下对应关系建立：

$$
\hat{x} \leftrightarrow x : \quad \hat{v}(f) = f(v) \quad \forall f \in V^*
$$

**注3.1** 这个结论对后续讨论的张量分析有重要意义。

# 线性空间中的映射

## §1. 引言

设V是域K上的线性空间。

**定义1.1.** 线性空间V(K)上的**双线性形式**是指满足以下条件的函数b: V×V→K：对于任意x,x₁,x₂,y,y₁,y₂∈V和任意λ₁,λ₂∈K，有：

(a) 关于第一个参数的线性性：
$$
b(\lambda_1 x_1 + \lambda_2 x_2,\, y) = \lambda_1 b(x_1,\, y) + \lambda_2 b(x_2,\, y)
$$

(b) 关于第二个参数的线性性：
$$
b(x,\, \lambda_1 y_1 + \lambda_2 y_2) = \lambda_1 b(x,\, y_1) + \lambda_2 b(x,\, y_2)
$$  

**例 1.1.** 设 \( f, g \in V^* \) 是空间 \( V(\mathbb{K}) \) 上的线性形式。双线性形式可以定义为  

\[b : V \times V \to \mathbb{K}, \quad b(x, y) = f(x) \cdot g(y)\]  

**例 1.2.** 平面（或空间）上几何向量的点积对每个自变量都是线性的，因此是一种双线性形式。  

**例 1.3.** 设 \( V = \mathbb{K}^n \) 是一个算术空间。双线性形式可以表示为  

\[b(x, y) = \sum_{i=1}^n \sum_{j=1}^n \beta_{ij} \xi^i \eta^j,\]  

其中 \( x = (\xi^1, \xi^2, \ldots, \xi^n)^T \in V \)，\( y = (\eta^1, \eta^2, \ldots, \eta^n)^T \in V \)。  

**注 1.2.** 最后一个例子的重要性在于，任何双线性形式都可以表示为这种形式。  

考虑 \( \text{Bil}_K(V) \) —— 所有定义在 \( V \) 上的双线性形式的集合。对于这个集合，以下性质成立：  

(a) 双线性形式 \( b, b' \in \text{Bil}_K(V) \) 相等，当且仅当它们在所有相同的自变量对上的取值相等：  

\[b = b' \quad \Leftrightarrow \quad b(x, y) = b'(x, y) \quad \forall x, y \in V\]  

(6) 存在零双线性形式 \(\theta \in \text{Bil}_K(V)\)，它在任意自变量对上的取值均为 \(0 \in \mathbb{K}\)：  

\[\theta \in \text{Bil}_K(V): \quad \theta(x, y) = 0, \quad \forall x, y \in V\]  

(a) 可以定义双线性形式 \(b, b' \in \text{Bil}_K(V)\) 的和为如下映射：  

\[c = b + b' \iff c(x, y) = b(x, y) + b'(x, y), \quad \forall x, y \in V\]  

(r) 可以定义双线性形式 \(b \in \text{Bil}_K(V)\) 与标量 \(\lambda \in \mathbb{K}\) 的乘积为如下映射：  

\[d = \lambda b \iff d(x, y) = \lambda b(x, y), \quad \forall x, y \in V\]  

**引理 1.1.** _映射 \( c \) 和 \( d \) 是双线性形式。_

**证明.** 类似于线性形式的相应命题。

**引理 1.2.** _集合 \(\operatorname{Bil}_{\mathbb{K}}(V)\) 具有线性空间的结构。_

**证明.** 可以直接验证线性空间的公理来确认。

**定义 1.2.** 双线性形式 \( b \in \operatorname{Bil}_{\mathbb{K}}(V) \) 称为对称的，如果满足 \( b(x,y) = b(y,x) \)。

**定义 1.3.** 双线性形式 \( b \in \operatorname{Bil}_{\mathbb{K}}(V) \) 称为反对称的，如果满足 \( b(x,y) = -b(y,x) \)。

**注 1.3.** 对称（反对称）双线性形式的集合构成 \(\operatorname{Bil}_{\mathbb{K}}(V)\) 中的线性子空间 \(\operatorname{Bil}^{S}_{\mathbb{K}}(V)\)（\(\operatorname{Bil}^{AS}_{\mathbb{K}}(V)\)）。

从任意双线性形式可以构造对称形式：

\[
b^{S}(x,y) = \frac{1}{2}(b(x,y) + b(y,x)), \qquad b^{S} \in \operatorname{Bil}^{S}_{\mathbb{K}}(V)
\]

类似地，可以构造反对称形式：

\[
b^{AS}(x,y) = \frac{1}{2}(b(x,y) - b(y,x)), \qquad b^{AS} \in \operatorname{Bil}^{AS}_{\mathbb{K}}(V)
\]

**引理 1.3.** _根据上述方法构造的对称形式和反对称形式的和，可以得到原始的双线性形式。_

**证明.** 通过直接验证可得：

\[b^S(x,y) + b^{AS}(x,y) = \frac{1}{2}(b(x,y) + b(y,x)) + \frac{1}{2}(b(x,y) - b(y,x)) = b(x,y)\]

**引理 1.4.** 双线性形式空间可以表示为对称和反对称双线性形式子空间的直和。

\[
\text{Bil}_K(V) = \text{Bil}_K^S(V) \oplus \text{Bil}_K^{AS}(V)
\]

**证明.** 前述构造对称（反对称）形式的过程表明：

\[
\text{Bil}_K(V) = \text{Bil}_K^S(V) + \text{Bil}_K^{AS}(V)
\]

现证明该和为直和。设双线性形式 \( h(x,y) \) 满足 \( h \in \text{Bil}_K^S(V) \cap \text{Bil}_K^{AS}(V) \)，则有：

\[
\begin{cases} 
h(x,y) = h(y,x) \\
h(x,y) = -h(y,x)
\end{cases}
\Rightarrow h(y,x) = -h(y,x) \Rightarrow h(x,y) = 0 \quad \forall x,y \in V
\]

由于子空间的交集中仅包含零双线性形式，故该和为直和。

## §2. 双线性形式的矩阵

假设 \( V \) 是一个有限维线性空间。在 \( V \) 中固定一个基 \( \{e_i\}_{i=1}^n \)，其中 \( n = \dim V \)。

**定义 2.1.** 双线性形式 \( b(x, y) \) 的系数 \( \beta_{ij} \) 定义为该形式在空间基向量上的取值：

\[b(e_i, e_j) = \beta_{ij}\]

**定理 2.1.** *给定一个双线性形式等价于给定其在基向量上的取值，即给定其系数。*

**证明.** 设在线性空间 \( V \) 的选定基 \( \{e_i\}_{i=1}^n \) 中，双线性形式 \( b(x, y) \) 由一组系数 \( \{\beta_{ij}\}_{i,j=1}^n \) 给出。那么对于任意 \( x = \sum_{i=1}^n \xi^i e_i \) 和 \( y = \sum_{j=1}^n \eta^j e_j \)，有：

\[b(x, y) = b \left( \sum_{i=1}^n \xi^i e_i, \sum_{j=1}^n \eta^j e_j \right) = \sum_{i=1}^n \sum_{j=1}^n \xi^i \eta^j b(e_i, e_j) = \sum_{i=1}^n \sum_{j=1}^n \xi^i \eta^j \beta_{ij}\]

类似于线性形式（其系数可以表示为一个行向量），双线性形式也有类似的表示方法。

**定义 2.2.** 双线性形式 \( b(x, y) \) 的矩阵是指由其系数构成的矩阵 \( B \)。

**引理 2.1.** 双线性形式空间 \( \text{Bil}_K(V) \) 与方阵空间 \( M_n(K) \) 同构。

**证明.** 同构关系通过以下方式建立：

\[b \leftrightarrow B \quad b' \leftrightarrow B'\]

\[b + b' \leftrightarrow B + B'\]

\[\lambda b \leftrightarrow \lambda B\]

双线性形式的线性运算与矩阵运算之间的对应关系可通过直接验证定义来确认。

**注 2.1.** 基于同样的类比，当 \( \dim V = n \) 时，我们曾建立 \( V^* \simeq K^n \) 的同构关系。这里我们再次观察到空间"坐标化"的思想。在此情况下，双线性形式的"坐标"就是其矩阵的系数。

**注 2.2.** 对称（反对称）双线性形式对应的矩阵是对称（反对称）矩阵：

\[b^S \leftrightarrow B_S \quad B_S = B_S^T\]

\[b^{AS} \leftrightarrow B_{AS} \quad B_{AS} = -B_{AS}^T\]

由于双线性形式的矩阵是依赖于基选择的，因此基变换将导致矩阵形式的改变。这一现象与我们在线性形式的系数行向量中所遇到的情况完全类似。

**定理 2.2.** *双线性形式 \( b(x, y) \) 在不同基 \(\{e_i\}_{i=1}^n\) 和 \(\{e_j'\}_{j=1}^n\) 下的矩阵 \( B \) 和 \( B' \) 满足如下关系：*

\[B' = C^T BC\]

其中 \( C = (e_j') \) 表示从基 \(\{e_i\}_{i=1}^n\) 到基 \(\{e_j'\}_{j=1}^n\) 的过渡矩阵。

**证明.** 设已知过渡矩阵 \( C = (c_j^i) \)，则新基的向量可通过旧基表示为：

\[e_j' = \sum_{i=1}^n c_j^i e_i\]

利用此表达式计算双线性形式在新基下的矩阵元素：

\[\beta_{ij}' = b(e_i', e_j') = b \left( \sum_{k=1}^n c_k^i e_k, \sum_{l=1}^n c_l^j e_l \right) = \sum_{k=1}^n \sum_{l=1}^n c_k^i c_l^j b(e_k, e_l) = \sum_{k=1}^n \sum_{l=1}^n c_k^i c_l^j \beta_{kl}\]

其中 \(\beta_{kl} = b(e_k, e_l)\)（对所有 \(k, l = 1,...,n\)）表示双线性形式在旧基下的系数矩阵。这个双重求和运算本质上就是矩阵乘法，可以表示为：

\[B' = C^T BC\]

这个结论可以通过直接展开矩阵乘法的指标形式来验证。

## §3. 二次型

设 \( V(\mathbb{K}) \) 是域 \(\mathbb{K}\) 上的线性空间，并假设该空间上定义了一个双线性形式 \( b : V \times V \rightarrow \mathbb{K} \)。

**定义 3.1.** 线性空间 \( V \) 上的二次型是指由双线性形式 \( b(x, y) \) 按如下方式构造的映射 \( q(v) \)：

\[q : V \rightarrow \mathbb{K}, \quad q(v) = b(v, v), \quad \forall v \in V\]

**注 3.1.** 任何双线性形式 \( b(x, y) \) 都可以通过将其定义域从 \( V \times V \) 限制到对角线子集 \(\{(v, v) : v \in V\} \subset V \times V\) 来得到一个二次函数 \( q(v) \)。

**引理 3.1.** *二次型是关于向量坐标的2次齐次多项式。*

**引理 3.1.** 二次型是关于向量坐标的二次齐次多项式。

**证明.** 通过以下推导可得：

\[q(\lambda v) = b(\lambda v, \lambda v) = \lambda^2 b(v, v) = \lambda^2 q(v)\]

由此我们证明了二次型是二阶齐次函数。现在固定空间 \(V\) 的一组基 \(\{e_i\}_{i=1}^n\)。任意向量可唯一表示为 \(v = \sum_{i=1}^n v^i e_i\)。那么二次型在坐标表示下具有如下形式：

\[q(v) = q\left( \sum_{i=1}^n v^i e_i \right) = b\left( \sum_{i=1}^n v^i e_i, \sum_{j=1}^n v^j e_j \right) = \sum_{i=1}^n \sum_{j=1}^n v^i v^j b(e_i, e_j) = \sum_{i=1}^n \sum_{j=1}^n v^i v^j \beta_{ij}\]

其中 \(\beta_{ij}\) 是构造二次型 \(q(v)\) 所用双线性形式的系数。

**引理 3.2.** 通过二次型 \(q(v)\) 可以唯一地恢复出双线性形式 \(b(x, y)\) 的对称分量。

**证明.** 考虑向量 \(x, y \in V\) 的和的二次型：

\[q(x+y) = b(x+y, x+y) = b(x,x)+b(x,y)+b(y,x)+b(y,y) = q(x)+b(x,y)+b(y,x)+q(y)\]

由此可得：

\[b(x,y) + b(y,x) = q(x+y) - q(x) - q(y)\]

若限定双线性形式为对称形式，即 \(b \in \text{Bil}^S(V)\)，则有：

\[b(x,y) = \frac{1}{2} (q(x+y) - q(x) - q(y))\]

**注 3.2.** 上述引理确立了二次型集合与对称双线性形式集合之间的一一对应关系。

**注 3.3.** 任何反对称双线性形式对应的二次型都为零形式。

**注 3.4.** 设双线性形式由系数为 \(\beta_{ij}\) 的矩阵描述，则二次型也可表示为：

\[q(v) = \sum_{i=1}^{n} \sum_{j=1}^{n} \beta_{ij} v^i v^j = \sum_{i=1}^{n} \beta_{ii}(v^i)^2 + 2 \sum_{i<j} \beta_{ij} v^i v^j\]

其中 \(v^i\) 表示向量 \(v\) 在选定基下的第 \(i\) 个坐标分量。

# 多重线性形式

## §1. 基本定义

**定义 1.1.** 线性空间 \( V \) 上的多重线性形式是指如下形式的映射：

\[A : \underbrace{V \times \ldots \times V}_{p} \times \underbrace{V^* \times \ldots \times V^*}_{q} \rightarrow \mathbb{K}\]

该映射对每个参数都具有线性性质：

\[A(x_1, \ldots, \alpha x_i' + \beta x_i'' , \ldots, x_p; \varphi^1, \ldots, \varphi^q) = \alpha A(x_1, \ldots, x_i', \ldots, x_p; \varphi^1, \ldots, \varphi^q) + \beta A(x_1, \ldots, x_i'', \ldots, x_p; \varphi^1, \ldots, \varphi^q),\]

其中 \( x_i \in V \)，\( \varphi^j \in V^* \)。

**定义 1.2.** 多重线性形式的**价**（valency）是指一对数 \((p, q)\)，用于表示该映射的向量参数和对偶向量参数（线性形式）的数量。  

**例 1.1.** 向量空间 \(V\) 上的线性形式是如下映射：  
\[f : V \rightarrow \mathbb{K}\]  

因此，线性形式 \(\varphi \in V^*\) 是一个 \((1, 0)\) 价的多重线性形式。  

**例 1.2.** 对偶空间 \(V^*\) 上的线性形式是如下映射：  
\[\hat{x} : V^* \rightarrow \mathbb{K}\]  

因此，线性形式 \(\hat{x} \in V^{**}\) 是一个 \((0, 1)\) 价的多重线性形式。然而，先前讨论过，在空间 \(V\) 和 \(V^{**}\) 之间存在一个自然同构，定义为：  
\[x \leftrightarrow \hat{x} \quad (\hat{x}, f) = (f, x) \quad \forall f \in V^*\]  
\[x \in V, \quad \hat{x} \in V^{**}\]  

因此，可以断言，\((0, 1)\) 价的多重线性形式在自然同构下唯一对应于线性空间 \(V\) 中的一个元素。  

**例 1.3.** 向量空间 \( V \) 上的双线性形式是如下映射：  
\[ g : V \times V \rightarrow \mathbb{K} \]  

因此，双线性形式是一个 \((2, 0)\) 价的多重线性形式。双线性形式的例子包括两个几何向量的点积：  
\[g(x_1, x_2) = (x_1, x_2),\]  
以及之前讨论过的其他所有双线性形式的例子。  

**例 1.4.** 我们还可以考虑三线性形式，即如下映射：  
\[\psi : V \times V \times V \rightarrow \mathbb{K}\]  
它是一个 \((3, 0)\) 价的多重线性形式。这类映射在几何中也有出现，例如三个向量的混合积（标量三重积）。  

## §2. 多重线性形式的运算

设 \( \Omega_q^p \) 表示所有 \((p, q)\) 价的多重线性形式的集合。

**定义 2.1.** 称两个相同价数的多重线性形式 \( A, B \in \Omega_q^p \) **相等**，如果对于任意的向量组 \( x_1, x_2, \ldots, x_p \in V \) 和对偶向量组 \( \varphi^1, \varphi^2, \ldots, \varphi^q \in V^* \)，均有：

\[A(x_1, x_2, \ldots, x_p; \varphi^1, \varphi^2, \ldots, \varphi^q) = B(x_1, x_2, \ldots, x_p; \varphi^1, \varphi^2, \ldots, \varphi^q)\]

**定义 2.2.** **零形式** \( \Theta \in \Omega_q^p \) 是指满足以下条件的多重线性形式：

\[\Theta(x_1, x_2, \ldots, x_p; \varphi^1, \varphi^2, \ldots, \varphi^q) = 0 \quad \forall x_i \in V, \forall \varphi^j \in V^*\]

设 \( A \) 和 \( B \) 是 \((p, q)\) 价的多重线性形式。下面定义它们的运算。  

### 2.1. 线性运算

**定义 2.3.** 映射 \( C = \mathcal{A} + \mathcal{B} \) 称为多重线性形式 \( \mathcal{A} \) 和 \( \mathcal{B} \) 的和，如果对于任意的向量组 \( x_1, x_2, \ldots, x_p \in V \) 和对偶向量组 \( \varphi^1, \varphi^2, \ldots, \varphi^n \in V^* \)，满足：

\[C(x_1, x_2, \ldots, x_p; \varphi^1, \varphi^2, \ldots, \varphi^n) = \mathcal{A}(x_1, x_2, \ldots, x_p; \varphi^1, \varphi^2, \ldots, \varphi^n) + \mathcal{B}(x_1, x_2, \ldots, x_p; \varphi^1, \varphi^2, \ldots, \varphi^n)\]

**引理 2.1.** 由多重线性形式 \( \mathcal{A}, \mathcal{B} \in \Omega_q^p \) 的和定义的映射 \( C \) 仍然是 \( \Omega_q^p \) 中的多重线性形式。

**证明.** 证明方法与线性形式和双线性形式的情况类似。

类似地，可以定义数乘运算（乘以标量）。  

**定义 2.4.** 映射 \(\lambda\mathcal{A}\) 称为多重线性形式 \(\mathcal{A}\) 与标量 \(\lambda\) 的数乘，如果对于任意的向量组 \(x_{1},x_{2},\ldots,x_{p}\in V\) 和对偶向量组 \(\varphi^{1},\varphi^{2},\ldots,\varphi^{q}\in V^{*}\)，满足：

\[(\lambda\mathcal{A})(x_{1},x_{2},\ldots,x_{p};\varphi^{1},\varphi^{2},\ldots, \varphi^{q})=\lambda\cdot\mathcal{A}(x_{1},x_{2},\ldots,x_{p};\varphi^{1},\varphi ^{2},\ldots,\varphi^{q})\]

**引理 2.2.** 由多重线性形式 \(\mathcal{A}\in\Omega_{q}^{p}\) 与标量 \(\lambda\in\mathbb{K}\) 的数乘定义的映射 \(\lambda\mathcal{A}\) 仍然是 \(\Omega_{q}^{p}\) 中的多重线性形式。

**证明.** 证明方法与线性形式和双线性形式的情况类似。

**定理 2.1.** 所有 \((p,q)\) 价的多重线性形式构成的集合 \(\Omega_{q}^{p}\) 形成一个线性空间。

**证明.** 只需验证线性空间的公理即可。  

### 2.2 多重线性形式的乘积

**定义 2.5.** 对于多重线性形式 \( A \in \Omega_{q_1}^{p_1} \) 和 \( B \in \Omega_{q_2}^{p_2} \)，它们的乘积 \( C = A \cdot B \) 定义为满足下列条件的映射：

\[
A(x_1, \ldots, x_{p_1}; \varphi^1, \ldots, \varphi^{q_1}) \cdot B(x_{p_1+1}, \ldots, x_{p_1+p_2}; \varphi^{q_1+1}, \ldots, \varphi^{q_1+q_2}) = C(x_1, \ldots, x_{p_1}, x_{p_1+1}, \ldots, x_{p_1+p_2}; \varphi^1, \ldots, \varphi^{q_1}, \varphi^{q_1+1}, \ldots, \varphi^{q_1+q_2})
\]

**例 2.1.** 双线性形式 \( b(x_1, x_2) \in \Omega_q^p \) 可以表示为：
\[
b(x_1, x_2) = f(x_1) \cdot g(x_2),
\]
其中 \( f, g \in \Omega_q^p = V^* \) 是线性形式。

**注记 2.1.** 两个价数分别为 \((p_1, q_1)\) 和 \((p_2, q_2)\) 的多重线性形式的乘积总可以得到一个 \((p_1 + p_2, q_1 + q_2)\) 价的多重线性形式。然而，并非所有 \((p, q)\) 价的多重线性形式都能分解为两个价数分别为 \((p_1, q_1)\) 和 \((p_2, q_2)\) 的多重线性形式的乘积，即使满足 \( p_1 + p_2 = p \) 且 \( q_1 + q_2 = q \)。

**引理 2.3.** 由多重线性形式乘积定义的映射 \( C \) 仍然是多重线性形式，且满足：
\[
C \in \Omega_{q_1+q_2}^{p_1+p_2}
\]  

**证明.** 不失一般性，我们只需证明其对第一个向量参数的线性性。其余参数的证明可类似进行，但记录会变得相当繁琐。设多重线性形式的乘积定义如下：

\[
C(x,\ldots,\ldots) = \mathcal{A}(x,\ldots,\ldots) \cdot \mathcal{B}(\ldots,\ldots,\ldots),
\]

其中省略号表示根据前述定义的其他所有参数。

当参数 \( x \) 表示为线性组合 \( x = \alpha_1 x_1 + \alpha_2 x_2 \) 时，有

\[
\begin{aligned}
C(\alpha_1 x_1 + \alpha_2 x_2, \ldots, \ldots) &= \mathcal{A}(\alpha_1 x_1 + \alpha_2 x_2, \ldots, \ldots) \cdot \mathcal{B}(\ldots,\ldots) \\
&= (\alpha_1 \mathcal{A}(x_1, \ldots, \ldots) + \alpha_2 \mathcal{A}(x_2, \ldots, \ldots)) \cdot \mathcal{B}(\ldots,\ldots) \\
&= \alpha_1 \mathcal{A}(x_1, \ldots, \ldots) \cdot \mathcal{B}(\ldots,\ldots) + \alpha_2 \mathcal{A}(x_2, \ldots, \ldots) \cdot \mathcal{B}(\ldots,\ldots) \\
&= \alpha_1 C(x_1, \ldots, \ldots) + \alpha_2 C(x_2, \ldots, \ldots),
\end{aligned}
\]

这里利用了映射 \( \mathcal{A} \) 的多重线性性质。由于该映射对每个参数都是线性的，上述推理对其所有参数集都成立。同时由于映射 \( \mathcal{B} \) 也是多重线性的，映射 \( C \) 对 \( \mathcal{B} \) 参数集中的每个参数也都保持线性性。

（注：证明通过选取典型参数展示了乘积映射保持线性性的关键步骤，同时指出该性质可推广至所有参数。最后强调了该构造对两个多重线性形式的普适性。）  

### 2.3 多重线性形式乘积的性质

(a) 不可交换性  
\[ \mathcal{A} \cdot \mathcal{B} \neq \mathcal{B} \cdot \mathcal{A} \]

该性质直接源于乘积定义中参数的顺序性。为说明这一点，考虑由线性形式 \( f^1, f^2 \in V^* \) 构成的简单例子：

\[
\begin{align*}
C_1 &= f^1 \cdot f^2 &\Rightarrow & C_1(x,y) &= f^1(x) \cdot f^2(y) \\
C_2 &= f^2 \cdot f^1 &\Rightarrow & C_2(x,y) &= f^2(x) \cdot f^1(y)
\end{align*}
\]

显然当 \( f^1 \neq f^2 \) 时 \( C_1 \neq C_2 \)。

(6) 结合律  
\[ \mathcal{A} \cdot (\mathcal{B} \cdot \mathcal{C}) = (\mathcal{A} \cdot \mathcal{B}) \cdot \mathcal{C} \]

(a) 零形式性质  
\[ \mathcal{A} \cdot \Theta_{(p_2,q_2)} = \Theta_{(p_1,q_1)} \cdot \mathcal{B} = \Theta_{(p_1+p_2,q_1+q_2)} \]

(r) 运算协调律（分配律）  
\[
\begin{aligned}
&\mathcal{A} \cdot (\mathcal{B} + \mathcal{C}) = \mathcal{A} \cdot \mathcal{B} + \mathcal{A} \cdot \mathcal{C} \\
&(\mathcal{A} + \mathcal{B}) \cdot \mathcal{C} = \mathcal{A} \cdot \mathcal{C} + \mathcal{B} \cdot \mathcal{C} \\
&(\alpha \mathcal{A}) \cdot \mathcal{B} = \alpha(\mathcal{A} \cdot \mathcal{B}) = \mathcal{A} \cdot (\alpha \mathcal{B})
\end{aligned}
\]

（注：性质(a)通过具体构造展示了非交换性；结合律保持张量积结构；零形式性质说明零形式的吸收性；分配律则建立了乘积与线性运算的兼容关系。）  

### §3. 多重线性形式的张量

在 \( V(\mathbb{K}) \) 中固定基 \(\{e_i\}_{i=1}^n\)，并构造其对偶基 \(\{f^j\}_{j=1}^n\) 于空间 \(V^*\) 中。这两个基满足以下关系：

\[
f^j(e_i) = \delta_i^j = 
\begin{cases} 
1, & i = j \\
0, & i \neq j 
\end{cases}
\]

**定义 3.1.** 多重线性形式 \(\mathcal{C}\) 的**张量**（其价为 \((p, q)\)）是指由 \(n^{p+q}\) 个标量组成的集合，这些标量由多重线性形式作用于所有可能的基向量组合得到：

\[
e_{i_1,i_2,\ldots,i_p}^{j_1,j_2,\ldots,j_q} = \mathcal{C}(e_{i_1}, e_{i_2},\ldots, e_{i_p}; f^{j_1}, f^{j_2}, \ldots, f^{j_q}),
\]

其中，指标 \(i_1, i_2, \ldots, i_p\) 和 \(j_1, j_2, \ldots, j_q\) 的取值范围为 \(1, \ldots, n\)，而 \(n = \dim V\) 是空间 \(V\) 的维数。

（注：此定义将多重线性形式在基下的表现具体化为张量，其分量完全由形式在基向量上的作用决定，为后续的张量分析奠定了基础。）  

### 关于哑指标的说明

在进一步讨论之前，我们需要指出一个重要事实：在分析线性对象时，大量指标的使用常常会导致理论和张量实际应用中频繁出现求和运算。为此，我们引入所谓的**爱因斯坦求和约定**（或称哑指标约定）。在本主题背景下，我们约定如下：

(a) **重复指标求和**：若单项式中出现相同的上标和下标，则默认对该指标求和：  
\[
a_i b^i = \sum_{i=1}^n a_i b^i
\]

(6) **哑指标性质**：求和指标的符号可任意替换（因其仅为求和记号）：  
\[
a_i b^i = a_j b^j = a_k b^k
\]

(b) **指标平衡原则**：若非哑指标，则等式两边的自由指标必须严格匹配（包括顺序和位置）：  
\[
a^k b_k = c^j d_j \quad \text{（有效）}  
\]  
而  
\[
a^k b_j \neq c^m d_n \quad \text{（无效，指标不匹配）}
\]

**定理 3.1.** 张量的定义等价于其在空间 \( V \) 和 \( V^* \) 的一对基下的分量表示。

（注：爱因斯坦约定通过隐式求和显著简化了张量运算的表示，同时指标平衡原则确保了表达式的数学一致性。此定理确立了张量与其坐标表示之间的等价关系。）  

**证明.** 考虑向量组 \(x_{1},\ldots,x_{p}\) 和线性形式组 \(\varphi^{1},\ldots,\varphi^{q}\) 在基下的展开式：

\[
\begin{aligned}
x_{k} &= \sum_{i=1}^{n}\xi_{k}^{i}e_{i} = \xi_{k}^{i}e_{i} \\
\varphi^{i} &= \sum_{j=1}^{n}\eta_{j}^{i}f^{j} = \eta_{j}^{i}f^{j}
\end{aligned}
\]

对它们应用张量 \(\mathcal{C}\) 并利用其多重线性性质：

\[
\begin{aligned}
&\mathcal{C}(x_{1},\ldots,x_{p};\varphi^{1},\ldots,\varphi^{q}) \\
&= \mathcal{C}(\xi_{1}^{i_{1}}e_{i_{1}},\ldots,\xi_{p}^{i_{p}}e_{i_{p}};\eta_{j_{1}}^{1}f^{j_{1}},\ldots,\eta_{j_{q}}^{q}f^{j_{q}}) \\
&= \xi_{1}^{i_{1}}\xi_{2}^{i_{2}}\cdots\xi_{p}^{i_{p}}\eta_{j_{1}}^{1}\eta_{j_{2}}^{2}\cdots\eta_{j_{q}}^{q} \cdot \mathcal{C}(e_{i_{1}},e_{i_{2}},\ldots,e_{i_{p}};f^{j_{1}},f^{j_{2}},\ldots,f^{j_{q}}) \\
&= \xi_{1}^{i_{1}}\xi_{2}^{i_{2}}\cdots\xi_{p}^{i_{p}}\eta_{j_{1}}^{1}\eta_{j_{2}}^{2}\cdots\eta_{j_{q}}^{q} c_{i_{1}i_{2}\ldots i_{p}}^{j_{1}j_{2}\ldots j_{q}},
\end{aligned}
\]

其中最后一步使用了爱因斯坦求和约定。

**注记 3.1.** 由此可见，张量的分量在固定基对 \(\{e_{i}\}_{i=1}^{n}\) 和 \(\{f^{j}\}_{j=1}^{q}\) 下完全确定其形式。此性质与以下先前讨论的内容类似：

1. (a) 线性形式 \(\varphi\) 在对偶空间 \(V^{*}\) 基下的系数展开 \(\{\varphi_{i}\}\)；
2. (b) 双线性形式 \(b(x,y)\) 的矩阵表示 \(B\)，其中系数 \(\beta_{ij}\) 对应基向量 \(e_{i}\) 和 \(e_{j}\) 上的取值。

（注：证明通过基展开展示了张量分量的完备性，注记则通过类比强调了不同线性对象在坐标表示下的统一性。最终结果表明：张量的作用完全由其基向量的像决定，这是张量计算的核心特征。）  

# 张量理论

## §1. 基变换下的张量转换

在上一讲中，我们将张量定义为通过计算多重线性形式在基向量组上的值而得到的分量集合。同时我们记得，线性形式和双线性形式的坐标表示（分别为系数行和矩阵）在基变换时会按照特定规律进行转换。下面我们将重新回顾这些规律，并引入后续讨论所需的附加记号。

设 \( V(\mathbb{K}) \) 是维度为 \( n = \dim_{\mathbb{K}} V \) 的线性空间，\( V^* \) 为其对偶空间。在这两个空间中分别定义两套基——"旧基"和"新基"：

\[
\begin{aligned}
V &: \{e_i\}_{i=1}^n, \quad \{e_k'\}_{k=1}^n \\
V^* &: \{f^j\}_{j=1}^n, \quad \{f^{l}\}_{l=1}^n
\end{aligned}
\]

（注：此处建立了基变换讨论的框架，新旧基的标记为后续推导变换公式做好了准备。空间维度的明确声明保证了后续指标运算的维数一致性。）  

在这些成对的空间基之间，我们可以通过过渡矩阵 \( T = \{ \tau_k^i \} \) 及其逆矩阵 \( S = \{\sigma_j^i\} \) 来定义基变换关系：

\[
\begin{aligned}
e_k' &= e_j \tau_k^j \\
f'^l &= \sigma_j^l f^j
\end{aligned}
\]

这里我们直接应用了爱因斯坦求和约定来书写变换关系。

相应地，对于向量坐标 \( x = (\xi^1, \ldots, \xi^n) \) 和线性形式系数 \( f = (\eta_1, \ldots, \eta_n) \)，其变换规则为：

\[
\begin{aligned}
\xi'^k &= \sigma_i^k \xi^i \\
\eta'_l &= \eta_j \tau_l^j
\end{aligned}
\]

由此我们可以得出结论：在本课程采用的记号约定下，具有上标的对象通过逆过渡矩阵 \( S \) 变换，而具有下标的对象则通过原过渡矩阵 \( T \) 变换。

现在我们将这个结果推广到多重线性形式 \( A \in \Omega_q^p \) 的张量及其在基变换下的分量转换规律。根据上一讲的定义，我们在新基下引入张量：

$a_{k_1 k_2 \ldots k_p}^{l_1 l_2 \ldots l_q}=\mathcal{A}\left(e_{k_1}^{\prime}, e_{k_2}^{\prime}, \ldots, e_{k_p}^{\prime} ; f^{\prime l_1}, f^{\prime l_2}, \ldots, f^{\prime l_q}\right)=\mapsto$

（注：这里清晰地展示了张量分量在不同基下的转换规则，上标分量使用逆矩阵变换，下标分量使用原矩阵变换，这是张量分析中最重要的基本性质之一。）  

现在，我们利用已定义的基变换关系，将表达式通过"旧基"元素表示出来：

$\begin{gathered}\mapsto=\mathcal{A}\left(e_{i_1} \tau_{k_1}^{i_1}, e_{i_2} \tau_{k_2}^{i_2}, \ldots, e_{i_p} \tau_{k_p}^{i_p} ; \sigma_{j_1}^{l_1} f^{j_1}, \sigma_{j_2}^{l_2} f^{j_2}, \ldots, \sigma_{j_q}^{l_q} f^{j_q}\right)= \\ =\tau_{k_1}^{i_1} \tau_{k_2}^{i_2} \ldots \tau_{k_p}^{i_p} \sigma_{j_1}^{l_1} \sigma_{j_2}^{l_2} \ldots \sigma_{j_q}^{l_q} \mathcal{A}\left(e_{i_1}, e_{i_2}, \ldots, e_{i_p} ; f^{j_1}, f^{j_2}, \ldots, f^{j_q}\right)= \\ =\tau_{k_1}^{i_1} \tau_{k_2}^{i_2} \ldots \tau_{k_p}^{i_p} \sigma_{j_1}^{l_1} \sigma_{j_2}^{l_2} \ldots \sigma_{j_q}^{l_q} a_{i_1 i_2 \ldots i_p}^{j_1 j_2},\end{gathered}$

这里我们利用了映射_А_对每个参数都是线性的这一性质，以及每个参数中隐含的线性运算（爱因斯坦求和和过渡矩阵的标量乘法）。

由此我们证明了以下结论。

**定理 1.1.** 多重线性形式的张量在基变换下按以下规律转换：

$a_{k_1 k_2 \ldots k_p}^{\prime l_1 l_2 \ldots l_q}=\tau_{k_1}^{i_1} \tau_{k_2}^{i_2} \ldots \tau_{k_p}^{i_p} \sigma_{j_1}^{l_1} \sigma_{j_2}^{l_2} \ldots \sigma_{j_q}^{l_q} a_{i_1 i_2 \ldots i_p}^{j_1 j_2 \ldots j_q}$

**注记 1.1.** 在某些代数应用中，这个转换规律正是张量定义的基础。基于这个观点，我们可以将张量定义为一个多分量对象，其系数按照这个特定规律进行转换。

除了本讲开头已经提到的特例外，我们还可以将一般形式的张量转换与双线性形式在基变换下的转换联系起来。事实上，如先前所述，双线性形式对应形如β_{ij}的张量。根据上述转换规律，这个特例可以用指标形式表示为：

\[
\beta'_{kl} = \tau^i_k\tau^j_l \beta_{ij}
\]

在矩阵语言中，这直接对应于 \( B' = T^\top B T \) 的转换关系。

**注记 1.2.** 在前一讲中，该变换规律记为 \( B' = C^\top B C \)。为避免与当前讲义的记号混淆，我们已对过渡矩阵的符号进行了统一调整。

## §2. 缩并运算

现在我们将定义多重线性形式及其对应张量的另一种重要运算。

**定义 2.1.** 对于多重线性形式 \( A \in \Omega^p_q \)，其**缩并运算**是指如下映射：该运算产生一个关于 \( p-1 \) 个向量参数和 \( q-1 \) 个对偶向量参数的函数 \( B \)，定义为

$\begin{aligned} & \mathcal{B}\left(x_1, \ldots, x_{k-1}, x_{k+1}, \ldots, x_p ; \varphi^1, \ldots, \varphi^{l-1}, \varphi^{l+1}, \ldots, \varphi^q\right)= \\ = & \mathcal{A}\left(x_1, \ldots, x_{k-1}, \mathbf{e}_{\mathbf{r}}, x_{k+1}, \ldots, x_p ; \varphi^1, \ldots, \varphi^{l-1}, \mathbf{f}^{\mathbf{r}}, \varphi^{l+1}, \ldots, \varphi^q\right)\end{aligned}$

其中右侧表达式对哑指标 \( r \) 进行求和。

由于线性性质从 \( A \) 继承而来，所得函数 \( B \) 仍然是多重线性形式。

（注：缩并运算通过固定基 \(\{e_r\}\) 和对偶基 \(\{f^r\}\) 的求和，消去了一个向量参数和一个对偶向量参数。这种运算将 \((p,q)\) 型张量降为 \((p-1,q-1)\) 型张量，是张量分析中最重要的操作之一，在物理应用中广泛出现于指标缩并的情形。）  

让我们考察所得多重线性形式的分量表示，并在基 \(\{e_i\}_{i=1}^n\) 和对偶基 \(\{f^j\}_{j=1}^n\) 下建立对应记号：

\[
A \leftrightarrow a_{i_1...i_{k-1}i_ki_{k+1}...i_p}^{j_1...j_{l-1}j_lj_{l+1}...j_q}
\]

\[
B \leftrightarrow b_{i_1...i_{k-1}i_{k+1}...i_p}^{j_1...j_{l-1}j_{l+1}...j_q}
\]

这两个多重线性形式的分量之间满足如下关系：

\[
b_{i_1...i_{k-1}i_{k+1}...i_p}^{j_1...j_{l-1}j_{l+1}...j_q} =  a_{i_1...i_{k-1}ri_{k+1}...i_p}^{j_1...j_{l-1}rj_{l+1}...j_q}
\]

这个关系式是通过将基向量代入缩并运算的定义，并根据多重线性形式张量的定义推导得出的。具体来说：
1. 在位置 \(i_k\) 处插入基向量 \(e_r\)
2. 在位置 \(j_l\) 处插入对偶基向量 \(f^r\)
3. 对重复指标 \(r\) 执行爱因斯坦求和约定

**注记 2.1.** 多重线性形式进行缩并运算的必要条件是：至少包含一个向量参数和一个对偶向量参数。在张量运算中，则要求至少存在一个上标和一个下标。

**例 2.1.** 通过缩并运算可以表示线性形式 \( f \) 作用于向量 \( x \)：
\[
f(x) = \eta_1 x^1 + \cdots + \eta_n x^n
\]

同样地，利用张量记法（包括缩并运算）可将线性方程组表示为指标形式：
\[
Ax = b \quad \Leftrightarrow \quad \alpha_i^j \xi^i = \beta^j,
\]
其中：
- \( \alpha_i^j \) 对应矩阵 \( A \) 的分量
- \( \xi^i \) 和 \( \beta^j \) 分别表示向量 \( x \) 和 \( b \) 的坐标分量

**注记 2.2.** 所有先前的矩阵运算均可转化为对应张量对象的指标表示。

### §3. 张量的应用

我们此前已引入克罗内克符号来描述对偶基之间的关系，但它也可以作为张量对象来定义。

**定义 3.1.** 克罗内克符号 \(\delta_{ij}\) 是一个 (2,0) 型的二重协变张量，其分量定义为：

\[
\delta_{ij} = 
\begin{cases} 
1, & i = j, \\ 
0, & i \neq j.
\end{cases}
\]

**注记 3.1.** 克罗内克符号具有对称性，即满足：

\[
\delta_{ij} = \delta_{ji}
\]

**3.1. 克罗内克符号与内积**

考虑在笛卡尔直角坐标系(DПСК)下该张量在几何问题中的应用。

**注记 3.2.** 在笛卡尔直角坐标系中成立以下性质：

\[
\delta_{ij} a^{j} = a_{i},
\]

该运算称为指标的升降。这个性质不仅适用于笛卡尔坐标系，在后续课程中我们将推广到任意坐标系。

基于此性质，克罗内克符号可用于表示笛卡尔直角坐标系中的内积：

\[
\mathbf{a} \cdot \mathbf{b} = a^{i}b^{j}g_{ij} = a^{i}b_{i} = \sum_{i=1}^{n} a^{i}b_{i}.
\]

### 3.2. 列维-奇维塔符号

**定义 3.2.** 列维-奇维塔符号 \(\varepsilon_{ijk}\) 是一个 (3,0) 型的三重协变张量，其在笛卡尔直角坐标系(DПСК)中的分量定义为：

\[
\varepsilon_{ijk} = 
\begin{cases}
+1, & \text{若}(i,j,k)\text{为}(1,2,3)\text{的偶排列}, \\
-1, & \text{若}(i,j,k)\text{为奇排列}, \\
0, & \text{其他情况（存在重复指标）}.
\end{cases}
\]

**注记 3.3.** 列维-奇维塔符号具有以下性质：

\[
\varepsilon_{ijk} = -\varepsilon_{jik} = -\varepsilon_{ikj},
\]

称为张量的反对称性，该性质直接由其定义得出。

在几何应用中，向量积 \(\mathbf{c} = \mathbf{a} \times \mathbf{b}\) 的分量可通过列维-奇维塔符号表示为：

\[
c_i = (\mathbf{a} \times \mathbf{b})_i = \varepsilon_{ijk}a^jb^k.
\]

展开为分量形式：

\[
\mathbf{c} = (\varepsilon_{1jk}a^jb^k, \varepsilon_{2jk}a^jb^k, \varepsilon_{3jk}a^jb^k).
\]

在坐标形式下，向量积表示为：
\[
\mathbf{c} = (\varepsilon_{1jk}a^jb^k, \varepsilon_{2jk}a^jb^k, \varepsilon_{3jk}a^jb^k)
\]

实际上，在笛卡尔直角坐标系中，向量积的完整表达式可写作：
\[
\mathbf{a} \times \mathbf{b} = (a^2b^3 - a^3b^2) \mathbf{i} + (a^3b^1 - a^1b^3) \mathbf{j} + (a^1b^2 - a^2b^1) \mathbf{k}
\]

根据"向量代数"专题的定义，需特别注意：
1. 当向量 **a** 和 **b** 的坐标指标不一致时，它们的乘积不会出现在向量 **c** 的分量计算公式中；
2. 当交换向量坐标指标时，乘积结果的符号会发生反转。

这些特性与列维-奇维塔符号的定义和性质完全吻合：
- 符号的反对称性（\(\varepsilon_{ijk} = -\varepsilon_{jik}\)）对应指标交换时的符号反转
- 非重复指标组合才产生非零项的特性对应不同指标向量的乘积关系

既然标量积和向量积都可以用张量来描述，那么很自然地可以推测混合积也可以用这种方式表示。

三个向量 \( a, b, c \) 在 \( \mathbb{R}^3 \) 中的混合积：

\[
(a, b, c) = a \cdot (b \times c) = (a^i) \cdot (\epsilon_{ijk} b^j c^k) = \epsilon_{ijk} a^i b^j c^k.
\]

最后，我们来看列维-奇维塔符号在非几何问题中的另一个推广。回忆在笛卡尔直角坐标系中，混合积可以通过行列式计算：

\[
(a, b, c) = \det \begin{pmatrix}
a^1 & a^2 & a^3 \\
b^1 & b^2 & b^3 \\
c^1 & c^2 & c^3
\end{pmatrix},
\]

由此可以推测，任意三个向量组成的行列式也可以通过矩阵列向量与列维-奇维塔符号的缩并运算来求得。  

### 3.3. 任意矩阵的行列式

我们将列维-奇维塔符号的定义推广到任意数量指标的情况。

**定义 3.3.** 在n维空间中的列维-奇维塔符号 \(\varepsilon_{i_1 i_2 \ldots i_n}\) 是一个具有n个指标的完全反对称(0,n)型张量。其在任何笛卡尔坐标系中的分量定义如下：

\[
\varepsilon_{i_1 i_2 \ldots i_n} =
\begin{cases} 
+1, & \text{若}(i_1, i_2, \ldots, i_n)\text{是}(1, 2, \ldots, n)\text{的偶排列}, \\
-1, & \text{若}(i_1, i_2, \ldots, i_n)\text{是奇排列}, \\
0, & \text{其他情况（存在重复指标）}.
\end{cases}
\]

**说明：**

- **反对称性**：交换任意两个指标会改变符号：
\[
\varepsilon_{..,i\ldots,j\ldots} = -\varepsilon_{..,j\ldots,i\ldots}
\]

- **非零分量**：只有当所有指标互不相同且构成(1,2,...,n)的排列时，分量才不为零。

- **排列的奇偶性**：排列的奇偶性由恢复原始顺序(1,2,...,n)所需的交换次数决定。

根据爱因斯坦求和约定，这里对所有指标 \( i_1, i_2, \ldots, i_n \) 进行求和，而列维-奇维塔符号的取值仅为 +1 或 -1。这引导我们得到n阶矩阵行列式的定义：

\[
\det A = \sum_{\sigma(1, \ldots, n)} (-1)^{|\sigma|} a_1^{i_1} a_2^{i_2} \ldots a_n^{i_n}
\]

其中 \(\sigma\) 表示指标重排的变换。

**注记 3.4.** 矩阵行列式最自然地来源于对张量（特别是反对称张量）的考察。

# 线性映射

前几章我们研究了具有线性性质的映射，其结果为某个域中的标量。然而，还存在另一类重要的映射类型，它定义了两个线性空间元素之间的对应关系。正如我们后续将看到的，线性形式实际上是这类映射的一个特例。

## §1. 基本概念

设 \( V(\mathbb{K}) \) 和 \( W(\mathbb{K}) \) 是域 \(\mathbb{K}\) 上的线性空间。

**定义 1.1.** 映射 \(\varphi : V \to W\) 称为线性的，如果对于所有 \( x_1, x_2 \in V \) 和所有 \(\alpha \in \mathbb{K}\) 满足以下性质：

\[
\varphi(x_1 + x_2) = \varphi(x_1) + \varphi(x_2), \quad \varphi(\alpha x) = \alpha \varphi(x)
\]

**注记 1.1.** 从 \(V(\mathbb{K})\) 到 \(W(\mathbb{K})\) 的所有线性映射的集合记作 \(\text{Hom}_\mathbb{K}(V, W)\)。
**例 1.1.** 线性映射的示例：

(a) 零映射：
\[
O: V \to W \quad O(x) = 0_W, \quad \forall x \in V
\]

(б) 恒等映射：
\[
\mathcal{I}: V \to V \quad \mathcal{I}(x) = x, \quad \forall x \in V
\]

(b) 伸缩变换：
\[
\varphi: V \to V \quad \varphi(x) = \lambda x, \quad \forall x \in V
\]

(r) 设 \(V\) 可分解为子空间的直和 \(V = V_1 \oplus V_2\)，则投影映射定义为：
\[
\mathcal{P}_{V_1}^{||V_2}: V \to V, \quad \mathcal{P}_{V_1}^{||V_2}(x) = x_1, \quad \forall x = x_1 + x_2 \in V, x_1 \in V_1, x_2 \in V_2
\]

(r) 设 \( V \) 可分解为子空间的直和 \( V = V_1 \oplus V_2 \)，则投影映射定义为：
\[
P_{V_1}^{W_2} : V \rightarrow V, \quad P_{V_1}^{W_2} x = x_1, \quad \forall x = x_1 + x_2 \in V, x_1 \in V_1, x_2 \in V_2
\]

(л) 设 \( \mathbb{R}^{\leq n}[t] \) 为次数不超过 \( n \) 的多项式空间，用 \( D \) 表示微分算子：
\[
Dp = \frac{dp}{dt}, \quad \forall p \in \mathbb{R}^{\leq n}[t]
\]

(e) 设 \( M_n(\mathbb{K}) \) 为 \( n \) 阶方阵空间，定义对称化 Sym 和反对称化 Asym 映射：
\[
Sym(A) = \frac{1}{2} (A + A^T)
\]
\[
Asym(A) = \frac{1}{2} (A - A^T)
\]

**注记 1.2.** 在表示线性映射及其参数时，常如上述某些例子中那样省略括号。换言之，记法 ϕ(x) 和 ϕx 被视为等价。

**§2. 映射的矩阵表示**

设 ϕ : V → W 为线性映射，其中 dimₖV = n，dimₖW = m，且 {eᵢ}ᵢ₌₁ⁿ 和 {gⱼ}ⱼ₌₁ᵐ 分别是空间 V 和 W 的基。

**定义 2.1.** 线性映射 ϕ 在基对 {eᵢ}ᵢ₌₁ⁿ 和 {gⱼ}ⱼ₌₁ᵐ 下的矩阵 Aϕ = {αⱼⁱ} 是指满足以下条件的矩阵：其各列由基向量 {eᵢ} 的像在基 {gⱼ} 下的坐标组成

\[
\phi e_i = \sum_{j=1}^m \alpha_j^i g_j
\]

**例 2.1.**  
(a) **零映射**的矩阵表示：
\[
O \rightarrow \Theta = 
\begin{pmatrix}
0 & 0 & \cdots & 0 \\
0 & 0 & \cdots & 0 \\
\vdots & \vdots & \ddots & \vdots \\
0 & 0 & \cdots & 0
\end{pmatrix}
\]

(б) **恒等映射**的矩阵表示：
\[
\mathcal{I} \rightarrow E =
\begin{pmatrix}
1 & 0 & \cdots & 0 \\
0 & 1 & \cdots & 0 \\
\vdots & \vdots & \ddots & \vdots \\
0 & 0 & \cdots & 1
\end{pmatrix}
\]

(b) **投影映射**的矩阵表示（当 \( V = V_1 \oplus V_2 \) 时，在适配子空间的基下）：
\[
\mathcal{P}_{V_1}^{|V_2} \rightarrow P_1 = 
\begin{pmatrix}
E & 0 \\
0 & \Theta
\end{pmatrix}
\]
其性质为：
\[
\mathcal{P}_{V_1}^{|V_2}x = x \ (\forall x \in V_1), \quad \mathcal{P}_{V_1}^{|V_2}x = 0 \ (\forall x \in V_2)
\]

**定理 2.1.** 给定线性映射 \(\varphi\) 等价于在固定基对下给定其矩阵表示 \(A_\varphi\)。

**证明.** 设 \(\varphi \in \text{Hom}_K(V, W)\) 为线性映射，\(\{e_i\}_{i=1}^n\) 和 \(\{g_j\}_{j=1}^m\) 分别为空间 \(V\) 和 \(W\) 的基。考虑元素 \(x \in V\) 和 \(y \in W\) 满足：
\[
x = \sum_{i=1}^n \xi^i e_i, \quad y = \sum_{j=1}^m \eta^j g_j, \quad \varphi(x) = y
\]

映射对元素 \(x\) 的作用可表示为：
\[
\varphi(x) = \varphi \left( \sum_{i=1}^n \xi^i e_i \right) = \sum_{i=1}^n \xi^i \varphi(e_i) = \sum_{i=1}^n \xi^i \sum_{j=1}^m \alpha_i^j g_j = \sum_{j=1}^m \eta^j g_j
\]

由此可得坐标变换关系：
\[
\eta^j = \sum_{i=1}^n \xi^i \alpha_i^j
\]

这表明仅需矩阵系数即可唯一确定元素的像，前提是向量和矩阵都在同一组基对下定义。□

## §3. 线性映射空间

考虑两个线性空间 \( V(\mathbb{K}) \) 和 \( W(\mathbb{K}) \)，以及它们之间的所有线性映射构成的集合。设 \(\varphi, \psi\) 为从 \(V\) 到 \(W\) 的线性映射。

**定义 3.1.** 线性映射 \(\varphi\) 和 \(\psi\) 称为相等，若满足：
\[
\forall x \in V \quad \varphi(x) = \psi(x)
\]

**定义 3.2.** 映射 \(\chi : V \to W\) 称为线性映射 \(\varphi, \psi : V \to W\) 的和，若满足：
\[
\forall x \in V \quad \chi(x) = \varphi(x) + \psi(x)
\]

**引理 3.1.** 线性映射的和 \(\chi = \varphi + \psi\) 仍是线性映射。

**证明.** 需验证线性映射和运算保持线性性质：

1. 加法保持性：
\[
\chi(x_1 + x_2) = \varphi(x_1 + x_2) + \psi(x_1 + x_2) = \varphi(x_1) + \varphi(x_2) + \psi(x_1) + \psi(x_2) = (\varphi + \psi)(x_1) + (\varphi + \psi)(x_2) = \chi(x_1) + \chi(x_2)
\]

2. 数乘保持性：
\[
\chi(\alpha x) = \varphi(\alpha x) + \psi(\alpha x) = \alpha\varphi(x) + \alpha\psi(x) = \alpha(\varphi + \psi)(x) = \alpha\chi(x)
\]

**推论 3.0.1.** 线性映射 \(\chi = \varphi + \psi\) 的矩阵 \( C_{\chi} \) 由对应矩阵 \( A_\varphi \) 与 \( B_\psi \) 的和给出：
\[
C_{\chi} = A_\varphi + B_\psi
\]

**定义 3.3.** 映射 \(\omega\) 称为线性映射 \(\varphi\) 与数 \(\lambda \in \mathbb{K}\) 的积，若满足：
\[
\forall x \in V \quad \omega(x) = \lambda \varphi(x)
\]

**引理 3.2.** 线性映射的数乘 \(\omega = \lambda \varphi\) 仍是线性映射。

**证明.** 证明过程与和运算的情形类似（通过验证加法和数乘的线性性质即可得证）。

**推论 3.0.2.** 线性映射 \(\omega = \lambda\varphi\) 的矩阵 \( D_\omega \) 由矩阵 \( A_\varphi \) 与标量 \(\lambda \in \mathbb{K}\) 的数乘给出：
\[
D_\omega = \lambda A_\varphi
\]

基于已定义的映射相等性、映射运算规则以及零元的存在性，我们可以在线性映射集合上建立线性空间结构。

**定理 3.1.** 从空间 \( V \) 到空间 \( W \) 的所有线性映射集合构成域 \( \mathbb{K} \) 上的线性空间。

**证明.** 该证明转化为验证线性空间公理的过程。

**注记 3.1.** 由于线性映射与其在固定基对下的矩阵表示之间存在保持线性性质的对应关系，可以断言空间 \(\text{Hom}_K(V, W)\) 与矩阵空间 \( M_{m \times n}(\mathbb{K}) \) 同构：

\[
\text{Hom}_K(V, W) \simeq M_{m \times n}(\mathbb{K})
\]

**线性映射的复合**

设 \( \varphi \in \text{Hom}_K(V, U) \) 和 \( \psi \in \text{Hom}_K(U, W) \) 为相应空间之间的线性映射。

**定义 3.4.** 映射 \( \chi : V \to W \) 称为线性映射 \( \psi \) 与 \( \varphi \) 的复合，若满足：

\[
\forall x \in V : \quad \chi(x) = (\psi \circ \varphi)(x) = \psi(\varphi(x))
\]

**引理 3.3.** 线性映射的复合 \( \chi = \psi \circ \varphi \) 仍是线性映射。

**证明.** 考虑 \( V \) 中向量线性组合的像：

$\chi\left(\sum_{i=1}^k \alpha^i x_i\right)=(\psi \circ \varphi)\left(\sum_{i=1}^k \alpha^i x_i\right)=\psi\left(\sum_{i=1}^k \alpha^i \varphi\left(x_i\right)\right)=\sum_{i=1}^k \alpha^i \psi\left(\varphi\left(x_i\right)\right)=\sum_{i=1}^k \alpha^i \chi\left(x_i\right)$

**推论 3.1.1.** 复合映射 \(\chi = \psi \circ \varphi\) 的矩阵等于对应矩阵的乘积：
\[
C_\chi = B_\psi \cdot A_\varphi
\]

## §4. 基变换

设 ϕ ∈ Homₖ(V, W)，且在空间 V 和 W 中分别给定两组基：

V 的基：{eᵢ}ᵢ₌₁ⁿ 和 {eⱼ'}ⱼ₌₁ⁿ  
W 的基：{gₖ}ₖ₌₁ⁿ 和 {gₗ'}ₗ₌₁ⁿ  

已知：
- T = {τⱼⁱ} 是从基 {e} 到基 {e'} 的过渡矩阵
- S = {σₗᵏ} 是从基 {g} 到基 {g'} 的过渡矩阵

**定理 4.1.** 算子矩阵在基变换下的转换关系为：
\[
A_\phi' = S^{-1}A_\phi T
\]

**证明.** 设 \( x \in V \) 是空间 \( V \) 的任意元素，\( y \) 为其像。则在基对 \(\{e\}\) 和 \(\{g\}\) 下有：
\[
\phi(x) = y \Leftrightarrow A_\phi x = y
\]

同时在基对 \(\{e'\}\) 和 \(\{g'\}\) 下成立：
\[
\phi(x) = y \Leftrightarrow A_\phi' x' = y'
\]

已知基变换时向量坐标的转换关系：
\[
x' = T^{-1}x, \quad y' = S^{-1}y
\]

将坐标变换代入矩阵表达式得：
\[
A_\phi' T^{-1}x = S^{-1}y
\]

由于过渡矩阵总是可逆的，因此可得：
\[
S A_\phi' T^{-1} = A_\phi
\]
等价表示为：
\[
A_\phi' = S^{-1} A_\phi T
\]

