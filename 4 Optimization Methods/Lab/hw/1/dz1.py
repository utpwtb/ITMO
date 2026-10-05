import numpy as np
import matplotlib.pyplot as plt

plt.rc('font', size=12)


def f(x):
    return 1.0 / x + np.exp(x)


def df(x):
    return -1.0 / (x * x) + np.exp(x)


def cubic_approximation(a, b, eps=0.0001, max_iter=100):
    history = []

    fa, fpa = f(a), df(a)
    fb, fpb = f(b), df(b)

    history.append((a, fa, fpa, b, fb, fpb))

    for it in range(max_iter):
        h = b - a

        s = (fb - fa) / h

        A = (3 * s - fpb - 2 * fpa) / h
        B = (fpb + fpa - 2 * s) / h

        disc = A * A - 3 * fpa * B / h

        if disc < 0:
            disc = 0.0

        if abs(B) < 1e-12:
            t = -fpa * h / (2 * A * h + 1e-12)
        else:
            t = (-A + np.sqrt(disc)) * h / (3 * B)
            if t <= 0.0 or t >= h:
                t = (-A - np.sqrt(disc)) * h / (3 * B)

        t = np.clip(t, 0.01 * h, 0.99 * h)

        x_new = a + t
        fx_new = f(x_new)
        fpx_new = df(x_new)

        history.append((a, fa, fpa, b, fb, fpb, x_new, fx_new, fpx_new))

        if abs(fpx_new) < eps:
            break

        if fpx_new < 0:
            a, fa, fpa = x_new, fx_new, fpx_new
        else:
            b, fb, fpb = x_new, fx_new, fpx_new

    return x_new, fx_new, history


def build_cubic(x1, f1, fp1, x2, f2, fp2):
    h = x2 - x1

    s = (f2 - f1) / h
    A = (3 * s - fp2 - 2 * fp1) / h
    B = (fp2 + fp1 - 2 * s) / h

    def cubic(x):
        t = x - x1
        return f1 + fp1 * t + A * t * t + B * t * t * t / h

    return cubic


def run():
    a, b = 0.5, 1.5
    eps = 0.0001

    print("=" * 60)
    print("ДЗ1.1: Метод кубической аппроксимации")
    print(f"f(x) = 1/x + e^x,  [{a}, {b}],  eps = {eps}")
    print("=" * 60)

    x_min, f_min, history = cubic_approximation(a, b, eps)

    print(f"\nТочка минимума:  x* = {x_min:.8f}")
    print(f"Значение в минимуме:  f(x*) = {f_min:.8f}")
    print(f"Производная в минимуме:  f'(x*) = {df(x_min):.2e}")
    print(f"Число итераций:  {len(history) - 1}")

    print("\nИстория итераций:")
    print(f"{'Итер.':>5}  {'a':>10}  {'b':>10}  {'x_new':>10}  {'f(x_new)':>12}  {'f\'(x_new)':>12}")
    for k, entry in enumerate(history):
        if len(entry) == 6:
            a_i, fa_i, fpa_i, b_i, fb_i, fpb_i = entry
            print(f"{'нач.':>5}  {a_i:10.6f}  {b_i:10.6f}  {'---':>10}  {'---':>12}  {'---':>12}")
        else:
            a_i, fa_i, fpa_i, b_i, fb_i, fpb_i, xn, fxn, fpxn = entry
            print(f"{k:>5}  {a_i:10.6f}  {b_i:10.6f}  {xn:10.6f}  {fxn:12.8f}  {fpxn:12.2e}")

    iter_list = [1, 3, len(history) - 1]
    for idx in iter_list:
        if idx < len(history) and len(history[idx]) == 9:
            plot_iteration(a, b, history, idx)
        elif idx >= len(history):
            plot_iteration(a, b, history, len(history) - 1)


def plot_iteration(a_orig, b_orig, history, iter_idx):
    entry = history[iter_idx]
    a_i, fa_i, fpa_i, b_i, fb_i, fpb_i, xn, fxn, fpxn = entry

    cubic = build_cubic(a_i, fa_i, fpa_i, b_i, fb_i, fpb_i)

    x_plot = np.linspace(a_orig - 0.1, b_orig + 0.1, 500)
    y_orig = f(x_plot)
    y_cubic = np.array([cubic(x) for x in x_plot])

    fig, ax = plt.subplots(figsize=(9, 6))
    ax.plot(x_plot, y_orig, 'b-', linewidth=2, label='f(x) = 1/x + eˣ')
    ax.plot(x_plot, y_cubic, 'r--', linewidth=1.8,
            label=f'кубическая аппроксимация (итер. {iter_idx})')

    ax.scatter([a_i, b_i], [fa_i, fb_i], c='green', s=70, zorder=5,
               label=f'границы [{a_i:.4f}, {b_i:.4f}]')
    ax.scatter([xn], [fxn], c='darkorange', s=90, zorder=5,
               marker='*', label=f'новое приближение x={xn:.5f}')

    ax.set_xlabel('x')
    ax.set_ylabel('f(x)')
    ax.set_title(f'ДЗ1.2: Итерация {iter_idx} метода кубической аппроксимации')
    ax.legend(fontsize=10)
    ax.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.savefig(f'iteration_{iter_idx}.png', dpi=150)
    plt.show()
    print(f"  -> Сохранён рисунок iteration_{iter_idx}.png")


if __name__ == '__main__':
    run()
