"""Лабораторная работа 5. Нечётный вариант UCI 856."""

import argparse
import csv
from math import isqrt
from pathlib import Path
from random import Random

import matplotlib

from metrics import curve_points, evaluate, threshold_points, trapezoidal_auc
from tree import entropy, fit, gini, route, walk

matplotlib.use("Agg")
import matplotlib.pyplot as plt

ROOT = Path(__file__).resolve().parents[1]
SPLIT_SEED = 42
FEATURE_SEED = 43


def load_data(path):
    with path.open(encoding="utf-8-sig", newline="") as stream:
        reader = csv.DictReader(stream)
        features = [name for name in reader.fieldnames if name not in ("Student ID", "OUTPUT Grade")]
        rows, labels = [], []
        missing = 0
        for record in reader:
            labels.append(int(int(record["OUTPUT Grade"]) >= 3))
            row = {}
            for name in features:
                value = (record[name] or "").strip()
                if value in ("", "?"):
                    value = "<пропуск>"
                    missing += 1
                row[name] = value
            rows.append(row)
    return rows, labels, features, missing


def stratified_split(labels):
    rng = Random(SPLIT_SEED)
    groups = [[i for i, label in enumerate(labels) if label == c] for c in (0, 1)]
    test_size = round(len(labels) / 5)
    positive_size = round(test_size * len(groups[1]) / len(labels))
    test = []
    for group, count in zip(groups, (test_size - positive_size, positive_size)):
        rng.shuffle(group)
        test.extend(group[:count])
    test_set = set(test)
    return [i for i in range(len(labels)) if i not in test_set], sorted(test)


def write_csv(path, columns, records):
    with path.open("w", encoding="utf-8-sig", newline="") as stream:
        writer = csv.writer(stream)
        writer.writerow(columns)
        writer.writerows(records)


def plot_importance(importance, path):
    names = sorted(importance, key=importance.get)
    fig, ax = plt.subplots(figsize=(7.2, 2.8), layout="constrained")
    values = [importance[name] for name in names]
    bars = ax.barh(names, values, color="#305e85", label="Энтропия")
    ax.bar_label(bars, fmt="%.3f", padding=4)
    ax.set_xlim(0, max(values, default=0) * 1.24 or 1)
    ax.set(xlabel="Сумма информационных выигрышей", ylabel="Признак",
           title="Важность признаков")
    ax.legend(loc="lower right")
    ax.grid(axis="x", alpha=0.2)
    ax.set_axisbelow(True)
    fig.savefig(path, dpi=220)
    plt.close(fig)


def plot_curves(curves, prevalence, path):
    fig, axes = plt.subplots(1, 2, figsize=(7.2, 3.1), layout="constrained")
    for axis, title, xlabel, ylabel in zip(
        axes, ("ROC на тесте", "PR на тесте"), ("FPR", "Recall"), ("TPR", "Precision")
    ):
        axis.set(title=title, xlabel=xlabel, ylabel=ylabel, xlim=(-0.02, 1.02), ylim=(-0.02, 1.03))
        axis.grid(alpha=0.23)
    styles = [("#305e85", "-", "o"), ("#ad4d20", "--", "s")]
    for (name, points), (color, linestyle, marker) in zip(curves.items(), styles):
        for axis, coords in zip(axes, points):
            x, y = zip(*coords)
            axis.plot(x, y, color=color, linestyle=linestyle, marker=marker, ms=2.6,
                      label=f"{name}, AUC={trapezoidal_auc(coords):.3f}")
    axes[0].plot([0, 1], [0, 1], ":", color="#666666", label="Случайный")
    axes[1].axhline(prevalence, linestyle=":", color="#666666", label="Доля класса 1")
    axes[0].legend(loc="lower right", fontsize=8)
    axes[1].legend(loc="lower left", fontsize=8)
    fig.savefig(path, dpi=220)
    plt.close(fig)


def run(data, output):
    rows, labels, names, missing = load_data(data)
    train, test = stratified_split(labels)
    # Одинаковый набор для всего дерева и обоих критериев.
    selected = sorted(Random(FEATURE_SEED).sample(range(len(names)), isqrt(len(names))))
    features = [names[i] for i in selected]
    train_rows, train_y = [rows[i] for i in train], [labels[i] for i in train]
    test_rows, test_y = [rows[i] for i in test], [labels[i] for i in test]

    lines = [f"Объектов: {len(labels)}. Признаков до отбора: {len(names)}. Пропусков: {missing}.",
             f"Seed разбиения: {SPLIT_SEED}. Seed отбора признаков: {FEATURE_SEED}."]
    for split, targets in (("Все данные", labels), ("Обучение", train_y), ("Тест", test_y)):
        lines.append(f"{split}: {len(targets)} объектов, класс 0 — {targets.count(0)}, класс 1 — {targets.count(1)}")
    lines.append("Признаки: " + ", ".join(features))

    output.mkdir(parents=True, exist_ok=True)
    curves = {}
    metrics_records, threshold_records = [], []
    for name, criterion in (("Энтропия", entropy), ("Джини", gini)):
        tree = fit(train_rows, train_y, features, criterion)
        nodes = list(walk(tree))
        leaves = [node.probability for _, _, node in nodes if node.feature is None]
        importance = dict.fromkeys(features, 0.0)
        lines.extend(["", name, f"Глубина: {max(depth for depth, _, _ in nodes)}. Листьев: {len(leaves)}."])
        for depth, branch, node in nodes:
            description = f"n={node.size}, p1={node.probability:.4f}"
            if node.feature is not None:
                importance[node.feature] += node.gain
                description = f"{node.feature} [Δ={node.gain:.5f}, {description}]"
            else:
                description = f"лист [{description}]"
            lines.append(f"{'  ' * depth}{branch} -> {description}")
        lines.append("Суммы выигрышей")
        for feature, gain in sorted(importance.items(), key=lambda item: -item[1]):
            lines.append(f"  {feature}: {gain:.6f}")
        if criterion is entropy:
            plot_importance(importance, output / "importance.png")

        routed = [route(tree, row) for row in test_rows]
        test_scores = [node.probability for node in routed]
        train_scores = [route(tree, row).probability for row in train_rows]
        lines.append(f"Остановок во внутренних узлах на тесте: {sum(node.feature is not None for node in routed)}")
        points = threshold_points(test_y, test_scores, leaves)
        roc, pr = curves[name] = curve_points(points)
        roc_auc, pr_auc = trapezoidal_auc(roc), trapezoidal_auc(pr)
        for split, targets, scores in (("train", train_y, train_scores), ("test", test_y, test_scores)):
            m = evaluate(targets, scores)
            areas = (roc_auc, pr_auc) if split == "test" else ("", "")
            metrics_records.append([name, split, 0.5, m.tp, m.fp, m.tn, m.fn,
                                    m.accuracy, m.precision, m.recall, *areas])
        for (threshold, m), (_, pr_precision) in zip(points, pr):
            threshold_records.append([name, threshold, m.tp, m.fp, m.tn, m.fn,
                                      m.fpr, m.recall, m.precision, pr_precision])

    plot_curves(curves, sum(test_y) / len(test_y), output / "curves.png")
    write_csv(output / "metrics.csv", ("criterion", "split", "threshold", "tp", "fp", "tn", "fn",
                                     "accuracy", "precision", "recall", "roc_auc", "pr_auc"), metrics_records)
    write_csv(output / "thresholds.csv", ("criterion", "threshold", "tp", "fp", "tn", "fn",
                                        "fpr", "recall", "precision", "pr_precision"), threshold_records)
    summary = "\n".join(lines)
    (output / "trees.txt").write_text(summary + "\n", encoding="utf-8")
    print(summary)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--data", type=Path, default=ROOT / "data" / "students.csv")
    parser.add_argument("--output", type=Path, default=ROOT / "results")
    args = parser.parse_args()
    run(args.data, args.output)


if __name__ == "__main__":
    main()
