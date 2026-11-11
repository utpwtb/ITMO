"""Figures used in the experiment report."""

import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt
from matplotlib.patches import Patch
import numpy as np


def save(fig, output):
    fig.savefig(output, bbox_inches="tight")
    plt.close(fig)


def distributions(data, title, output, class_counts=None):
    """Display each variable on its own raw measurement scale."""
    with_class_counts = class_counts is not None
    panel_count = len(data) + int(with_class_counts)
    columns = 5 if with_class_counts else 4
    rows = (panel_count + columns - 1) // columns
    fig, axes = plt.subplots(rows, columns, figsize=(11, 1.95 * rows))
    fig.subplots_adjust(
        left=0.07, right=0.99, bottom=0.16, top=0.88, hspace=0.85, wspace=0.48,
    )
    fig.suptitle(title, fontsize=15)
    panels = axes.flat
    for (name, values), ax in zip(data.items(), panels):
        ax.hist(values, bins="auto", color="#306b9a", edgecolor="white")
        label = "OD280/OD315" if name == "od280/od315_of_diluted_wines" else name
        ax.set_xlabel(label, fontsize=9)
        ax.set_ylabel("Частота", fontsize=8)
        ax.locator_params(axis="x", nbins=4)
        ax.tick_params(labelsize=8)
    legend = [Patch(color="#306b9a", label="Распределение числовой переменной")]
    if with_class_counts:
        ax = next(panels)
        labels, counts = class_counts
        ax.bar(labels, counts, color="#a34e27", width=0.62)
        ax.set_xticks(labels)
        ax.set_xlabel("Класс вина", fontsize=9)
        ax.set_ylabel("Частота", fontsize=8)
        ax.tick_params(labelsize=8)
        legend.append(Patch(color="#a34e27", label="Число объектов класса"))
    for ax in panels:
        ax.set_axis_off()
    fig.legend(handles=legend, loc="lower center", ncol=len(legend), frameon=False)
    save(fig, output)


def validation_curves(records, distances, score, ylabel, title, output):
    fig, ax = plt.subplots(figsize=(7.6, 3.7), layout="constrained")
    styles = (("#306b9a", "o", "-"), ("#a34e27", "s", "--"), ("#2c795a", "^", "-."))
    for distance, (color, marker, line) in zip(distances, styles):
        series = [record for record in records if record["distance"] == distance]
        k = [record["k"] for record in series]
        ax.plot(k, [record[score] for record in series],
                color=color, marker=marker, linestyle=line, label=distance)
    ax.set(title=title, xlabel="Число соседей k", ylabel=ylabel, xticks=k)
    ax.grid(alpha=0.25)
    ax.legend(title="Расстояние", frameon=False)
    save(fig, output)


def confusion_plot(labels, matrix, output):
    fig, ax = plt.subplots(figsize=(4.6, 3.7), layout="constrained")
    cells = ax.imshow(matrix, cmap="Blues", vmin=0)
    fig.colorbar(cells, ax=ax, label="Число объектов")
    for (row, col), count in np.ndenumerate(matrix):
        color = "white" if count > matrix.max() / 2 else "#162b3b"
        ax.text(col, row, str(count), ha="center", va="center", color=color)
    ax.set(title="Wine — матрица ошибок на тесте",
           xlabel="Предсказанный класс", ylabel="Фактический класс",
           xticks=range(len(labels)), yticks=range(len(labels)),
           xticklabels=labels, yticklabels=labels)
    save(fig, output)


def regression_plot(actual, predicted, output):
    fig, ax = plt.subplots(figsize=(5.3, 4.4), layout="constrained")
    low = min(actual.min(), predicted.min()) - 10
    high = max(actual.max(), predicted.max()) + 10
    ax.plot([low, high], [low, high], "--", color="#4b5260",
            label="Точное совпадение")
    ax.scatter(actual, predicted, s=26, alpha=0.75, color="#306b9a",
               label="Тестовый объект")
    ax.set(title="Diabetes — прогнозы на тесте",
           xlabel="Фактическое значение", ylabel="Предсказанное значение",
           xlim=(low, high), ylim=(low, high), aspect="equal")
    ax.grid(alpha=0.25)
    ax.legend(loc="upper left", frameon=False)
    save(fig, output)
