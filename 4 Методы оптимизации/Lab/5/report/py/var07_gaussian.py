import numpy as np
import matplotlib.pyplot as plt
from scipy.optimize import minimize

# ==============================================================================
# ВАРИАНТ 7
# ==============================================================================
data = np.array([
    [1.10, 1.10, 0.29],
    [2.01, 1.98, 1.24],
    [3.01, 2.85, 4.94],
    [3.86, 3.99, 4.72],
    [5.10, 4.90, 0.77]
])

# ==============================================================================
# ЗАДАНИЕ 1: Извлечение значений X, Y, Z из data
# ==============================================================================
X = data[:, 0]
Y = data[:, 1]
Z = data[:, 2]

print("Мои данные:")
for i in range(len(X)):
    print(f"  Точка {i}: x={X[i]:.2f}, y={Y[i]:.2f}, z={Z[i]:.2f}")

# ==============================================================================
# ЗАДАНИЕ 2: Функция Гаусса
# ==============================================================================
def gauss_2d(x, y, A, x0, y0, sigma_x, sigma_y, theta=0, offset=0):
    """
    2D функция Гаусса
    Формула: A * exp(-(x_new^2/(2*sigma_x^2) + y_new^2/(2*sigma_y^2))) + offset,
    x_new, y_new - координаты в канонической системе
    """
    if theta != 0:
        x_new = (x - x0) * np.cos(theta) + (y - y0) * np.sin(theta)
        y_new = -(x - x0) * np.sin(theta) + (y - y0) * np.cos(theta)
    else:
        x_new = x - x0
        y_new = y - y0
    exp_part = np.exp(-((x_new**2)/(2*sigma_x**2) + (y_new**2)/(2*sigma_y**2)))
    result = A * exp_part + offset
    return result

# ==============================================================================
# ЗАДАНИЕ 3: Функция потерь
# ==============================================================================
def loss_function(model_params):
    """MSE для реальных и модельных значений."""
    A, x0, y0, sigma_x, sigma_y, theta, offset = model_params

    if sigma_x <= 0 or sigma_y <= 0 or A <= 0:
        return 1e10

    predictions = []
    for i in range(len(X)):
        pred = gauss_2d(X[i], Y[i], A, x0, y0, sigma_x, sigma_y, theta, offset)
        predictions.append(pred)

    errors = (np.array(predictions) - Z) ** 2
    mse = 0.5 * np.mean(errors)
    return mse

# ==============================================================================
# ЗАДАНИЕ 4: Начальное приближение
# ==============================================================================
max_idx = np.argmax(Z)               # индекс максимума Z
A_start = Z[max_idx] + 0.1           # максимум Z + корректировка
x0_start = X[max_idx]                # X в точке максимума
y0_start = Y[max_idx]                # Y в точке максимума
sigma_x_start = np.std(X) * 0.5
sigma_y_start = np.std(Y) * 0.5
offset_start = 0.0
theta_start = 0.0

params_start = [A_start, x0_start, y0_start, sigma_x_start, sigma_y_start, theta_start, offset_start]

print("Значения для инициализации модельных параметров (начальное приближение):")
print(f"  Amplitude (A):     {A_start:.2f}")
print(f"  Center (x0, y0):   ({x0_start:.2f}, {y0_start:.2f})")
print(f"  Sigma_x:           {sigma_x_start:.2f}")
print(f"  Sigma_y:           {sigma_y_start:.2f}")
print(f"  Theta (rotation):  0.00 рад")
print(f"  Offset:            0.00")
print()

# ==============================================================================
# ЗАДАНИЕ 5: Границы и оптимизация
# ==============================================================================
bounds = [
    (0.1, 10.0), (0.0, 6.0), (0.0, 6.0),
    (0.1, 5.0), (0.1, 5.0), (-np.pi/4, np.pi/4), (-1.0, 1.0)
]

print("\nЗапускаем оптимизацию...")
result = minimize(loss_function, params_start, method='L-BFGS-B', bounds=bounds)

# ==============================================================================
# РЕЗУЛЬТАТЫ
# ==============================================================================
A_opt, x0_opt, y0_opt, sigma_x_opt, sigma_y_opt, theta_opt, offset_opt = result.x

print("\n" + "="*50)
print("РЕЗУЛЬТАТЫ")
print("="*50)
print(f"\nA = {A_opt:.4f}")
print(f"x0 = {x0_opt:.4f}, y0 = {y0_opt:.4f}")
print(f"sigma_x = {sigma_x_opt:.4f}, sigma_y = {sigma_y_opt:.4f}")
print(f"theta = {theta_opt:.4f} рад = {np.degrees(theta_opt):.2f}°, offset = {offset_opt:.4f}")
print(f"\nФинальная ошибка: {result.fun:.8f}")

# ==============================================================================
# ЗАДАНИЕ 6: Проверка (верификация)
# ==============================================================================
predictions = []
for i in range(len(X)):
    pred = gauss_2d(X[i], Y[i], A_opt, x0_opt, y0_opt, sigma_x_opt, sigma_y_opt, theta_opt, offset_opt)
    predictions.append(pred)

errors = np.array(predictions) - Z
squared_errors = errors ** 2

print("\nПроверка:")
print(f"{'Точка':<8} {'x':<6} {'y':<6} {'z_факт':<10} {'z_модель':<10} {'Ошибка':<10} {'Кв. ошибка':<12}")
print("-" * 62)
for i in range(len(X)):
    print(f"{i:<8} {X[i]:<6.2f} {Y[i]:<6.2f} {Z[i]:<10.2f} {predictions[i]:<10.4f} {errors[i]:<10.4f} {squared_errors[i]:<12.6f}")

mse = np.mean(squared_errors)
rmse = np.sqrt(mse)
print(f"\nMSE = {mse:.8f}")
print(f"RMSE = {rmse:.8f}")

# ==============================================================================
# ЗАДАНИЕ 7: Визуализация
# ==============================================================================
x_grid = np.linspace(0, 6, 50)
y_grid = np.linspace(0, 6, 50)
X_grid, Y_grid = np.meshgrid(x_grid, y_grid)

Z_grid = np.zeros((50, 50))
for i in range(50):
    for j in range(50):
        Z_grid[i, j] = gauss_2d(X_grid[i, j], Y_grid[i, j], A_opt, x0_opt, y0_opt, sigma_x_opt, sigma_y_opt, theta_opt, offset_opt)

# 3D график
fig = plt.figure(figsize=(14, 6))

ax1 = fig.add_subplot(121, projection='3d')
ax1.plot_surface(X_grid, Y_grid, Z_grid, cmap='viridis', alpha=0.8)
ax1.scatter(X, Y, Z, c='red', s=80)
ax1.set_xlabel('X')
ax1.set_ylabel('Y')
ax1.set_zlabel('Z')
ax1.set_title('3D-визуализация Гауссианы (Вариант 7)')

# Линии уровня
ax2 = fig.add_subplot(122)
contour = ax2.contourf(X_grid, Y_grid, Z_grid, levels=25, cmap='viridis', alpha=0.9)
scatter = ax2.scatter(X, Y, c=Z, s=120, edgecolors='black', cmap='viridis', vmin=Z.min(), vmax=Z.max())
ax2.contour(X_grid, Y_grid, Z_grid, levels=10, colors='white', alpha=0.3, linewidths=0.5)
ax2.set_xlabel('X', fontsize=10)
ax2.set_ylabel('Y', fontsize=10)
ax2.set_title('Линии уровня модельной функции\nи точки исходных данных', fontsize=12, fontweight='bold')
ax2.grid(True, alpha=0.3)
cbar = plt.colorbar(contour, ax=ax2, label='Z')
cbar.ax.tick_params(labelsize=9)

# Добавляем подписи номеров точек
for i in range(len(X)):
    ax2.annotate(f'{i}', (X[i], Y[i]), textcoords="offset points", xytext=(8, 8), fontsize=10, color='red')

plt.tight_layout()
print("\nГотово! Получилась двумерная гауссиана - аппроксимация для z(x,y)!")
plt.savefig('../pic/gaussian_3d.png', dpi=300, bbox_inches='tight')
plt.close()
print("График сохранён в ../pic/gaussian_3d.png")
