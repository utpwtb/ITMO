import numpy as np
import matplotlib.pyplot as plt

# 定义网格
x = np.linspace(-2, 2, 400)
y = np.linspace(-2, 2, 400)
X, Y = np.meshgrid(x, y)

# ========== 方程组1 ==========
# x + sin(y) = -0.4
F1 = X + np.sin(Y) + 0.4

# 2y - cos(x + 1) = 0
F2 = 2*Y - np.cos(X + 1)

plt.figure()
plt.contour(X, Y, F1, levels=[0])
plt.contour(X, Y, F2, levels=[0])
plt.title("System 1")
plt.xlabel("x")
plt.ylabel("y")
plt.grid()

# ========== 方程组2 ==========
# sin(y) + 2x = 2
F3 = np.sin(Y) + 2*X - 2

# y + cos(x - 1) = 0.7
F4 = Y + np.cos(X - 1) - 0.7

plt.figure()
plt.contour(X, Y, F3, levels=[0])
plt.contour(X, Y, F4, levels=[0])
plt.title("System 2")
plt.xlabel("x")
plt.ylabel("y")
plt.grid()

# ========== 方程组3 ==========
# sin(x + y) - 1.4x = 0
F5 = np.sin(X + Y) - 1.4*X

# x^2 + y^2 = 1
F6 = X**2 + Y**2 - 1

plt.figure()
plt.contour(X, Y, F5, levels=[0])
plt.contour(X, Y, F6, levels=[0])
plt.title("System 3")
plt.xlabel("x")
plt.ylabel("y")
plt.grid()

plt.show()