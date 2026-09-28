"""Генератор гипоэкспоненциального распределения: две стадии a и стадия b."""
import argparse
import math
import numpy as np


def fit(mean, variance):
    """Три стадии применимы при 1/3 <= variance/mean**2 < 1."""
    c2 = variance / mean**2
    if not 1 / 3 <= c2 < 1:
        raise ValueError("Для этой параметризации требуется 1/3 <= CV^2 < 1")
    a = (mean - math.sqrt((3 * variance - mean**2) / 2)) / 3
    return a, mean - 2 * a


def generate(mean, variance, size=300, seed=263):
    a, b = fit(mean, variance)
    rng = np.random.default_rng(seed)
    u = rng.random((size, 3))
    # 1-U лежит в (0,1]; log1p обеспечивает устойчивое вычисление.
    return (-np.log1p(-u) * np.array([a, a, b])).sum(axis=1)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--mean", type=float, default=276.47820235696366)
    parser.add_argument("--variance", type=float, default=29298.17305090093)
    parser.add_argument("--n", type=int, default=300)
    parser.add_argument("--seed", type=int, default=263)
    args = parser.parse_args()
    if args.n < 2:
        parser.error("n должно быть не меньше 2")
    y = generate(args.mean, args.variance, args.n, args.seed)
    print("First 10:", y[:10])
    print("n, mean, variance, std, CV:", len(y), y.mean(), y.var(ddof=1),
          y.std(ddof=1), y.std(ddof=1) / y.mean())
