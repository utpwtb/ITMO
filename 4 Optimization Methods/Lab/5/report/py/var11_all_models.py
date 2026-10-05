import numpy as np
import matplotlib.pyplot as plt
from scipy.optimize import minimize
import os

# ==============================================================================
# ВАРИАНТ 11 — Исходные данные
# ==============================================================================
data = np.array([
    [0.85, 1.12, 0.73],
    [1.83, 2.20, 3.65],
    [2.91, 3.12, 4.86],
    [3.93, 3.92, 2.00],
    [4.86, 4.94, 0.32]
])

X = data[:, 0]
Y = data[:, 1]
Z = data[:, 2]
XY = data[:, :2]

save_dir = '../pic'
os.makedirs(save_dir, exist_ok=True)

print("="*70)
print("ЛАБОРАТОРНАЯ РАБОТА №5 — ВАРИАНТ 11")
print("Аппроксимация табличных данных")
print("="*70)

# ==============================================================================
# ЗАДАНИЕ 1: Аппроксимация двумерной гауссианой
# ==============================================================================
print("\n" + "="*70)
print("ЗАДАНИЕ 1: Гауссова модель")
print("="*70)

def gaussian_2d(xy, A, x0, y0, sigma_x, sigma_y, theta=0, offset=0):
    if isinstance(xy, tuple):
        x, y = xy
    else:
        x, y = xy[:, 0], xy[:, 1]
    if theta != 0:
        dx = (x - x0) * np.cos(theta) + (y - y0) * np.sin(theta)
        dy = -(x - x0) * np.sin(theta) + (y - y0) * np.cos(theta)
    else:
        dx = x - x0
        dy = y - y0
    Q = (dx**2) / (2 * sigma_x**2) + (dy**2) / (2 * sigma_y**2)
    return A * np.exp(-Q) + offset

def loss_gaussian(params, x, y, z_true):
    A, x0, y0, sigma_x, sigma_y, theta, offset = params
    if sigma_x <= 0 or sigma_y <= 0 or A <= 0:
        return 1e10
    z_pred = gaussian_2d((x, y), A, x0, y0, sigma_x, sigma_y, theta, offset)
    return np.mean((z_pred - z_true) ** 2)

peak_idx = np.argmax(Z)
init_gauss = [Z[peak_idx] + 0.1, X[peak_idx], Y[peak_idx],
              np.std(X)*0.5, np.std(Y)*0.5, 0.0, 0.0]

bounds_gauss = [
    (0.1, 10.0), (0.0, 6.0), (0.0, 6.0),
    (0.1, 5.0), (0.1, 5.0), (-np.pi/4, np.pi/4), (-1.0, 1.0)
]

print(f"\nНачальное приближение:")
print(f"  A={init_gauss[0]:.2f}, x0={init_gauss[1]:.2f}, y0={init_gauss[2]:.2f}")
print(f"  sigma_x={init_gauss[3]:.2f}, sigma_y={init_gauss[4]:.2f}")

gauss_loss_hist = []
def cb_gauss(xk):
    gauss_loss_hist.append(loss_gaussian(xk, X, Y, Z))

res_gauss = minimize(loss_gaussian, init_gauss, args=(X, Y, Z),
                     method='L-BFGS-B', bounds=bounds_gauss,
                     callback=cb_gauss)
A_g, x0_g, y0_g, sx_g, sy_g, th_g, off_g = res_gauss.x
z_pred_gauss = gaussian_2d((X, Y), *res_gauss.x)
err_gauss = z_pred_gauss - Z
sq_err_gauss = err_gauss ** 2
mse_gauss = np.mean(sq_err_gauss)
rmse_gauss = np.sqrt(mse_gauss)

print(f"\nОптимальные параметры:")
print(f"  A = {A_g:.4f}")
print(f"  x0 = {x0_g:.4f}, y0 = {y0_g:.4f}")
print(f"  sigma_x = {sx_g:.4f}, sigma_y = {sy_g:.4f}")
print(f"  theta = {th_g:.4f} рад = {np.degrees(th_g):.2f}°")
print(f"  offset = {off_g:.4f}")
print(f"  Число итераций: {res_gauss.nit}")

print(f"\nАналитический вид модели:")
print(f"  z(x,y) = {A_g:.4f} * exp(-Q) + {off_g:.4f}")
print(f"  Q = (x - {x0_g:.4f})^2/(2*{sx_g:.4f}^2) + (y - {y0_g:.4f})^2/(2*{sy_g:.4f}^2)")
if abs(th_g) > 0.01:
    print(f"  Поворот: theta = {np.degrees(th_g):.2f}°")

print(f"\nТаблица невязок (Гауссиана):")
print(f"  {'Точка':<8} {'x':<6} {'y':<6} {'z_факт':<10} {'z_модель':<12} {'Невязка':<12} {'Кв.невязка':<14}")
print(f"  " + "-"*68)
for i in range(len(X)):
    print(f"  {i:<8} {X[i]:<6.2f} {Y[i]:<6.2f} {Z[i]:<10.2f} {z_pred_gauss[i]:<12.4f} {err_gauss[i]:<12.6f} {sq_err_gauss[i]:<14.10f}")
print(f"\n  MSE = {mse_gauss:.10f}, RMSE = {rmse_gauss:.10f}")

# ==============================================================================
# ЗАДАНИЕ 2: Аппроксимация эллиптическим параболоидом
# ==============================================================================
print("\n" + "="*70)
print("ЗАДАНИЕ 2: Эллиптический параболоид")
print("="*70)

def elliptic_paraboloid(xy, z0, x0, y0, a, b, h):
    if isinstance(xy, tuple):
        x, y = xy
    else:
        x, y = xy[:, 0], xy[:, 1]
    dx = x - x0
    dy = y - y0
    return z0 + a * dx**2 + b * dy**2 + 2 * h * dx * dy

def loss_paraboloid(params, x, y, z_true):
    z0, x0, y0, a, b, h = params
    if a * b <= h**2 + 1e-6:
        return 1e10
    z_pred = elliptic_paraboloid((x, y), z0, x0, y0, a, b, h)
    return np.mean((z_pred - z_true) ** 2)

peak_idx_p = np.argmax(Z)
init_parab = [Z[peak_idx_p], X[peak_idx_p], Y[peak_idx_p], -1.0, -1.0, 0.0]

bounds_parab = [
    (-1.0, 10.0), (0.0, 6.0), (0.0, 6.0),
    (-5.0, -0.01), (-5.0, -0.01), (-2.0, 2.0)
]

print(f"\nНачальное приближение:")
print(f"  z0={init_parab[0]:.2f}, x0={init_parab[1]:.2f}, y0={init_parab[2]:.2f}")

parab_loss_hist = []
def cb_parab(xk):
    parab_loss_hist.append(loss_paraboloid(xk, X, Y, Z))

res_parab = minimize(loss_paraboloid, init_parab, args=(X, Y, Z),
                     method='L-BFGS-B', bounds=bounds_parab,
                     callback=cb_parab,
                     options={'maxiter': 500})
z0_p, x0_p, y0_p, a_p, b_p, h_p = res_parab.x
z_pred_parab = elliptic_paraboloid((X, Y), *res_parab.x)
err_parab = z_pred_parab - Z
sq_err_parab = err_parab ** 2
mse_parab = np.mean(sq_err_parab)
rmse_parab = np.sqrt(mse_parab)

print(f"\nОптимальные параметры:")
print(f"  z0 = {z0_p:.4f}, x0 = {x0_p:.4f}, y0 = {y0_p:.4f}")
print(f"  a = {a_p:.4f}, b = {b_p:.4f}, h = {h_p:.4f}")
print(f"  Число итераций: {res_parab.nit}")

print(f"\nАналитический вид модели:")
print(f"  z(x,y) = {z0_p:.4f}")
print(f"           + ({a_p:.4f})*(x - {x0_p:.4f})^2")
print(f"           + ({b_p:.4f})*(y - {y0_p:.4f})^2")
print(f"           + 2*({h_p:.4f})*(x - {x0_p:.4f})(y - {y0_p:.4f})")

print(f"\nТаблица невязок (Параболоид):")
print(f"  {'Точка':<8} {'x':<6} {'y':<6} {'z_факт':<10} {'z_модель':<12} {'Невязка':<12} {'Кв.невязка':<14}")
print(f"  " + "-"*68)
for i in range(len(X)):
    print(f"  {i:<8} {X[i]:<6.2f} {Y[i]:<6.2f} {Z[i]:<10.2f} {z_pred_parab[i]:<12.4f} {err_parab[i]:<12.6f} {sq_err_parab[i]:<14.6f}")
print(f"\n  MSE = {mse_parab:.6f}, RMSE = {rmse_parab:.6f}")

# ==============================================================================
# ЗАДАНИЕ 3: Аппроксимация константной моделью (MSE и MAE)
# ==============================================================================
print("\n" + "="*70)
print("ЗАДАНИЕ 3: Константная модель (MSE и MAE)")
print("="*70)

# MSE-оптимальная константа: среднее арифметическое
const_mse = np.mean(Z)
# MAE-оптимальная константа: медиана
const_mae = np.median(Z)

z_pred_const_mse = np.full_like(Z, const_mse)
z_pred_const_mae = np.full_like(Z, const_mae)

err_const_mse = z_pred_const_mse - Z
sq_err_const_mse = err_const_mse ** 2
mse_const = np.mean(sq_err_const_mse)
mae_of_mse_const = np.mean(np.abs(err_const_mse))

err_const_mae = z_pred_const_mae - Z
abs_err_const_mae = np.abs(err_const_mae)
mae_const = np.mean(abs_err_const_mae)
mse_of_mae_const = np.mean(err_const_mae ** 2)

print(f"\nМинимизация MSE:")
print(f"  Оптимальная константа z = mean(z) = {const_mse:.4f}")
print(f"  MSE(min) = {mse_const:.4f}")
print(f"  MAE = {mae_of_mse_const:.4f}")

print(f"\nМинимизация MAE:")
print(f"  Оптимальная константа z = median(z) = {const_mae:.4f}")
print(f"  MAE(min) = {mae_const:.4f}")
print(f"  MSE = {mse_of_mae_const:.4f}")

print(f"\nТаблица невязок (MSE-константа = {const_mse:.4f}):")
print(f"  {'Точка':<8} {'x':<6} {'y':<6} {'z_факт':<10} {'z_модель':<12} {'Невязка':<12} {'Кв.невязка':<14}")
print(f"  " + "-"*68)
for i in range(len(X)):
    print(f"  {i:<8} {X[i]:<6.2f} {Y[i]:<6.2f} {Z[i]:<10.2f} {z_pred_const_mse[i]:<12.4f} {err_const_mse[i]:<12.6f} {sq_err_const_mse[i]:<14.6f}")

print(f"\nТаблица невязок (MAE-константа = {const_mae:.4f}):")
print(f"  {'Точка':<8} {'x':<6} {'y':<6} {'z_факт':<10} {'z_модель':<12} {'Невязка':<12} {'|Невязка|':<12}")
print(f"  " + "-"*68)
for i in range(len(X)):
    print(f"  {i:<8} {X[i]:<6.2f} {Y[i]:<6.2f} {Z[i]:<10.2f} {z_pred_const_mae[i]:<12.4f} {err_const_mae[i]:<12.6f} {abs_err_const_mae[i]:<12.6f}")

# ==============================================================================
# ЗАДАНИЕ 5: Аппроксимация RBF-сетью
# ==============================================================================
print("\n" + "="*70)
print("ЗАДАНИЕ 5: RBF-сеть")
print("="*70)

class KMeansScratch:
    def __init__(self, n_clusters=2, max_iters=100):
        self.n_clusters = n_clusters
        self.max_iters = max_iters
        self.centroids = None

    def _euclidean_distance(self, X, centroids):
        distances = np.zeros((X.shape[0], centroids.shape[0]))
        for k in range(centroids.shape[0]):
            diff = X - centroids[k]
            distances[:, k] = np.sqrt(np.sum(diff ** 2, axis=1))
        return distances

    def fit(self, X):
        indices = np.array([0, 2])
        self.centroids = X[indices].copy()
        for _ in range(self.max_iters):
            distances = self._euclidean_distance(X, self.centroids)
            labels = np.argmin(distances, axis=1)
            new_centroids = np.zeros_like(self.centroids)
            for k in range(self.n_clusters):
                cluster_points = X[labels == k]
                if len(cluster_points) > 0:
                    new_centroids[k] = cluster_points.mean(axis=0)
                else:
                    new_centroids[k] = self.centroids[k]
            shift = np.sqrt(np.sum((new_centroids - self.centroids) ** 2))
            self.centroids = new_centroids
            if shift < 1e-4:
                break
        return self.centroids

class RBFNetwork:
    def __init__(self, n_hidden=2, lr=0.01, epochs=500):
        self.n_hidden = n_hidden
        self.lr = lr
        self.epochs = epochs
        self.centers = None
        self.widths = None
        self.weights = None
        self.bias = None
        self.loss_history = []

    def _gaussian(self, X, center, width):
        diff = X - center
        dist_sq = np.sum(diff ** 2, axis=1)
        return np.exp(-dist_sq / (2 * width ** 2))

    def initialize(self, X):
        kmeans = KMeansScratch(n_clusters=self.n_hidden)
        self.centers = kmeans.fit(X)
        dist_between = np.sqrt(np.sum((self.centers[0] - self.centers[1])**2))
        self.widths = np.array([dist_between, dist_between]) * 0.5
        self.widths = np.maximum(self.widths, 0.1)
        self.weights = np.random.randn(self.n_hidden) * 0.5
        self.bias = 0.0

    def forward(self, X):
        activations = np.zeros((X.shape[0], self.n_hidden))
        for j in range(self.n_hidden):
            activations[:, j] = self._gaussian(X, self.centers[j], self.widths[j])
        output = np.dot(activations, self.weights) + self.bias
        return output, activations

    def train(self, X, y):
        self.loss_history = []
        N = X.shape[0]
        for epoch in range(self.epochs):
            y_pred, activations = self.forward(X)
            error = y_pred - y
            loss = np.mean(error ** 2)
            self.loss_history.append(loss)

            grad_w = np.zeros(self.n_hidden)
            grad_b = 0.0
            grad_sigma = np.zeros(self.n_hidden)
            grad_c = np.zeros_like(self.centers)
            for i in range(N):
                for j in range(self.n_hidden):
                    phi = activations[i, j]
                    diff = X[i] - self.centers[j]
                    dist_sq = np.sum(diff ** 2)
                    grad_w[j] += (2.0 / N) * error[i] * phi
                    grad_b += (2.0 / N) * error[i]
                    if self.widths[j] > 1e-5:
                        grad_sigma[j] += (2.0 / N) * error[i] * self.weights[j] * phi * (dist_sq / (self.widths[j] ** 3))
                        grad_c[j] += (2.0 / N) * error[i] * self.weights[j] * phi * (diff / (self.widths[j] ** 2))
            self.weights -= self.lr * grad_w
            self.bias -= self.lr * grad_b
            self.widths -= self.lr * grad_sigma
            self.centers -= self.lr * grad_c
            self.widths = np.maximum(self.widths, 0.01)

    def predict(self, X):
        y_pred, _ = self.forward(X)
        return y_pred

np.random.seed(42)
rbf = RBFNetwork(n_hidden=2, lr=0.1, epochs=500)
rbf.initialize(XY)

print(f"\nИнициализация K-средними:")
print(f"  Центры: c1=({rbf.centers[0,0]:.4f}, {rbf.centers[0,1]:.4f}), c2=({rbf.centers[1,0]:.4f}, {rbf.centers[1,1]:.4f})")
print(f"  Ширины: sigma1={rbf.widths[0]:.4f}, sigma2={rbf.widths[1]:.4f}")

rbf.train(XY, Z)
z_pred_rbf = rbf.predict(XY)
err_rbf = z_pred_rbf - Z
sq_err_rbf = err_rbf ** 2
mse_rbf = np.mean(sq_err_rbf)
rmse_rbf = np.sqrt(mse_rbf)

print(f"Начальный лосс: {rbf.loss_history[0]:.6f}")
print(f"Конечный лосс:  {rbf.loss_history[-1]:.6f}")

print(f"\nОптимальные параметры:")
print(f"  bias = {rbf.bias:.4f}")
for i in range(rbf.n_hidden):
    print(f"  Нейрон {i+1}: w={rbf.weights[i]:.4f}, c=({rbf.centers[i,0]:.4f}, {rbf.centers[i,1]:.4f}), sigma={rbf.widths[i]:.4f}")

print(f"\nАналитический вид модели:")
print(f"  z(x,y) = {rbf.bias:.4f}")
for i in range(rbf.n_hidden):
    print(f"    + {rbf.weights[i]:.4f} * exp(-((x-{rbf.centers[i,0]:.4f})^2 + (y-{rbf.centers[i,1]:.4f})^2) / (2*{rbf.widths[i]:.4f}^2))")

print(f"\nТаблица невязок (RBF-сеть):")
print(f"  {'Точка':<8} {'x':<6} {'y':<6} {'z_факт':<10} {'z_модель':<12} {'Невязка':<12} {'Кв.невязка':<14}")
print(f"  " + "-"*68)
for i in range(len(X)):
    print(f"  {i:<8} {X[i]:<6.2f} {Y[i]:<6.2f} {Z[i]:<10.2f} {z_pred_rbf[i]:<12.4f} {err_rbf[i]:<12.6f} {sq_err_rbf[i]:<14.10f}")
print(f"\n  MSE = {mse_rbf:.10f}, RMSE = {rmse_rbf:.10f}")

# ==============================================================================
# СВОДНАЯ ТАБЛИЦА
# ==============================================================================
print("\n" + "="*70)
print("СВОДНАЯ ТАБЛИЦА РЕЗУЛЬТАТОВ")
print("="*70)

print(f"\n{'Точка':<8} {'x':<6} {'y':<6} {'z_факт':<10} {'Гаусс':<10} {'Параб.':<10} {'RBF':<10}")
print("-" * 60)
for i in range(len(X)):
    print(f"{i:<8} {X[i]:<6.2f} {Y[i]:<6.2f} {Z[i]:<10.2f} {z_pred_gauss[i]:<10.4f} {z_pred_parab[i]:<10.4f} {z_pred_rbf[i]:<10.4f}")

print(f"\n{'Метод':<20} {'MSE':<14} {'RMSE':<14}")
print("-" * 48)
print(f"{'Гауссиана':<20} {mse_gauss:<14.10f} {rmse_gauss:<14.10f}")
print(f"{'Параболоид':<20} {mse_parab:<14.6f} {rmse_parab:<14.6f}")
print(f"{'Конст. MSE':<20} {mse_const:<14.6f} {np.sqrt(mse_const):<14.6f}")
print(f"{'Конст. MAE':<20} {mse_of_mae_const:<14.6f} {np.sqrt(mse_of_mae_const):<14.6f}")
print(f"{'RBF-сеть':<20} {mse_rbf:<14.10f} {rmse_rbf:<14.10f}")

# ==============================================================================
# ГРАФИКИ
# ==============================================================================
x_grid = np.linspace(0, 6, 50)
y_grid = np.linspace(0, 6, 50)
Xg, Yg = np.meshgrid(x_grid, y_grid)
XY_grid = np.column_stack([Xg.ravel(), Yg.ravel()])

Zg_gauss = gaussian_2d((XY_grid[:, 0], XY_grid[:, 1]), A_g, x0_g, y0_g, sx_g, sy_g, th_g, off_g).reshape(50, 50)
Zg_parab = elliptic_paraboloid((XY_grid[:, 0], XY_grid[:, 1]), z0_p, x0_p, y0_p, a_p, b_p, h_p).reshape(50, 50)
Zg_rbf = rbf.predict(XY_grid).reshape(50, 50)

def plot_model_surface_and_contour(Xg, Yg, Zg, Xpts, Ypts, Zpts, title, filename):
    """Построение 3D поверхности + линий уровня с точками данных."""
    fig = plt.figure(figsize=(14, 6))
    vmin, vmax = Zg.min(), Zg.max()

    ax1 = fig.add_subplot(121, projection='3d')
    surf = ax1.plot_surface(Xg, Yg, Zg, cmap='viridis', alpha=0.85)
    ax1.scatter(Xpts, Ypts, Zpts, c='red', s=80, edgecolors='black', linewidth=0.5,
                label='Данные (Вариант 11)')
    ax1.set_xlabel('X')
    ax1.set_ylabel('Y')
    ax1.set_zlabel('Z')
    ax1.set_title(f'{title}\n3D-поверхность')
    ax1.legend()

    ax2 = fig.add_subplot(122)
    contour = ax2.contourf(Xg, Yg, Zg, levels=25, cmap='viridis', alpha=0.9, vmin=vmin, vmax=vmax)
    ax2.scatter(Xpts, Ypts, c=Zpts, s=120, edgecolors='black', linewidth=1.5,
                cmap='viridis', vmin=vmin, vmax=vmax)
    ax2.contour(Xg, Yg, Zg, levels=10, colors='white', alpha=0.3, linewidths=0.5)
    for i in range(len(Xpts)):
        ax2.annotate(f'{i}', (Xpts[i], Ypts[i]), textcoords="offset points",
                     xytext=(7, 7), fontsize=10, color='red', fontweight='bold',
                     bbox=dict(boxstyle='round,pad=0.3', facecolor='white', alpha=0.7))
    ax2.set_xlabel('X')
    ax2.set_ylabel('Y')
    ax2.set_title(f'{title}\nЛинии уровня с точками данных')
    ax2.grid(True, alpha=0.3)
    cbar = plt.colorbar(contour, ax=ax2, label='Z')
    cbar.ax.tick_params(labelsize=9)

    plt.tight_layout()
    plt.savefig(os.path.join(save_dir, filename), dpi=300, bbox_inches='tight')
    plt.close()
    print(f"График сохранён: {filename}")

# --- Графики поверхностей ---
plot_model_surface_and_contour(Xg, Yg, Zg_gauss, X, Y, Z,
    'Гауссова модель (Вариант 11)', 'gaussian_model.png')
plot_model_surface_and_contour(Xg, Yg, Zg_parab, X, Y, Z,
    'Эллиптический параболоид (Вариант 11)', 'paraboloid_model.png')
plot_model_surface_and_contour(Xg, Yg, Zg_rbf, X, Y, Z,
    'RBF-сеть (Вариант 11)', 'rbf_model.png')

# --- Кривая обучения: Параболоид ---
fig, ax = plt.subplots(figsize=(9, 5))
iters = list(range(len(parab_loss_hist)))
ax.plot(iters, parab_loss_hist, 'o-', color='#FF9800', markersize=5, linewidth=1.5)
ax.set_yscale('log')
ax.set_xlabel('Номер итерации')
ax.set_ylabel('MSE (логарифмическая шкала)')
ax.set_title('Кривая обучения: Эллиптический параболоид\nВариант 11', fontweight='bold')
ax.grid(True, alpha=0.3)
ax.annotate(f'MSE = {parab_loss_hist[-1]:.6f}',
            xy=(len(parab_loss_hist)-1, parab_loss_hist[-1]),
            xytext=(-80, -20), textcoords="offset points",
            fontsize=10, fontweight='bold', color='#FF9800',
            arrowprops=dict(arrowstyle='->', color='#FF9800'))
plt.tight_layout()
plt.savefig(os.path.join(save_dir, 'paraboloid_learning_curve.png'), dpi=300, bbox_inches='tight')
plt.close()
print("График сохранён: paraboloid_learning_curve.png")

# --- Кривая обучения: RBF-сеть ---
fig, ax = plt.subplots(figsize=(9, 5))
epochs_list = list(range(len(rbf.loss_history)))
ax.plot(epochs_list, rbf.loss_history, '-', color='#4CAF50', linewidth=1.2, label='RBF-сеть')
ax.axhline(y=rbf.loss_history[-1], color='red', linestyle='--', alpha=0.5,
           label=f'Конечный MSE = {rbf.loss_history[-1]:.6f}')
ax.set_yscale('log')
ax.set_xlabel('Номер эпохи')
ax.set_ylabel('MSE (логарифмическая шкала)')
ax.set_title('Кривая обучения: RBF-сеть\nВариант 11', fontweight='bold')
ax.legend()
ax.grid(True, alpha=0.3)
plt.tight_layout()
plt.savefig(os.path.join(save_dir, 'rbf_learning_curve.png'), dpi=300, bbox_inches='tight')
plt.close()
print("График сохранён: rbf_learning_curve.png")

# --- Сравнение MSE всех методов ---
fig, ax = plt.subplots(figsize=(9, 5))
methods = ['Гауссиана', 'Параболоид', 'Конст.\nMSE', 'Конст.\nMAE', 'RBF-сеть']
mse_values = [mse_gauss, mse_parab, mse_const, mse_of_mae_const, mse_rbf]
colors = ['#2196F3', '#FF9800', '#9C27B0', '#E91E63', '#4CAF50']
bars = ax.bar(methods, mse_values, color=colors, alpha=0.85, edgecolor='black', linewidth=1.2)

for bar, val in zip(bars, mse_values):
    if val > 0.01:
        ax.annotate(f'{val:.4f}', xy=(bar.get_x() + bar.get_width()/2, bar.get_height()),
                    xytext=(0, 8), textcoords="offset points", ha='center', va='bottom',
                    fontsize=9, fontweight='bold')
    else:
        ax.annotate(f'{val:.2e}', xy=(bar.get_x() + bar.get_width()/2, max(bar.get_height(), 1e-15)),
                    xytext=(0, 8), textcoords="offset points", ha='center', va='bottom',
                    fontsize=9, fontweight='bold')

ax.set_yscale('log')
ax.set_ylabel('MSE (логарифмическая шкала)')
ax.set_title('Сравнение MSE методов аппроксимации\nВариант 11', fontweight='bold')
ax.grid(True, alpha=0.3, axis='y')
plt.tight_layout()
plt.savefig(os.path.join(save_dir, 'mse_comparison.png'), dpi=300, bbox_inches='tight')
plt.close()
print("График сохранён: mse_comparison.png")

# --- Сравнение абсолютных невязок (без константных) ---
fig, ax = plt.subplots(figsize=(10, 6))
x_labels = [f'{i}' for i in range(len(X))]
x_pos = np.arange(len(X))
width = 0.25

abs_errors = [np.abs(err_gauss), np.abs(err_parab), np.abs(err_rbf)]
labels = ['Гауссиана', 'Параболоид', 'RBF-сеть']
bar_colors = ['#2196F3', '#FF9800', '#4CAF50']

for j, (ae, lbl, clr) in enumerate(zip(abs_errors, labels, bar_colors)):
    offset = (j - 1) * width
    bars = ax.bar(x_pos + offset, ae, width, label=lbl, color=clr, alpha=0.85)
    for bar in bars:
        height = bar.get_height()
        if height > 0.001:
            ax.annotate(f'{height:.3f}', xy=(bar.get_x() + bar.get_width()/2, height),
                        xytext=(0, 3), textcoords="offset points", ha='center', va='bottom', fontsize=7)

ax.set_xlabel('Номер точки')
ax.set_ylabel('Абсолютная невязка $|z_{pred} - z_{true}|$')
ax.set_title('Сравнение абсолютных невязок трёх методов\nВариант 11', fontweight='bold')
ax.set_xticks(x_pos)
ax.set_xticklabels(x_labels)
ax.legend()
ax.grid(True, alpha=0.3, axis='y')
plt.tight_layout()
plt.savefig(os.path.join(save_dir, 'error_comparison.png'), dpi=300, bbox_inches='tight')
plt.close()
print("График сохранён: error_comparison.png")

# --- Сравнение 3D всех трёх моделей ---
fig = plt.figure(figsize=(18, 6))
models_3d = [
    (Zg_gauss, 'Гауссиана', 'viridis'),
    (Zg_parab, 'Эллиптический параболоид', 'plasma'),
    (Zg_rbf, 'RBF-сеть', 'cividis')
]
for idx, (Zg, model_title, cmap) in enumerate(models_3d):
    ax = fig.add_subplot(1, 3, idx+1, projection='3d')
    ax.plot_surface(Xg, Yg, Zg, cmap=cmap, alpha=0.85)
    ax.scatter(X, Y, Z, c='red', s=60, edgecolors='black', linewidth=0.5)
    ax.set_xlabel('X')
    ax.set_ylabel('Y')
    ax.set_zlabel('Z')
    ax.set_title(model_title, fontweight='bold')

plt.suptitle('Сравнение трёх методов аппроксимации — Вариант 11',
             fontsize=14, fontweight='bold', y=1.02)
plt.tight_layout()
plt.savefig(os.path.join(save_dir, 'all_models_3d.png'), dpi=300, bbox_inches='tight')
plt.close()
print("График сохранён: all_models_3d.png")

# --- Константная модель: визуализация ---
fig, ax = plt.subplots(figsize=(9, 5))
x_idx = np.arange(len(X))
ax.axhline(y=const_mse, color='#9C27B0', linestyle='--', linewidth=2,
           label=f'MSE-константа = {const_mse:.4f}')
ax.axhline(y=const_mae, color='#E91E63', linestyle=':', linewidth=2,
           label=f'MAE-константа = {const_mae:.4f}')
ax.scatter(x_idx, Z, c='#2196F3', s=120, zorder=5, edgecolors='black',
           label='Данные (Вариант 11)')
for i, (xi, zi) in enumerate(zip(x_idx, Z)):
    ax.plot([xi, xi], [const_mse, zi], color='#9C27B0', alpha=0.5, linewidth=1.2)
    ax.plot([xi, xi], [const_mae, zi], color='#E91E63', alpha=0.5, linewidth=1.2)

ax.set_xlabel('Номер точки')
ax.set_ylabel('z')
ax.set_title('Аппроксимация константной моделью\nВариант 11', fontweight='bold')
ax.set_xticks(x_idx)
ax.set_xticklabels([f'{i}' for i in range(len(X))])
ax.legend()
ax.grid(True, alpha=0.3)
plt.tight_layout()
plt.savefig(os.path.join(save_dir, 'constant_model.png'), dpi=300, bbox_inches='tight')
plt.close()
print("График сохранён: constant_model.png")

print("\n" + "="*70)
print("ВСЕ ГРАФИКИ ПОСТРОЕНЫ")
print("="*70)
