"""Демонстрация генерации и расчёта характеристик для защиты УИР 1."""
from pathlib import Path
from statistics import NormalDist
import math
import numpy as np

DATA = Path(__file__).resolve().parents[2] / "data" / "measurements.csv"
SIZES = (10, 20, 50, 100, 200, 300)
PROBABILITIES = (0.90, 0.95, 0.99)


def parameters(mean, variance):
    a = (mean - math.sqrt((3 * variance - mean**2) / 2)) / 3
    b = mean - 2 * a
    return a, b


def generate(a, b, size, seed):
    u = np.random.default_rng(seed).random((size, 3))
    return (-np.log1p(-u) * np.array([a, a, b])).sum(axis=1)


def characteristics(values):
    n = len(values)
    mean = float(np.mean(values))
    variance = float(np.var(values, ddof=1))
    std = math.sqrt(variance)
    halfwidths = [NormalDist().inv_cdf((1 + p) / 2) * std / math.sqrt(n)
                  for p in PROBABILITIES]
    return mean, variance, std, std / mean, *halfwidths


def lag_correlation(values, lag):
    return float(np.corrcoef(values[:-lag], values[lag:])[0, 1])


def main():
    original = np.loadtxt(DATA, delimiter=",", skiprows=1)[:, 1]
    assert len(original) == 300
    mean, variance = characteristics(original)[:2]
    a, b = parameters(mean, variance)
    generated = generate(a, b, len(original), seed=263)

    table_original = [characteristics(original[:n]) for n in SIZES]
    table_generated = [characteristics(generated[:n]) for n in SIZES]
    acf_original = [lag_correlation(original, k) for k in range(1, 11)]
    acf_generated = [lag_correlation(generated, k) for k in range(1, 11)]
    boundaries = np.linspace(0, max(original.max(), generated.max()), 11)
    frequencies_original, _ = np.histogram(original, bins=boundaries)
    frequencies_generated, _ = np.histogram(generated, bins=boundaries)
    correlation = float(np.corrcoef(original, generated)[0, 1])

    print(f"a = {a:.6f}; b = {b:.6f}")
    print("Первые 5 сгенерированных значений:",
          np.round(generated[:5], 3))
    for name, row in (("Исходная", table_original[-1]),
                      ("Сгенерированная", table_generated[-1])):
        print(f"{name}: m={row[0]:.3f}; D={row[1]:.3f}; "
              f"s={row[2]:.3f}; v={row[3]:.4f}; "
              f"eps=({row[4]:.3f}, {row[5]:.3f}, {row[6]:.3f})")
    print(f"r_x(1)={acf_original[0]:.4f}; "
          f"r_y(1)={acf_generated[0]:.4f}; r_xy={correlation:.4f}")
    print("Частоты:", frequencies_original.sum(),
          frequencies_generated.sum())


if __name__ == "__main__":
    main()
