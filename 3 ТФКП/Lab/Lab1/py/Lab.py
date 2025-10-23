import numpy as np
import matplotlib.pyplot as plt
import matplotlib
matplotlib.use('TkAgg')

plt.ion()
iter_func = lambda z, c: (z ** 2 + c)

def calc_steps(c, max_iter_num=128):
    z = complex(0, 0)
    num = 0
    while num < max_iter_num and abs(z) < 2:
        z = iter_func(z,c)
        num += 1
    return num

def display_mandelbrot(x_num = 1000, y_num = 1000):
    X, Y = np.meshgrid(np.linspace(-2, 2, x_num + 1), np.linspace(-2, 2, y_num + 1))
    C = X + Y *1j
    result = np.zeros((y_num + 1, x_num + 1))
    for i in range(y_num + 1):
        for j in range(x_num + 1):
            result[i, j] = calc_steps(C[i, j])

    plt.imshow(result, interpolation="bilinear", cmap = plt.cm.hot,
               vmax = abs(result).max(), vmin = abs(result).min(),
               extent = [-2, 2, -2, 2])
    plt.tight_layout()
    plt.show()

if __name__ == '__main__':
    display_mandelbrot(2000, 2000)