import numpy as np
import matplotlib.pyplot as plt

e = np.e

# ===== 显示窗口 =====
ZLIM = 20
Z1LIM = 8
WLIM = 8

# ===== 生成笛卡尔网格（点数适中）=====
N = 500
x = np.linspace(-ZLIM, ZLIM, N)
y = np.linspace(-ZLIM, ZLIM, N)
X, Y = np.meshgrid(x, y)
Z = X + 1j*Y

# ===== D1 =====
mask_D1 = np.abs(Z) > e
Z_D1 = Z[mask_D1]


Z1 = Z_D1 / e


Z2 = Z1**2

W = np.log(Z2) / np.pi
W1 = (-2) / W

# ===== Step 4 =====
#Wf = W[(W.real > 0) & (np.abs(W-1) > 1)]
Wf = W1

# ===== 作图 =====
fig, axs = plt.subplots(2, 2, figsize=(12, 12))
s = 0.6

axs[0,0].scatter(Z_D1.real, Z_D1.imag, s=s)
axs[0,0].set_title(r"$D_1:\ |z|>e$")
axs[0,0].set_xlim(-ZLIM, ZLIM)
axs[0,0].set_ylim(-ZLIM, ZLIM)

axs[0,1].scatter(Z1.real, Z1.imag, s=s)
axs[0,1].set_title(r"$z_1=z/e$")
axs[0,1].set_xlim(-Z1LIM, Z1LIM)
axs[0,1].set_ylim(-Z1LIM, Z1LIM)

axs[1,0].scatter(Z2.real, Z2.imag, s=s)
axs[1,0].set_title(r"$z_2:\ {z_1}^2$")
axs[1,0].set_xlim(-Z1LIM, Z1LIM)
axs[1,0].set_ylim(0, Z1LIM)

axs[1,1].scatter(Wf.real, Wf.imag, s=s)
axs[1,1].set_title(r"$D_2$")
axs[1,1].set_xlim(0, WLIM)
axs[1,1].set_ylim(0, WLIM)

for ax in axs.flat:
    ax.set_aspect("equal")
    ax.axhline(0, linewidth=0.4, color='black')
    ax.axvline(0, linewidth=0.4, color='black')

plt.tight_layout()
plt.show()
