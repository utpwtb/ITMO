import numpy as np
import matplotlib.pyplot as plt

e = np.e

# ===== 显示窗口 =====
ZLIM = 20
Z1LIM = 8
Z2LIM = 4

# ===== 生成笛卡尔网格 =====
N = 600
x = np.linspace(-ZLIM, ZLIM, N)
y = np.linspace(-ZLIM, ZLIM, N)
X, Y = np.meshgrid(x, y)
Z = X + 1j * Y

# ===== 初始区域 D1: |z| > e =====
mask_D1 = np.abs(Z) > e
Z_D1 = Z[mask_D1]

# ===== Step 1: z1 = z / e =====
Z1 = Z_D1 / e

# ===== Step 2 (教材方式): sqrt(z1) → 上半平面 =====

# (1) 沿正实轴作割线
cut_mask = ~((np.abs(Z1.imag) < 1e-6) & (Z1.real >= 0))
Z1_cut = Z1[cut_mask]

# (2) 极坐标
r = np.abs(Z1_cut)
theta = np.angle(Z1_cut)          # (-π, π]

# (3) 选教材分支：arg ∈ (0, 2π)
theta = np.where(theta <= 0, theta + 2*np.pi, theta)

# (4) 平方根
Z2 = np.sqrt(r) * np.exp(1j * theta / 2)

# ===== 作图 =====
fig, axs = plt.subplots(1, 3, figsize=(15, 5))
s = 0.6

axs[0].scatter(Z_D1.real, Z_D1.imag, s=s)
axs[0].set_title(r"$D_1:\ |z|>e$")
axs[0].set_xlim(-ZLIM, ZLIM)
axs[0].set_ylim(-ZLIM, ZLIM)

axs[1].scatter(Z1.real, Z1.imag, s=s)
axs[1].set_title(r"$z_1 = z/e$")
axs[1].set_xlim(-Z1LIM, Z1LIM)
axs[1].set_ylim(-Z1LIM, Z1LIM)

axs[2].scatter(Z2.real, Z2.imag, s=s)
axs[2].set_title(r"$z_2=\sqrt{z_1},\ \Im z_2>0$")
axs[2].set_xlim(-Z2LIM, Z2LIM)
axs[2].set_ylim(0, Z2LIM)

for ax in axs:
    ax.set_aspect("equal")
    ax.axhline(0, linewidth=0.4, color="black")
    ax.axvline(0, linewidth=0.4, color="black")

plt.tight_layout()
plt.show()
