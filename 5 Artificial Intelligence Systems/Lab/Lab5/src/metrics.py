"""Бинарные метрики и точки кривых без библиотечных реализаций."""

from dataclasses import dataclass


@dataclass
class Confusion:
    tp: int
    fp: int
    tn: int
    fn: int

    @property
    def accuracy(self):
        return (self.tp + self.tn) / (self.tp + self.fp + self.tn + self.fn)

    @property
    def precision(self):
        return self.tp / (self.tp + self.fp) if self.tp + self.fp else 0.0

    @property
    def recall(self):
        return self.tp / (self.tp + self.fn) if self.tp + self.fn else 0.0

    @property
    def fpr(self):
        return self.fp / (self.fp + self.tn) if self.fp + self.tn else 0.0


def evaluate(labels, scores, threshold=0.5):
    tp = fp = tn = fn = 0
    for label, score in zip(labels, scores, strict=True):
        prediction = int(score >= threshold)
        tp += int(label == prediction == 1)
        fp += int(label == 0 and prediction == 1)
        tn += int(label == prediction == 0)
        fn += int(label == 1 and prediction == 0)
    return Confusion(tp, fp, tn, fn)


def threshold_points(labels, scores, leaf_scores):
    # Значения во внутренних узлах тоже возможны при отсутствии ветви.
    thresholds = {0.0, 1.0, *leaf_scores, *scores}
    # При +inf нет положительных прогнозов даже при наличии оценки 1.
    return [
        (threshold, evaluate(labels, scores, threshold))
        for threshold in [float("inf"), *sorted(thresholds, reverse=True)]
    ]


def curve_points(points):
    roc = [(m.fpr, m.recall) for _, m in points]
    # При пустом наборе положительных прогнозов используем (0, 1) для PR.
    pr = [(m.recall, m.precision if m.tp + m.fp else 1.0) for _, m in points]
    return roc, pr


def trapezoidal_auc(points):
    # Стабильная сортировка по x сохраняет порядок порогов при равных x.
    ordered = sorted(points, key=lambda point: point[0])
    return sum(
        (right_x - left_x) * (left_y + right_y) / 2
        for (left_x, left_y), (right_x, right_y) in zip(ordered, ordered[1:])
    )
