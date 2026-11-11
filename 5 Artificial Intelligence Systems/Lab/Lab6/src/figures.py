"""Write the figures and external predictions used in the report."""

import csv
from itertools import groupby
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from PIL import Image, ImageOps

from inference import preprocess_image
from network import softmax


def save_figure(figure, path):
    figure.savefig(path, dpi=190, bbox_inches="tight", facecolor="white")
    plt.close(figure)


def plot_curves(folder, history):
    for name, group in groupby(history, key=lambda row: row[0]):
        _, epochs, train_loss, train_acc, val_loss, val_acc = zip(*group)
        figure, axes = plt.subplots(1, 2, figsize=(8.0, 2.7), layout="constrained")
        for axis, train, val, label in (
            (axes[0], train_loss, val_loss, "Кросс-энтропия"),
            (axes[1], np.array(train_acc) * 100, np.array(val_acc) * 100, "Точность, %"),
        ):
            axis.plot(epochs, train, marker=".", label="train", color="#285aa2")
            axis.plot(epochs, val, marker=".", label="val", color="#bd5728")
            axis.set(xlabel="Эпоха", ylabel=label, title=f"Модель {name} · {label}")
            axis.set_xticks(epochs[::2])
            axis.grid(alpha=0.25)
            axis.legend()
        save_figure(figure, folder / f"learning_{name}.png")


def plot_examples(folder, images, labels, test_x, test_labels, predictions, confusion):
    figure, axes = plt.subplots(5, 5, figsize=(4.3, 4.7), layout="constrained")
    figure.suptitle("Примеры из исходной обучающей выборки")
    for index, axis in enumerate(axes.flat):
        axis.imshow(images[index], cmap="gray", vmin=0, vmax=1)
        axis.set_title(str(labels[index]), fontsize=10)
        axis.axis("off")
    save_figure(figure, folder / "mnist_samples.png")

    figure, axis = plt.subplots(figsize=(5.5, 4.3), layout="constrained")
    colors = axis.imshow(np.log1p(confusion), cmap="Blues")
    for (row, column), count in np.ndenumerate(confusion):
        axis.text(column, row, str(count), ha="center", va="center", fontsize=8,
                  color="white" if count > 100 else "#161616")
    axis.set(xticks=range(10), yticks=range(10), xlabel="Предсказанный класс",
             ylabel="Истинный класс", title="Матрица ошибок на тесте MNIST")
    figure.colorbar(colors, ax=axis, label="ln(1 + число объектов)")
    save_figure(figure, folder / "confusion_matrix.png")

    # Pick two examples of each of the three largest directed confusions.
    off_diagonal = confusion.copy()
    np.fill_diagonal(off_diagonal, 0)
    pairs = np.argsort(-off_diagonal.ravel(), kind="stable")[:3]
    examples = []
    for pair in pairs:
        true, predicted = divmod(int(pair), 10)
        indexes = np.flatnonzero((test_labels == true) & (predictions == predicted))
        examples.extend(indexes[:2])
    figure, axes = plt.subplots(1, 6, figsize=(8.0, 1.9), layout="constrained")
    figure.suptitle("Ошибки теста · истинный класс → прогноз")
    for axis, index in zip(axes, examples):
        axis.imshow(test_x[index], cmap="gray", vmin=0, vmax=1)
        axis.set_title(f"{test_labels[index]} → {predictions[index]}\nIDX {index}", fontsize=9)
        axis.axis("off")
    for axis in axes[len(examples):]:
        axis.axis("off")
    save_figure(figure, folder / "test_errors.png")


def plot_drawings(folder, model):
    drawings = sorted((Path(__file__).resolve().parents[1] / "data/drawings").glob("*.png"))
    figure, axes = plt.subplots(len(drawings), 3, figsize=(6.0, 5.5),
                                squeeze=False, layout="constrained")
    figure.suptitle("Распознавание внешних рисунков")
    rows = []
    for (original_axis, direct_axis, prepared_axis), path in zip(axes, drawings):
        with Image.open(path) as original:
            gray = original.convert("L")
            original_axis.imshow(gray, cmap="gray", vmin=0, vmax=255)
        raw = np.asarray(gray, dtype=np.float32)
        border = np.concatenate((raw[0], raw[-1], raw[1:-1, 0], raw[1:-1, -1]))
        background = np.median(border)
        if background - raw.min() > raw.max() - background:
            gray = ImageOps.invert(gray)
        direct = np.asarray(gray.resize((28, 28), Image.Resampling.LANCZOS),
                            dtype=np.float32) / 255.0
        prepared = preprocess_image(path)
        direct_prob, prob = softmax(model.forward(np.stack((direct, prepared))))
        direct_digit, digit = int(direct_prob.argmax()), int(prob.argmax())
        true = int(path.stem)
        rows.append((path.name, true, direct_digit, float(direct_prob[direct_digit]),
                     digit, *map(float, prob)))
        original_axis.set_title(f"Исходная цифра {true}", fontsize=9)
        for axis, image, prediction, confidence, label in (
            (direct_axis, direct, direct_digit, direct_prob[direct_digit], "Прямой ресайз"),
            (prepared_axis, prepared, digit, prob[digit], "Полная обработка"),
        ):
            axis.imshow(image, cmap="gray", vmin=0, vmax=1)
            axis.set_title(f"{label}\n{prediction} · {confidence:.2%}", fontsize=9)
        for axis in (original_axis, direct_axis, prepared_axis):
            axis.axis("off")
    save_figure(figure, folder / "external_drawings.png")
    with (folder / "external_predictions.csv").open("w", encoding="utf-8", newline="") as file:
        writer = csv.writer(file)
        writer.writerow(("file", "true", "direct_prediction", "direct_probability",
                         "prediction", *(f"p_{digit}" for digit in range(10))))
        writer.writerows(rows)


def plot_results(folder, history, images, labels, test_x, test_labels, predictions, confusion, model):
    plot_curves(folder, history)
    plot_examples(folder, images, labels, test_x, test_labels, predictions, confusion)
    plot_drawings(folder, model)
