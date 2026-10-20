"""Create portable SVG charts with the standard library, NumPy and Pandas."""

from html import escape

import numpy as np
import pandas as pd

COLORS = ["#246b91", "#d17a27", "#35947d", "#915a9e"]


class Chart:
    def __init__(self, width, height, title):
        self.width, self.height = width, height
        self.parts = []
        self.rect(0, 0, width, height, "white")
        self.text(24, 30, title, size=19)

    def text(self, x, y, value, size=12, color="#223344", anchor="start"):
        self.parts.append(
            f'<text x="{x}" y="{y}" font-size="{size}" fill="{color}" text-anchor="{anchor}" font-family="sans-serif">{escape(str(value))}</text>'
        )

    def rect(self, x, y, width, height, color):
        self.parts.append(
            f'<rect x="{x}" y="{y}" width="{width}" height="{height}" fill="{color}"/>'
        )

    def line(self, x1, y1, x2, y2, color="#d4dce3", width=1):
        self.parts.append(
            f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="{color}" stroke-width="{width}"/>'
        )

    def path(self, xs, ys, color, width=2):
        points = " ".join(f"{x:.3f},{y:.3f}" for x, y in zip(xs, ys))
        self.parts.append(
            f'<polyline points="{points}" fill="none" stroke="{color}" stroke-width="{width}"/>'
        )

    def save(self, path):
        path.write_text(
            f'<svg xmlns="http://www.w3.org/2000/svg" width="{self.width}" height="{self.height}" viewBox="0 0 {self.width} {self.height}">'
            + "".join(self.parts)
            + "</svg>",
            encoding="utf-8",
        )


def numeric_summary(frame, folder):
    columns = ["Age", "Fare", "SibSp", "Parch", "Pclass", "Survived"]
    chart = Chart(960, 580, "Числовые признаки: описательная статистика")
    for index, column in enumerate(columns):
        x, y = 35 + (index % 2) * 475, 65 + (index // 2) * 170
        stats = frame[column].describe()
        chart.text(
            x,
            y,
            f"{column}: n={stats['count']:.0f}; среднее={stats['mean']:.2f}; σ={stats['std']:.2f}",
            size=13,
        )
        maximum = max(float(stats["max"]), 1)

        def scale(value):
            return x + 20 + float(value) / maximum * 395

        level = y + 53
        chart.line(scale(stats["min"]), level, scale(stats["max"]), level, "#246b91", 2)
        for key in ["min", "max"]:
            chart.line(
                scale(stats[key]), level - 8, scale(stats[key]), level + 8, "#246b91", 2
            )
        chart.rect(
            scale(stats["25%"]),
            level - 14,
            max(1, scale(stats["75%"]) - scale(stats["25%"])),
            28,
            "#bfd8e5",
        )
        chart.line(
            scale(stats["50%"]),
            level - 14,
            scale(stats["50%"]),
            level + 14,
            "#246b91",
            3,
        )
        chart.text(
            x,
            y + 95,
            f"min {stats['min']:.2f}   Q1 {stats['25%']:.2f}   Q2 {stats['50%']:.2f}   Q3 {stats['75%']:.2f}   max {stats['max']:.2f}",
            size=11,
        )
    chart.text(
        35,
        565,
        "Линия: min–max; прямоугольник: Q1–Q3; штрих: медиана. σ — выборочное стандартное отклонение.",
        size=12,
    )
    chart.save(folder / "numeric_summary.svg")


def categorical_summary(frame, folder):
    chart = Chart(960, 590, "Категории и пропуски в исходных данных")
    for index, column in enumerate(["Survived", "Sex", "Pclass", "Embarked"]):
        x, y = 35 + index % 2 * 470, 70 + index // 2 * 210
        chart.text(x, y, column, size=15)
        counts = frame[column].fillna("Missing").astype(str).value_counts().sort_index()
        for row, (label, count) in enumerate(counts.items()):
            yy = y + 20 + row * 35
            chart.text(x, yy + 15, label)
            chart.rect(x + 85, yy, count / len(frame) * 300, 22, COLORS[index])
            chart.text(x + 90 + count / len(frame) * 300, yy + 15, count)
    chart.text(
        35,
        510,
        "Пропуски: "
        + "; ".join(
            f"{name} — {count} ({count / len(frame):.1%})"
            for name, count in frame.isna().sum().items()
            if count
        )
        + ".",
        size=15,
    )
    chart.text(
        35,
        545,
        "Survived: 0 — не выжил; 1 — выжил. Для остальных полей пропусков нет.",
        size=13,
    )
    chart.save(folder / "categories.svg")


def learning_curves(output, folder):
    histories = pd.read_csv(output / "metrics/learning_curves.csv")
    table = pd.read_csv(output / "metrics/test.csv")
    chart = Chart(960, 490, "Сходимость: log loss на обучающей выборке")
    for panel, (method, maximum) in enumerate([("gd", 5000), ("newton", 30)]):
        x, y, width, height = 65 + panel * 470, 85, 385, 285
        chart.text(
            x, 60, "Градиентный спуск" if method == "gd" else "Метод Ньютона", size=16
        )
        for value in [0.4, 0.5, 0.6, 0.7]:
            yy = y + height * (0.7 - value) / 0.3
            chart.line(x, yy, x + width, yy)
            chart.text(x - 10, yy + 4, f"{value:.1f}", anchor="end")
        for value in np.linspace(0, maximum, 6):
            xx = x + width * value / maximum
            chart.text(xx, y + height + 22, f"{value:.0f}", anchor="middle")
        subset = table[(table.method == method) & (table.iterations == maximum)]
        for index, row in enumerate(subset.itertuples()):
            history = histories[histories.config_id == row.config_id]
            step = max(1, len(history) // 500)
            history = pd.concat(
                [history.iloc[::step], history.tail(1)]
            ).drop_duplicates()
            chart.path(
                x + width * history.iteration / maximum,
                y + height * (0.7 - history.train_log_loss) / 0.3,
                COLORS[index],
            )
            chart.line(x + index * 98, 430, x + index * 98 + 18, 430, COLORS[index], 3)
            chart.text(x + index * 98 + 23, 435, f"α={row.learning_rate:g}", size=11)
        chart.text(x + width / 2, 410, "Итерации", anchor="middle")
    chart.save(folder / "learning_curves.svg")


def performance(output, folder):
    table = pd.read_csv(output / "metrics/test.csv")
    chart = Chart(960, 640, "Тестовые метрики для всех 21 конфигураций")
    metrics = ["accuracy", "precision", "recall", "f1"]
    x0, width = 315, 130
    chart.text(30, 63, "Метод / α / итерации", size=13)
    for i, name in enumerate(metrics):
        chart.text(x0 + i * width + width / 2, 63, name, anchor="middle", size=13)
    for index, row in enumerate(table.itertuples()):
        y = 80 + index * 24
        chart.text(
            30,
            y + 16,
            f"{'GD' if row.method == 'gd' else 'Newton'} / {row.learning_rate:g} / {row.iterations}"
            + (" *" if row.selected else ""),
            size=12,
        )
        for i, name in enumerate(metrics):
            value = getattr(row, name)
            shade = int(245 - (value - 0.4) * 120)
            chart.rect(
                x0 + i * width,
                y,
                width - 4,
                22,
                f"#{shade:02x}{min(250, shade + 14):02x}{min(255, shade + 24):02x}",
            )
            chart.text(
                x0 + i * width + width / 2, y + 16, f"{value:.3f}", anchor="middle"
            )
    chart.text(
        30,
        615,
        "* Конфигурация выбрана по минимуму log loss на валидационной выборке.",
        size=13,
    )
    chart.save(folder / "performance.svg")


def confusion(output, folder):
    table = pd.read_csv(output / "metrics/test.csv")
    row = table[table.selected].iloc[0]
    chart = Chart(640, 390, "Матрица ошибок выбранной модели")
    chart.text(375, 70, "Предсказанный класс", anchor="middle", size=15)
    chart.text(265, 100, "0", anchor="middle", size=16)
    chart.text(445, 100, "1", anchor="middle", size=16)
    for i, label in enumerate(["Истинный 0", "Истинный 1"]):
        chart.text(25, 165 + 110 * i, label, size=15)
        for j in range(2):
            key = [["tn", "fp"], ["fn", "tp"]][i][j]
            chart.rect(
                175 + 180 * j,
                115 + 110 * i,
                175,
                105,
                "#bfd8e5" if i == j else "#f3dbc5",
            )
            chart.text(
                263 + 180 * j,
                178 + 110 * i,
                f"{key.upper()} = {int(row[key])}",
                size=23,
                anchor="middle",
            )
    chart.text(
        25, 365, "Положительный класс: Survived = 1; порог вероятности: 0,5.", size=13
    )
    chart.save(folder / "confusion.svg")


def make_figures(frame, output):
    folder = output / "figures"
    numeric_summary(frame, folder)
    categorical_summary(frame, folder)
    learning_curves(output, folder)
    performance(output, folder)
    confusion(output, folder)
