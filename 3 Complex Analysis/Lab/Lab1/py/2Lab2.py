import numpy as np
import matplotlib.pyplot as plt

e = np.e

# ===== 显示窗口 =====
ZLIM = 20
Z1LIM = 8
Z2LIM = 4

# ===== 生成网格 =====
N = 500
x = np.linspace(-ZLIM, ZLIM, N)
y = np.linspace(-ZLIM, ZLIM, N)
X, Y = np.meshgrid(x, y)
Z = X + 1j * Y

# ===== 初始区域 D1 =====
mask_D1 = np.abs(Z) > e
Z_D1 = Z[mask_D1]

# ===== Step 1: z1 = z / e =====
Z1 = Z_D1 / e

# ===== Step 2: z2 = sqrt(z1)（主值，四象限）=====
Z2 = np.sqrt(Z1)

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
axs[2].set_title(r"$z_2 = \sqrt{z_1}$ (principal branch)")
axs[2].set_xlim(-Z2LIM, Z2LIM)
axs[2].set_ylim(-Z2LIM, Z2LIM)

for ax in axs:
    ax.set_aspect("equal")
    ax.axhline(0, linewidth=0.4, color="black")
    ax.axvline(0, linewidth=0.4, color="black")

plt.tight_layout()
plt.show()
