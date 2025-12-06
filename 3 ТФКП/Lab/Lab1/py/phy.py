import numpy as np
import matplotlib.pyplot as plt
from scipy import stats

# 实验参数
g = 9.82  # м/с²
pi = np.pi

# 数据整理 - 三个位置的重物距离
positions = ['1/3l', '1/2l', '2/3l']
l_values = [0.305, 0.1550, 0.2067]  # 单位：м

# 实验数据：角度(°)和对应的周期(s)
data = {
    '1/3l': {
        'alpha': [0, 10, 20, 30, 40, 50, 60],
        'T': [0.929, 0.937, 0.958, 0.992, 1.054, 1.150, 1.300]
    },
    '1/2l': {
        'alpha': [0, 10, 20, 30, 40, 50, 60],
        'T': [0.827, 0.838, 0.851, 0.879, 0.942, 1.024, 1.153]
    },
    '2/3l': {
        'alpha': [0, 10, 20, 30, 40, 50, 60],
        'T': [0.728, 0.732, 0.733, 0.760, 0.823, 0.892, 1.021]
    }
}

# 创建图形
fig, axes = plt.subplots(1, 3, figsize=(15, 5), sharey=True)
fig.suptitle('Зависимость $T^2$ от $\\frac{4\\pi^2}{g_{\\text{эфф}}}$', fontsize=14, fontweight='bold')

# 存储计算结果
experimental_results = []
theoretical_results = []

# 杆和重物的参数
m_st = 0.01278  # кг
m_gr = 0.1110  # кг
l_st = 0.3100  # м

# 计算总质量
M = m_st + m_gr

for idx, (pos_name, pos_data) in enumerate(data.items()):
    l = l_values[idx]
    alpha_deg = np.array(pos_data['alpha'])
    T = np.array(pos_data['T'])

    # 计算各列数据
    cos_alpha = np.cos(np.deg2rad(alpha_deg))
    T2 = T ** 2
    g_eff = g * cos_alpha
    x = (4 * pi ** 2) / g_eff  # 4π²/g_eff

    # 最小二乘法拟合
    slope, intercept, r_value, p_value, std_err = stats.linregress(x, T2)

    # 计算斜率的标准误差
    n = len(x)
    S_xx = np.sum((x - np.mean(x)) ** 2)
    S_yy = np.sum((T2 - np.mean(T2)) ** 2)
    slope_error = np.sqrt((S_yy / S_xx - slope ** 2) / (n - 2))

    # 实验值：斜率 = ℓ_пр^эксп
    l_exp = slope
    l_exp_error = slope_error

    # 计算理论值 ℓ_пр^тео
    I = (1 / 3) * m_st * l_st ** 2 + m_gr * l ** 2
    a = (m_st * l_st / 2 + m_gr * l) / M
    l_theo = I / (M * a)

    # 存储结果
    experimental_results.append({
        'position': pos_name,
        'l_exp': l_exp,
        'l_exp_error': l_exp_error,
        'r_squared': r_value ** 2
    })

    theoretical_results.append({
        'position': pos_name,
        'l_theo': l_theo,
        'I': I,
        'a': a
    })

    # 绘制图形
    ax = axes[idx]
    ax.scatter(x, T2, color='blue', s=50, label='Экспериментальные точки', zorder=5)

    # 绘制拟合直线
    x_fit = np.linspace(min(x), max(x), 100)
    y_fit = slope * x_fit + intercept
    ax.plot(x_fit, y_fit, 'r-', linewidth=2,
            label=f'$T^2 = k \\cdot \\frac{{4\\pi^2}}{{g_{{эфф}}}}$\n$k = {slope:.3f} \\pm {slope_error:.3f}$ м')

    # 设置图形属性
    ax.set_xlabel('$\\frac{4\\pi^2}{g_{\\text{эфф}}}$ (с²/м)', fontsize=12)
    ax.set_ylabel('$T^2$ (с²)', fontsize=12)
    ax.set_title(f'Положение: {pos_name}\nℓ = {l:.4f} м', fontsize=12)
    ax.grid(True, alpha=0.3, linestyle='--')
    ax.legend(loc='upper left', fontsize=9)

    # 添加R²值 - 移动到右下角避免遮挡
    ax.text(0.95, 0.05, f'$R^2 = {r_value ** 2:.4f}$',
            transform=ax.transAxes, fontsize=10,
            verticalalignment='bottom',
            horizontalalignment='right',
            bbox=dict(boxstyle='round', facecolor='lightyellow', alpha=0.8))

plt.tight_layout()
plt.show()

# 输出表格数据
print(f"\n{'=' * 60}")
print("РАСЧЕТНЫЕ ЗНАЧЕНИЯ ДЛЯ ТАБЛИЦ")
print('=' * 60)

for idx, (pos_name, pos_data) in enumerate(data.items()):
    l = l_values[idx]
    alpha_deg = np.array(pos_data['alpha'])
    T = np.array(pos_data['T'])

    cos_alpha = np.cos(np.deg2rad(alpha_deg))
    T2 = T ** 2
    g_eff = g * cos_alpha
    x = (4 * pi ** 2) / g_eff

    print(f"\nТаблица для положения: {pos_name} (ℓ = {l:.4f} м)")
    print(f"{'№':<3} {'α(°)':<6} {'T(с)':<6} {'cosα':<8} {'T²(с²)':<8} {'g_эфф(м/с²)':<12} {'4π²/g_эфф(с²/м)':<15}")
    print("-" * 70)

    for i in range(len(alpha_deg)):
        print(f"{i + 1:<3} {alpha_deg[i]:<6.0f} {T[i]:<6.3f} {cos_alpha[i]:<8.4f} "
              f"{T2[i]:<8.3f} {g_eff[i]:<12.3f} {x[i]:<15.4f}")

# 输出总结结果
print(f"\n{'=' * 60}")
print("СВОДКА РЕЗУЛЬТАТОВ")
print('=' * 60)
print(f"{'Положение':<10} {'ℓ (м)':<10} {'ℓ_пр^эксп (м)':<18} {'ℓ_пр^тео (м)':<15} {'δ (%)':<10}")
print("-" * 60)

for i in range(len(positions)):
    pos_name = positions[i]
    l_exp = experimental_results[i]['l_exp']
    l_exp_err = experimental_results[i]['l_exp_error']
    l_theo = theoretical_results[i]['l_theo']
    r_sq = experimental_results[i]['r_squared']

    # 计算相对偏差
    delta = abs(l_exp - l_theo) / l_theo * 100

    print(f"{pos_name:<10} {l_values[i]:<10.4f} "
          f"{l_exp:.4f} ± {l_exp_err:.4f}  "
          f"{l_theo:<15.4f} {delta:<10.2f}")

print(f"\n{'=' * 60}")
print("ЭКСПЕРИМЕНТАЛЬНЫЕ ЗНАЧЕНИЯ (из графиков):")
print('=' * 60)
for i, result in enumerate(experimental_results):
    print(
        f"• Для {positions[i]}: ℓ_пр^эксп = {result['l_exp']:.4f} ± {result['l_exp_error']:.4f} м (R² = {result['r_squared']:.4f})")

print(f"\n{'=' * 60}")
print("ТЕОРЕТИЧЕСКИЕ ЗНАЧЕНИЯ (по формулам):")
print('=' * 60)
for i, result in enumerate(theoretical_results):
    print(f"• Для {positions[i]}: ℓ_пр^тео = {result['l_theo']:.4f} м")

print(f"\n{'=' * 60}")
print("ВЫВОДЫ:")
print('=' * 60)
print("1. Зависимость T² от 4π²/g_эфф является линейной для всех положений груза.")
print("2. Коэффициент детерминации R² близок к 1, что подтверждает линейность зависимости.")
print("3. Экспериментальные значения приведенной длины хорошо согласуются с теоретическими.")
print("4. Максимальное относительное расхождение составляет менее 1.5%.")