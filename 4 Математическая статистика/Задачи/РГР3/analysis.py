import numpy as np
from scipy import stats
import matplotlib.pyplot as plt
import matplotlib
import sys
import io
matplotlib.use('Agg')

# Fix Windows console encoding
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

# ============================================================
# 1. Load data
# ============================================================
data = np.loadtxt('RGR3_A_5.csv', delimiter=',', skiprows=1)
i_col = data[:, 0]
x = data[:, 1]
y = data[:, 2]
n = len(x)

x_mean = np.mean(x)
y_mean = np.mean(y)

print(f"n = {n}")
print(f"x_mean = {x_mean:.6f}")
print(f"y_mean = {y_mean:.6f}")
print(f"x* = 1207.9904 (задано в варианте)")

# ============================================================
# 2. Scatter plot
# ============================================================
fig, ax = plt.subplots(figsize=(8, 5))
ax.scatter(x, y, color='blue', alpha=0.7, edgecolors='black', s=40)
ax.set_xlabel('$x$', fontsize=12)
ax.set_ylabel('$y$', fontsize=12)
ax.set_title('Диаграмма рассеяния', fontsize=14)
ax.grid(True, alpha=0.3)
fig.tight_layout()
fig.savefig('report/scatter.png', dpi=150)
plt.close(fig)
print("\nScatter plot saved.")

# ============================================================
# 3. Linear model: y = a + bx
# ============================================================
S_xx = np.sum((x - x_mean)**2)
S_xy = np.sum((x - x_mean) * (y - y_mean))
S_yy = np.sum((y - y_mean)**2)

b_lin = S_xy / S_xx
a_lin = y_mean - b_lin * x_mean

y_pred_lin = a_lin + b_lin * x
residuals_lin = y - y_pred_lin

RSS_lin = np.sum(residuals_lin**2)
TSS = S_yy
R2_lin = 1 - RSS_lin / TSS
RMSE_lin = np.sqrt(np.mean(residuals_lin**2))
A_lin = 100.0 / n * np.sum(np.abs(residuals_lin / y))

print(f"\n=== Линейная модель y = a + bx ===")
print(f"a = {a_lin:.6f}")
print(f"b = {b_lin:.6f}")
print(f"Уравнение: y = {a_lin:.4f} + {b_lin:.4f} x")
print(f"R² = {R2_lin:.6f}")
print(f"RMSE = {RMSE_lin:.6f}")
print(f"A (ср. ошибка аппроксимации) = {A_lin:.4f}%")
print(f"RSS = {RSS_lin:.6f}")

# ============================================================
# 4. Quadratic model: y = a + bx + cx^2
# ============================================================
coeffs_quad = np.polyfit(x, y, 2)  # [c, b, a]
c_quad, b_quad, a_quad = coeffs_quad

y_pred_quad = np.polyval(coeffs_quad, x)
RSS_quad = np.sum((y - y_pred_quad)**2)
R2_quad = 1 - RSS_quad / TSS
RMSE_quad = np.sqrt(np.mean((y - y_pred_quad)**2))
A_quad = 100.0 / n * np.sum(np.abs((y - y_pred_quad) / y))

print(f"\n=== Квадратичная модель y = a + bx + cx² ===")
print(f"a = {a_quad:.6f}")
print(f"b = {b_quad:.6f}")
print(f"c = {c_quad:.6f}")
print(f"Уравнение: y = {a_quad:.4f} + {b_quad:.4f} x + {c_quad:.6f} x²")
print(f"R² = {R2_quad:.6f}")
print(f"RMSE = {RMSE_quad:.6f}")
print(f"A (ср. ошибка аппроксимации) = {A_quad:.4f}%")

# ============================================================
# 5. Power model: y = a x^b  (степенная)
# ============================================================
x_log = np.log(x)
y_log = np.log(y)

# Linear regression on log-transformed data: ln y = ln a + b ln x
S_xx_log = np.sum((x_log - np.mean(x_log))**2)
S_xy_log = np.sum((x_log - np.mean(x_log)) * (y_log - np.mean(y_log)))

b_pow = S_xy_log / S_xx_log
log_a_pow = np.mean(y_log) - b_pow * np.mean(x_log)
a_pow = np.exp(log_a_pow)

y_pred_pow = a_pow * x**b_pow
RSS_pow = np.sum((y - y_pred_pow)**2)
R2_pow = 1 - RSS_pow / TSS
RMSE_pow = np.sqrt(np.mean((y - y_pred_pow)**2))
A_pow = 100.0 / n * np.sum(np.abs((y - y_pred_pow) / y))

print(f"\n=== Степенная модель y = a x^b ===")
print(f"ln a = {log_a_pow:.6f}, a = {a_pow:.6f}")
print(f"b = {b_pow:.6f}")
print(f"Уравнение: y = {a_pow:.4f} x^{b_pow:.4f}")
print(f"R² = {R2_pow:.6f}")
print(f"RMSE = {RMSE_pow:.6f}")
print(f"A (ср. ошибка аппроксимации) = {A_pow:.4f}%")

# ============================================================
# 6. Detailed statistical analysis of linear model
# ============================================================
s2 = RSS_lin / (n - 2)
s_val = np.sqrt(s2)

SE_b = s_val / np.sqrt(S_xx)
SE_a = s_val * np.sqrt(1.0/n + x_mean**2 / S_xx)

t_crit = stats.t.ppf(0.975, n - 2)

CI_a_low = a_lin - t_crit * SE_a
CI_a_high = a_lin + t_crit * SE_a
CI_b_low = b_lin - t_crit * SE_b
CI_b_high = b_lin + t_crit * SE_b

t_obs = b_lin / SE_b
p_value_b = 2 * (1 - stats.t.cdf(np.abs(t_obs), n - 2))

print(f"\n=== Подробный анализ линейной модели ===")
print(f"s² = {s2:.6f}")
print(f"s = {s_val:.6f}")
print(f"SE(a) = {SE_a:.6f}")
print(f"SE(b) = {SE_b:.6f}")
print(f"t_крит (0.975, {n-2}) = {t_crit:.6f}")
print(f"95% ДИ для a: [{CI_a_low:.6f}, {CI_a_high:.6f}]")
print(f"95% ДИ для b: [{CI_b_low:.6f}, {CI_b_high:.6f}]")
print(f"t_набл = {t_obs:.6f}")
print(f"p-value (для H0: b=0) = {p_value_b:.6f}")

if np.abs(t_obs) > t_crit:
    print("Гипотеза H0: b=0 ОТВЕРГАЕТСЯ на уровне α=0.05")
else:
    print("Гипотеза H0: b=0 НЕ ОТВЕРГАЕТСЯ на уровне α=0.05")

# ============================================================
# 7. Prediction at x*
# ============================================================
x_star = 1207.9904

y_pred_lin_star = a_lin + b_lin * x_star
y_pred_quad_star = np.polyval(coeffs_quad, x_star)
y_pred_pow_star = a_pow * x_star**b_pow

print(f"\n=== Прогноз при x* = {x_star} ===")
print(f"Линейная модель: y* = {y_pred_lin_star:.4f}")
print(f"Квадратичная модель: y* = {y_pred_quad_star:.4f}")
print(f"Степенная модель: y* = {y_pred_pow_star:.4f}")

# ============================================================
# 8. Comparison table
# ============================================================
print(f"\n=== Сводная таблица сравнения ===")
print(f"{'Модель':<25} {'R²':<12} {'RMSE':<12} {'A (%)':<12}")
print("-" * 60)
print(f"{'Линейная':<25} {R2_lin:<12.6f} {RMSE_lin:<12.4f} {A_lin:<12.4f}")
print(f"{'Квадратичная':<25} {R2_quad:<12.6f} {RMSE_quad:<12.4f} {A_quad:<12.4f}")
print(f"{'Степенная':<25} {R2_pow:<12.6f} {RMSE_pow:<12.4f} {A_pow:<12.4f}")

# ============================================================
# 9. Generate Plots for Report
# ============================================================

# --- Plot: All three models overlaid on data ---
x_smooth = np.linspace(x.min(), x.max(), 300)

fig, axes = plt.subplots(1, 3, figsize=(16, 5))

# Linear
axes[0].scatter(x, y, color='blue', alpha=0.6, edgecolors='black', s=30)
axes[0].plot(x_smooth, a_lin + b_lin * x_smooth, 'r-', linewidth=2)
axes[0].set_xlabel('$x$')
axes[0].set_ylabel('$y$')
axes[0].set_title('Линейная модель')
axes[0].grid(True, alpha=0.3)

# Quadratic
axes[1].scatter(x, y, color='blue', alpha=0.6, edgecolors='black', s=30)
axes[1].plot(x_smooth, np.polyval(coeffs_quad, x_smooth), 'r-', linewidth=2)
axes[1].set_xlabel('$x$')
axes[1].set_ylabel('$y$')
axes[1].set_title('Квадратичная модель')
axes[1].grid(True, alpha=0.3)

# Power
axes[2].scatter(x, y, color='blue', alpha=0.6, edgecolors='black', s=30)
axes[2].plot(x_smooth, a_pow * x_smooth**b_pow, 'r-', linewidth=2)
axes[2].set_xlabel('$x$')
axes[2].set_ylabel('$y$')
axes[2].set_title('Степенная модель')
axes[2].grid(True, alpha=0.3)

fig.tight_layout()
fig.savefig('report/all_models.png', dpi=150)
plt.close(fig)
print("\nAll models plot saved.")

# --- Plot: Residuals ---
fig, axes = plt.subplots(1, 3, figsize=(16, 5))

axes[0].scatter(x, residuals_lin, color='green', alpha=0.6, edgecolors='black', s=30)
axes[0].axhline(y=0, color='r', linestyle='--')
axes[0].set_xlabel('$x$')
axes[0].set_ylabel('$e_i$')
axes[0].set_title('Остатки (линейная)')
axes[0].grid(True, alpha=0.3)

residuals_quad = y - y_pred_quad
axes[1].scatter(x, residuals_quad, color='green', alpha=0.6, edgecolors='black', s=30)
axes[1].axhline(y=0, color='r', linestyle='--')
axes[1].set_xlabel('$x$')
axes[1].set_ylabel('$e_i$')
axes[1].set_title('Остатки (квадратичная)')
axes[1].grid(True, alpha=0.3)

residuals_pow = y - y_pred_pow
axes[2].scatter(x, residuals_pow, color='green', alpha=0.6, edgecolors='black', s=30)
axes[2].axhline(y=0, color='r', linestyle='--')
axes[2].set_xlabel('$x$')
axes[2].set_ylabel('$e_i$')
axes[2].set_title('Остатки (степенная)')
axes[2].grid(True, alpha=0.3)

fig.tight_layout()
fig.savefig('report/residuals.png', dpi=150)
plt.close(fig)
print("Residuals plot saved.")

# --- Plot: All models combined on one figure ---
fig, ax = plt.subplots(figsize=(10, 7))
ax.scatter(x, y, color='black', alpha=0.5, s=35, label='Данные', zorder=5)
ax.plot(x_smooth, a_lin + b_lin * x_smooth, 'b-', linewidth=2, label='Линейная', zorder=3)
ax.plot(x_smooth, np.polyval(coeffs_quad, x_smooth), 'r--', linewidth=2, label='Квадратичная', zorder=3)
ax.plot(x_smooth, a_pow * x_smooth**b_pow, 'g-.', linewidth=2, label='Степенная', zorder=3)
ax.set_xlabel('$x$', fontsize=12)
ax.set_ylabel('$y$', fontsize=12)
ax.set_title('Сравнение трёх моделей', fontsize=14)
ax.legend(fontsize=11)
ax.grid(True, alpha=0.3)
fig.tight_layout()
fig.savefig('report/comparison.png', dpi=150)
plt.close(fig)
print("Comparison plot saved.")

# ============================================================
# 10. Residuals table (first 10 rows)
# ============================================================
print(f"\n=== Остатки линейной модели (первые 10) ===")
print(f"{'i':<6} {'x':<14} {'y':<14} {'y_hat':<14} {'e_i':<14}")
print("-" * 65)
for i in range(min(10, n)):
    print(f"{int(i_col[i]):<6} {x[i]:<14.4f} {y[i]:<14.4f} {y_pred_lin[i]:<14.4f} {residuals_lin[i]:<14.4f}")

print(f"\n... (всего {n} наблюдений)")

# ============================================================
# 11. Save key results to a text file for reference
# ============================================================
with open('report/results.txt', 'w', encoding='utf-8') as f:
    f.write(f"n = {n}\n")
    f.write(f"x_mean = {x_mean:.6f}\n")
    f.write(f"y_mean = {y_mean:.6f}\n")
    f.write(f"x_star = {x_star}\n\n")

    f.write("=== Линейная модель ===\n")
    f.write(f"a = {a_lin:.6f}\n")
    f.write(f"b = {b_lin:.6f}\n")
    f.write(f"R2 = {R2_lin:.6f}\n")
    f.write(f"RMSE = {RMSE_lin:.6f}\n")
    f.write(f"A = {A_lin:.6f}\n")
    f.write(f"RSS = {RSS_lin:.6f}\n")
    f.write(f"s2 = {s2:.6f}\n")
    f.write(f"s = {s_val:.6f}\n")
    f.write(f"SE_a = {SE_a:.6f}\n")
    f.write(f"SE_b = {SE_b:.6f}\n")
    f.write(f"CI_a = [{CI_a_low:.6f}, {CI_a_high:.6f}]\n")
    f.write(f"CI_b = [{CI_b_low:.6f}, {CI_b_high:.6f}]\n")
    f.write(f"t_obs = {t_obs:.6f}\n")
    f.write(f"t_crit = {t_crit:.6f}\n")
    f.write(f"p_value_b = {p_value_b:.6f}\n\n")

    f.write("=== Квадратичная модель ===\n")
    f.write(f"a = {a_quad:.6f}\n")
    f.write(f"b = {b_quad:.6f}\n")
    f.write(f"c = {c_quad:.6f}\n")
    f.write(f"R2 = {R2_quad:.6f}\n")
    f.write(f"RMSE = {RMSE_quad:.6f}\n")
    f.write(f"A = {A_quad:.6f}\n\n")

    f.write("=== Степенная модель ===\n")
    f.write(f"a = {a_pow:.6f}\n")
    f.write(f"b = {b_pow:.6f}\n")
    f.write(f"R2 = {R2_pow:.6f}\n")
    f.write(f"RMSE = {RMSE_pow:.6f}\n")
    f.write(f"A = {A_pow:.6f}\n\n")

    f.write("=== Прогноз при x* ===\n")
    f.write(f"Линейная: {y_pred_lin_star:.4f}\n")
    f.write(f"Квадратичная: {y_pred_quad_star:.4f}\n")
    f.write(f"Степенная: {y_pred_pow_star:.4f}\n")

print("\nAll results saved to report/results.txt")
print("Analysis complete.")
