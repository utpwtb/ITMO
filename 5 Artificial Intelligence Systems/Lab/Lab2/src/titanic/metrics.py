"""Binary metrics with class 1 (survived) as the positive class."""

import numpy as np


def classification_metrics(target, predicted):
    target, predicted = np.asarray(target), np.asarray(predicted)
    if target.ndim != 1 or target.shape != predicted.shape or target.size == 0:
        raise ValueError("Expected matching nonempty one-dimensional arrays")
    if not np.isin(target, [0, 1]).all() or not np.isin(predicted, [0, 1]).all():
        raise ValueError("Labels must be binary")
    tn = int(np.sum((target == 0) & (predicted == 0)))
    fp = int(np.sum((target == 0) & (predicted == 1)))
    fn = int(np.sum((target == 1) & (predicted == 0)))
    tp = int(np.sum((target == 1) & (predicted == 1)))
    return {
        "accuracy": (tn + tp) / len(target),
        "precision": tp / (tp + fp) if tp + fp else 0.0,
        "recall": tp / (tp + fn) if tp + fn else 0.0,
        "f1": 2 * tp / (2 * tp + fp + fn) if 2 * tp + fp + fn else 0.0,
        "tn": tn,
        "fp": fp,
        "fn": fn,
        "tp": tp,
    }
