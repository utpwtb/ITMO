import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from statsmodels.distributions.empirical_distribution import ECDF
import scipy.stats as stats
from sklearn.cluster import KMeans

sns.set_theme(style="whitegrid")

# 读取数据
df = pd.read_csv('RGR1_A-5_X1-X4.csv')
cols = ['X1', 'X2', 'X3']
n = len(df)
print(f"Объём выборки n = {n}")

# 计算基本统计量
stats_dict = {}
for col in cols:
    x = df[col]
    stats_dict[col] = {
        'Среднее': x.mean(),
        'Смещ. дисперсия': x.var(ddof=0),
        'Несмещ. дисперсия': x.var(ddof=1),
        'Смещ. откл.': x.std(ddof=0),
        'Несмещ. откл.': x.std(ddof=1),
        'Медиана': x.median(),
        'Q1 (25%)': x.quantile(0.25),
        'Q3 (75%)': x.quantile(0.75)
    }

stats_df = pd.DataFrame(stats_dict).round(2)
print("\nОсновные числовые характеристики:")
print(stats_df)

# 图1: 三列数据的变分序列放在一起
fig1, axes1 = plt.subplots(1, 3, figsize=(18, 5))

for i, col in enumerate(cols):
    x = df[col].sort_values()
    n_points = len(x)
    axes1[i].scatter(range(1, n_points + 1), x, s=10, alpha=0.6, color='darkorange')
    axes1[i].set_title(f'{col}')
    axes1[i].set_xlabel('Порядковый номер')
    axes1[i].set_ylabel('Значение')
    axes1[i].grid(True, alpha=0.3)

plt.tight_layout()
plt.show()

# 图2: 三列数据的ЭФР放在一起
fig2, axes2 = plt.subplots(1, 3, figsize=(18, 5))

for i, col in enumerate(cols):
    x = df[col].sort_values()
    ecdf = ECDF(x)
    axes2[i].step(ecdf.x, ecdf.y, where='post', color='purple', linewidth=2)
    axes2[i].set_title(f'{col}')
    axes2[i].set_xlabel('Значение')
    axes2[i].set_ylabel('F(x)')
    axes2[i].grid(True, alpha=0.3)

plt.tight_layout()
plt.show()

# 计算每个规则的箱数
bins_data = {}
for col in cols:
    x = df[col]
    S = stats_df.loc['Смещ. откл.', col]
    IQR = stats_df.loc['Q3 (75%)', col] - stats_df.loc['Q1 (25%)', col]

    h_scott = 3.5 * S * (n ** (-1 / 3))
    bins_scott = max(1, int(np.ceil((x.max() - x.min()) / h_scott)))

    h_fd = 2 * IQR * (n ** (-1 / 3))
    bins_fd = max(1, int(np.ceil((x.max() - x.min()) / h_fd)))

    bins_sturges = 1 + int(np.floor(np.log2(n)))

    bins_data[col] = {
        'scott': bins_scott,
        'fd': bins_fd,
        'sturges': bins_sturges
    }

# 为每个方法定义统一的颜色（跨列一致）
method_colors = {
    'scott': 'skyblue',  # Scott规则统一用蓝色
    'fd': 'lightgreen',  # Freedman-Diaconis规则统一用绿色
    'sturges': 'salmon'  # Sturges规则统一用橙红色
}

method_names = {
    'scott': 'Скотта',
    'fd': 'Фридмана-Диакониса',
    'sturges': 'Стерджеса'
}

# 为每一列数据生成一张图，包含三种规则的直方图
for col in cols:
    fig, axes = plt.subplots(1, 3, figsize=(18, 5))

    x = df[col]

    # 1. Scott规则
    bins_scott = bins_data[col]['scott']
    sns.histplot(x, bins=bins_scott, kde=False, ax=axes[0],
                 color=method_colors['scott'], edgecolor='black', alpha=0.7)
    axes[0].set_title(f'Правило {method_names["scott"]} (bins={bins_scott})')
    axes[0].set_xlabel('Значение')
    axes[0].set_ylabel('Частота')
    axes[0].grid(True, alpha=0.3)

    # 2. Freedman-Diaconis规则
    bins_fd = bins_data[col]['fd']
    sns.histplot(x, bins=bins_fd, kde=False, ax=axes[1],
                 color=method_colors['fd'], edgecolor='black', alpha=0.7)
    axes[1].set_title(f'Правило {method_names["fd"]} (bins={bins_fd})')
    axes[1].set_xlabel('Значение')
    axes[1].set_ylabel('Частота')
    axes[1].grid(True, alpha=0.3)

    # 3. Sturges规则
    bins_sturges = bins_data[col]['sturges']
    sns.histplot(x, bins=bins_sturges, kde=False, ax=axes[2],
                 color=method_colors['sturges'], edgecolor='black', alpha=0.7)
    axes[2].set_title(f'Правило {method_names["sturges"]} (bins={bins_sturges})')
    axes[2].set_xlabel('Значение')
    axes[2].set_ylabel('Частота')
    axes[2].grid(True, alpha=0.3)

    plt.tight_layout()
    plt.show()

# 参数估计
params = {}

# 1. X1: 带位移的指数分布
mean_x1, s_x1 = df['X1'].mean(), df['X1'].std(ddof=0)
c_mle = df['X1'].min()
params['1. X1 (Экспоненциальное)'] = {
    'Метод': ['ММ', 'ММП'],
    'lambda': [1 / s_x1, 1 / (mean_x1 - c_mle)],
    'c': [mean_x1 - s_x1, c_mle]
}

# 2. X2: 均匀分布
mean_x2, s2_x2 = df['X2'].mean(), df['X2'].var(ddof=0)
params['2. X2 (Равномерное)'] = {
    'Метод': ['ММ', 'ММП'],
    'a': [mean_x2 - np.sqrt(3 * s2_x2), df['X2'].min()],
    'b': [mean_x2 + np.sqrt(3 * s2_x2), df['X2'].max()]
}

# 3. X3: 正态分布
mean_x3, s2_x3 = df['X3'].mean(), df['X3'].var(ddof=0)
params['3. X3 (Нормальное)'] = {
    'Метод': ['ММ', 'ММП'],
    'mu': [mean_x3, mean_x3],
    'sigma2': [s2_x3, s2_x3]
}

print("\n=== Оценки параметров ===")
for dist_name, dist_params in params.items():
    print(f"\n{dist_name}")
    for key, values in dist_params.items():
        if key != 'Метод':
            print(f"  {key}: ММ = {values[0]:.4f}, ММП = {values[1]:.4f}")

# 参数化概率估计
print("\n=== Вероятность P(X > x0) ===")
data = []
for col in cols:
    x = df[col]
    mean_val = x.mean()
    std_val = x.std(ddof=1)
    x0 = mean_val + std_val

    # 经验概率
    p_emp = (x > x0).mean()

    # 参数化概率 (MLE)
    if col == 'X3':
        mu = params['3. X3 (Нормальное)']['mu'][1]
        var = params['3. X3 (Нормальное)']['sigma2'][1]
        p_param = 1 - stats.norm.cdf(x0, loc=mu, scale=np.sqrt(var))
    elif col == 'X2':
        a = params['2. X2 (Равномерное)']['a'][1]
        b = params['2. X2 (Равномерное)']['b'][1]
        if a <= x0 <= b:
            p_param = (b - x0) / (b - a)
        else:
            p_param = 0 if x0 > b else 1
    elif col == 'X1':
        lam = params['1. X1 (Экспоненциальное)']['lambda'][1]
        c = params['1. X1 (Экспоненциальное)']['c'][1]
        p_param = np.exp(-lam * (x0 - c)) if x0 >= c else 1

    data.append({
        'Переменная': col,
        'x0': x0,
        'P_эмп': p_emp,
        'P_парам': p_param,
        '|Δ|': abs(p_emp - p_param)
    })

df_prob = pd.DataFrame(data).round(4)
print(df_prob)

# 分组样本的矩估计
print("\n=== Оценки по группированным данным ===")
grouped_results = []
for col in cols:
    x = df[col]
    n = len(x)

    S = x.std(ddof=0)
    IQR = x.quantile(0.75) - x.quantile(0.25)
    h_fd = 2 * IQR * (n ** (-1 / 3))
    bins_fd = max(1, int(np.ceil((x.max() - x.min()) / h_fd)))

    hist, bin_edges = np.histogram(x, bins=bins_fd)
    bin_mids = (bin_edges[:-1] + bin_edges[1:]) / 2

    ex_grouped = np.sum(hist * bin_mids) / n
    dx_grouped = np.sum(hist * (bin_mids - ex_grouped) ** 2) / (n - 1)

    ex_original = x.mean()
    dx_original = x.var(ddof=1)

    grouped_results.append({
        'Переменная': col,
        'Кол-во интервалов': bins_fd,
        'EX (групп.)': ex_grouped,
        'EX (исходн.)': ex_original,
        '|Δ EX|': abs(ex_grouped - ex_original),
        'DX (групп.)': dx_grouped,
        'DX (исходн.)': dx_original,
        '|Δ DX|': abs(dx_grouped - dx_original)
    })

df_grouped = pd.DataFrame(grouped_results).round(4)
print(df_grouped)

# 置信区间
print("\n=== Доверительные интервалы (95%) ===")
alpha = 0.05
z_val = stats.norm.ppf(1 - alpha / 2)
t_val = stats.t.ppf(1 - alpha / 2, df=n - 1)
chi2_lower = stats.chi2.ppf(alpha / 2, df=n - 1)
chi2_upper = stats.chi2.ppf(1 - alpha / 2, df=n - 1)

print("--- Асимптотические ДИ для EX ---")
for col in cols:
    mean_val = df[col].mean()
    se = df[col].std(ddof=1) / np.sqrt(n)
    margin = z_val * se
    print(f"{col}: ({mean_val - margin:.2f}, {mean_val + margin:.2f})")

print("\n--- Точные ДИ для X3 ---")
mean_x3 = df['X3'].mean()
std_hat_x3 = df['X3'].std(ddof=1)
var_hat_x3 = df['X3'].var(ddof=1)

ci_mean = (mean_x3 - t_val * std_hat_x3 / np.sqrt(n), mean_x3 + t_val * std_hat_x3 / np.sqrt(n))
ci_var = ((n - 1) * var_hat_x3 / chi2_upper, (n - 1) * var_hat_x3 / chi2_lower)

print(f"Ожидание (a)   : ({ci_mean[0]:.2f}, {ci_mean[1]:.2f})")
print(f"Дисперсия (s^2): ({ci_var[0]:.2f}, {ci_var[1]:.2f})")

# 额外分析: X4的双峰分布和聚类
print("\n=== Анализ X4 (бимодальность и кластеризация) ===")

# 1. 直方图和经验分布函数
fig, axes = plt.subplots(1, 2, figsize=(14, 5))

sns.histplot(df['X4'], bins=30, color='coral', alpha=0.5, ax=axes[0], kde=True)
axes[0].set_title('Гистограмма X4')
axes[0].set_xlabel('X4 (мс)')
axes[0].set_ylabel('Частота')
axes[0].axvline(df['X4'].mean(), color='red', linestyle='--', label=f'Среднее = {df["X4"].mean():.2f}')
axes[0].axvline(df['X4'].median(), color='green', linestyle='--', label=f'Медиана = {df["X4"].median():.2f}')
axes[0].legend()

ecdf = ECDF(df['X4'])
axes[1].step(ecdf.x, ecdf.y, where='post', color='purple', linewidth=2)
axes[1].set_title('Эмпирическая функция распределения X4')
axes[1].set_xlabel('X4 (мс)')
axes[1].set_ylabel('F(x)')
axes[1].grid(True, alpha=0.3)
axes[1].axhline(0.5, color='red', linestyle='--', alpha=0.5)

plt.tight_layout()
plt.show()

# 2. K-means聚类
print("\nКластеризация (k=2):")
kmeans = KMeans(n_clusters=2, random_state=42, n_init=10)
df['Cluster'] = kmeans.fit_predict(df[['X4']])

# 可视化聚类
plt.figure(figsize=(12, 5))

plt.subplot(1, 2, 1)
sns.histplot(data=df, x='X4', hue='Cluster', palette='Set1', bins=30, kde=True, legend=False)
plt.title('Распределение X4 с разделением на кластеры')
plt.xlabel('X4 (мс)')
plt.ylabel('Частота')
plt.axvline(df['X4'].mean(), color='black', linestyle='--', label='Общее среднее', linewidth=2)
plt.legend()

plt.subplot(1, 2, 2)
sns.boxplot(data=df, x='Cluster', y='X4', hue='Cluster', palette='Set1', legend=False)
plt.title('Box-plot кластеров')
plt.xlabel('Кластер')
plt.ylabel('X4 (мс)')
plt.axhline(df['X4'].mean(), color='black', linestyle='--', label='Общее среднее', linewidth=2)
plt.legend()

plt.tight_layout()
plt.show()

print("\nХарактеристики кластеров:")
cluster_stats = df.groupby('Cluster')['X4'].agg(['mean', 'std', 'count', 'min', 'max']).round(2)
cluster_stats.columns = ['Среднее', 'Ст. отклонение', 'Количество', 'Минимум', 'Максимум']
print(cluster_stats)
print(f"\nОбщее среднее X4: {df['X4'].mean():.2f}")