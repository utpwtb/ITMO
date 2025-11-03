import numpy as np
import matplotlib.pyplot as plt
import matplotlib
matplotlib.use('TkAgg')

def julia(h, w, maxit=100, c=0 + 0j):

    y, x = np.ogrid[-1.5:1.5:h * 1j, -1.5:1.5:w * 1j]
    z = x + y * 1j

    divtime = maxit + np.zeros(z.shape, dtype=int)

    for i in range(maxit):
        z = z ** 2 + c
        diverge = z * np.conj(z) > 2 ** 2
        div_now = diverge & (divtime == maxit)
        divtime[div_now] = i
        z[diverge] = 2

    return divtime

plt.imshow(julia(5000, 5000, maxit=100, c=-0.5251993 + 0.5251993j))
plt.title("Julia Set c = -0.5251993 + 0.5251993j")
plt.show()