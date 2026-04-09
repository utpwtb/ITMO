import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from statsmodels.distributions.empirical_distribution import ECDF
import scipy.stats as stats

df = pd.read_csv('RGR1_A-5_X1-X4.csv')

cols = ['X1', 'X2', 'X3']
n = len(df)

# 计算各项数值特征
stats_dict = {}
for col in cols:
    x = df[col]
    mean_val = x.mean()
    var_biased = x.var(ddof=0)  # S^2 (有偏)
    var_unbiased = x.var(ddof=1)  # sigma^2 (无偏)
    std_biased = x.std(ddof=0)  # S
    std_unbiased = x.std(ddof=1)  # sigma
    median_val = x.median()
    q1 = x.quantile(0.25)
    q3 = x.quantile(0.75)

    stats_dict[col] = {
        'Mean': mean_val, 'S^2': var_biased, 'sigma^2_hat': var_unbiased,
        'S': std_biased, 'sigma_hat': std_unbiased, 'Median': median_val,
        'Q1': q1, 'Q3': q3, 'Min': x.min(), 'Max': x.max()
    }

stats_df = pd.DataFrame(stats_dict)
print("--- 数值特征 ---")
print(stats_df)

# 可视化：直方图与经验分布函数 (EDF)
fig, axes = plt.subplots(3, 2, figsize=(12, 12))

for i, col in enumerate(cols):
    x = df[col].sort_values()  # 变分级数

    # 规则计算
    iqr = stats_dict[col]['Q3'] - stats_dict[col]['Q1']
    h_fd = 2 * iqr * (n ** (-1 / 3))
    bins_fd = int((x.max() - x.min()) / h_fd) if h_fd > 0 else 'auto'

    # 直方图 (使用 Freedman-Diaconis 规则)
    sns.histplot(x, bins=bins_fd, kde=False, ax=axes[i, 0], stat='density', color='skyblue')
    axes[i, 0].set_title(f'{col} - Histogram (FD Rule)')

    # 经验分布函数 EDF
    ecdf = ECDF(x)
    axes[i, 1].step(ecdf.x, ecdf.y, where='post', color='red')
    axes[i, 1].set_title(f'{col} - Empirical Distribution Function')
    axes[i, 1].grid(True)

plt.tight_layout()
plt.show()

# 参数估计计算
params_est = {}

# X3: 正态分布
x3 = df['X3']
mean_x3, s2_x3 = stats_df.loc['Mean', 'X3'], stats_df.loc['S^2', 'X3']
params_est['X3_Normal'] = {
    'MoM': {'a': mean_x3, 'sigma^2': s2_x3},
    'MLE': {'a': mean_x3, 'sigma^2': s2_x3}
}

# X2: 均匀分布
x2 = df['X2']
mean_x2, s2_x2 = stats_df.loc['Mean', 'X2'], stats_df.loc['S^2', 'X2']
params_est['X2_Uniform'] = {
    'MoM': {'a': mean_x2 - np.sqrt(3 * s2_x2), 'b': mean_x2 + np.sqrt(3 * s2_x2)},
    'MLE': {'a': x2.min(), 'b': x2.max()}
}

# X1: 偏移指数分布
x1 = df['X1']
mean_x1, s_x1 = stats_df.loc['Mean', 'X1'], stats_df.loc['S', 'X1']
lambda_mom = 1 / s_x1
c_mom = mean_x1 - 1 / lambda_mom
c_mle = x1.min()
lambda_mle = 1 / (mean_x1 - c_mle)
params_est['X1_Exponential'] = {
    'MoM': {'lambda': lambda_mom, 'c': c_mom},
    'MLE': {'lambda': lambda_mle, 'c': c_mle}
}

for k, v in params_est.items():
    print(f"--- {k} ---")
    print(f"MoM: {v['MoM']}")
    print(f"MLE: {v['MLE']}")

print("\n--- 4.4 概率估计 P(X > x0) ---")
for col in cols:
    x = df[col]
    x0 = stats_df.loc['Mean', col] + stats_df.loc['sigma_hat', col]

    # 经验概率
    p_emp = (x > x0).mean()

    # 参数概率 (使用 MLE 参数)
    if col == 'X3':  # Normal
        a, std = params_est['X3_Normal']['MLE']['a'], np.sqrt(params_est['X3_Normal']['MLE']['sigma^2'])
        p_param = 1 - stats.norm.cdf(x0, loc=a, scale=std)
    elif col == 'X2':  # Uniform
        a, b = params_est['X2_Uniform']['MLE']['a'], params_est['X2_Uniform']['MLE']['b']
        p_param = (b - x0) / (b - a) if a <= x0 <= b else (0 if x0 > b else 1)
    elif col == 'X1':  # Exponential
        lam, c = params_est['X1_Exponential']['MLE']['lambda'], params_est['X1_Exponential']['MLE']['c']
        p_param = np.exp(-lam * (x0 - c)) if x0 >= c else 1

    print(f"{col} (x0={x0:.2f}): 经验值 = {p_emp:.4f}, 参数值 = {p_param:.4f}")

print("\n--- 4.5 分组样本矩估计 ---")
# 以 X3 为例演示分组计算
hist, bin_edges = np.histogram(df['X3'], bins='auto')
bin_mids = (bin_edges[:-1] + bin_edges[1:]) / 2
n_total = len(df['X3'])

ex_grouped = np.sum(hist * bin_mids) / n_total
dx_grouped = np.sum(hist * (bin_mids - ex_grouped) ** 2) / (n_total - 1)

print(f"X3 原始 EX = {stats_df.loc['Mean', 'X3']:.4f}, 分组 EX = {ex_grouped:.4f}")
print(f"X3 原始 DX (无偏) = {stats_df.loc['sigma^2_hat', 'X3']:.4f}, 分组 DX = {dx_grouped:.4f}")

print("\n--- 4.6 置信区间 (1-alpha = 0.95) ---")
alpha = 0.05
z_val = stats.norm.ppf(1 - alpha / 2)
t_val = stats.t.ppf(1 - alpha / 2, df=n - 1)
chi2_lower = stats.chi2.ppf(alpha / 2, df=n - 1)
chi2_upper = stats.chi2.ppf(1 - alpha / 2, df=n - 1)

# 1. 渐近置信区间
for col in cols:
    mean_val = stats_df.loc['Mean', col]
    se = stats_df.loc['sigma_hat', col] / np.sqrt(n)
    margin = z_val * se
    print(f"{col} EX 渐近置信区间: ({mean_val - margin:.2f}, {mean_val + margin:.2f})")

# 2. X3 (正态分布) 的精确置信区间
mean_x3 = stats_df.loc['Mean', 'X3']
sigma_hat_x3 = stats_df.loc['sigma_hat', 'X3']
sigma2_hat_x3 = stats_df.loc['sigma^2_hat', 'X3']

ci_a_exact = (mean_x3 - t_val * sigma_hat_x3 / np.sqrt(n),
              mean_x3 + t_val * sigma_hat_x3 / np.sqrt(n))

ci_var_exact = ((n - 1) * sigma2_hat_x3 / chi2_upper,
                (n - 1) * sigma2_hat_x3 / chi2_lower)

print(f"\nX3 精确置信区间 (期望 a): ({ci_a_exact[0]:.2f}, {ci_a_exact[1]:.2f})")
print(f"X3 精确置信区间 (方差 sigma^2): ({ci_var_exact[0]:.2f}, {ci_var_exact[1]:.2f})")
