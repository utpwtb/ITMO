import matplotlib.pyplot as plt
import numpy as np

plt.rcParams['font.family'] = 'Arial'
plt.rcParams['mathtext.fontset'] = 'stix'

# ============================================================
# Data
# ============================================================
R_M_all = np.array([0, 10, 20, 30, 40, 50, 60, 70, 80, 90, 100, 200, 300, 400])
lam_all = np.array([0.2590, 0.3051, 0.3220, 0.3466, 0.3806, 0.4122, 0.4631,
                    0.4176, 0.5229, 0.5438, 0.5682, 0.8498, 0.7408, 1.0397])

R_M = R_M_all[:11]
lam = lam_all[:11]

coeffs = np.polyfit(R_M, lam, 1)
k, b = coeffs[0], coeffs[1]
R_M_intercept = -b / k
R0 = -R_M_intercept
print(f"Fit: lambda = {k:.5f} * R_M + {b:.4f}, R0 = {R0:.1f} Ohm")

R_full = R_M + R0
Q_vals = np.array([15.5, 13.8, 13.2, 12.6, 11.8, 11.2, 10.4,
                   11.1, 9.7, 9.5, 9.3])

C_vals = np.array([0.022, 0.033, 0.047, 0.47])
T_exp = np.array([460, 560, 660, 2150])

L_thomson = T_exp**2 / (4 * np.pi**2 * C_vals) * 1e-3  # mH
L_T = np.mean(L_thomson)
print(f"L from Thomson (mH): {L_thomson}, average = {L_T:.0f}")

# ============================================================
# Figure 1: lambda vs R_M
# ============================================================
fig1, ax1 = plt.subplots(figsize=(8, 5))

ax1.scatter(R_M, lam, color='blue', s=36, zorder=5, label='Эксперимент')
R_M_fit = np.linspace(0, 105, 50)
ax1.plot(R_M_fit, k * R_M_fit + b, 'r-', linewidth=1.5, label='Аппроксимация')
# Show R0 as extrapolation: dashed line from x=0 down to intercept
ax1.annotate(f'$R_0 \\approx {R0:.0f}$ Ом\n(экстраполяция)',
             xy=(5, 0.05), fontsize=10, color='red',
             bbox=dict(boxstyle='round,pad=0.3', facecolor='white', edgecolor='red', alpha=0.8))

ax1.set_xlabel('$R_\\mathrm{М}$, Ом', fontsize=13)
ax1.set_ylabel('$\\lambda$', fontsize=13)
ax1.set_title('Зависимость $\\lambda(R_\\mathrm{М})$', fontsize=13)
ax1.legend(fontsize=11, loc='upper left')
ax1.grid(True, alpha=0.4)
ax1.set_xlim(0, 108)
ax1.set_ylim(0.22, 0.62)

fig1.tight_layout()
fig1.savefig('pic/lambda_vs_Rm.png', dpi=200)
print("Saved lambda_vs_Rm.png")

# ============================================================
# Figure 2: Q vs R  (smooth theoretical curve)
# ============================================================
fig2, ax2 = plt.subplots(figsize=(8, 5))

# Experimental points
ax2.scatter(R_full, Q_vals, color='blue', s=36, zorder=5, label='Эксперимент')

# Smooth theoretical curve: Q = 2*pi / (1 - exp(-2*lambda))
# where lambda = k * (R - R0) + b = k * (R - R0) + b ... no, lambda = k*R_M + b
# and R = R_M + R0, so R_M = R - R0
# lambda(R) = k*(R - R0) + b = k*R - k*R0 + b
# Since b = -k*R_M_intercept and R0 = -R_M_intercept, k*R0 = -k*R_M_intercept = b
# So lambda(R) = k*R - b + b = k*R. Wait:
# lambda = k*R_M + b = k*(R - R0) + b = k*R - k*R0 + b
# R0 = -R_M_intercept = b/k, so k*R0 = b
# lambda(R) = k*R - b + b = k*R
# That's the small-damping approximation! Let me just use the data directly.

R_smooth = np.linspace(80, 195, 100)
lam_smooth = k * (R_smooth - R0) + b  # since R_M = R - R0
Q_smooth = 2 * np.pi / (1 - np.exp(-2 * lam_smooth))

ax2.plot(R_smooth, Q_smooth, 'r-', linewidth=1.5,
         label='$Q = 2\\pi / (1 - e^{-2\\lambda(R)})$')

ax2.set_xlabel('$R = R_\\mathrm{М} + R_0$, Ом', fontsize=13)
ax2.set_ylabel('$Q$', fontsize=13)
ax2.set_title('Зависимость $Q(R)$', fontsize=13)
ax2.legend(fontsize=11)
ax2.grid(True, alpha=0.4)
ax2.set_xlim(80, 195)
ax2.set_ylim(8, 17)

fig2.tight_layout()
fig2.savefig('pic/Q_vs_R.png', dpi=200)
print("Saved Q_vs_R.png")

# ============================================================
# Figure 3: T vs C
# ============================================================
fig3, ax3 = plt.subplots(figsize=(8, 5))

ax3.scatter(C_vals, T_exp, color='blue', s=49, zorder=5, label='$T_\\mathrm{эксп}$')

C_smooth = np.linspace(0.015, 0.5, 200)
T_thomson = 2 * np.pi * np.sqrt(L_T * 1e-3 * C_smooth * 1e-6) * 1e6
ax3.plot(C_smooth, T_thomson, 'g-', linewidth=1.8, alpha=0.7,
         label='$T = 2\\pi\\sqrt{L_T C}$')

for i, lbl in enumerate(['$C_1$', '$C_2$', '$C_3$', '$C_4$']):
    ax3.annotate(lbl, (C_vals[i], T_exp[i]),
                 textcoords="offset points", xytext=(10, 5), fontsize=10)

ax3.set_xlabel('$C$, мкФ', fontsize=13)
ax3.set_ylabel('$T$, мкс', fontsize=13)
ax3.set_title('Зависимость $T(C)$', fontsize=13)
ax3.legend(fontsize=10, loc='upper left')
ax3.grid(True, alpha=0.4)
ax3.set_xlim(0, 0.52)
ax3.set_ylim(0, 2400)

fig3.tight_layout()
fig3.savefig('pic/T_vs_C.png', dpi=200)
print("Saved T_vs_C.png")

print("\nDone.")
