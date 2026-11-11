"""Classification and regression scores implemented with NumPy."""

import numpy as np


def confusion_matrix(actual, predicted):
    # Sorted labels define both axes. Rows are actual, columns predicted.
    labels = np.union1d(actual, predicted)
    matrix = np.zeros((len(labels), len(labels)), dtype=int)
    rows = np.searchsorted(labels, actual)
    columns = np.searchsorted(labels, predicted)
    np.add.at(matrix, (rows, columns), 1)
    return labels, matrix


def _divide(numerator, denominator):
    # A class score with an undefined denominator contributes zero.
    return np.divide(
        numerator, denominator,
        out=np.zeros_like(numerator, dtype=float), where=denominator != 0,
    )


def classification_scores(matrix):
    tp = matrix.diagonal()
    precision = _divide(tp, matrix.sum(axis=0))
    recall = _divide(tp, matrix.sum(axis=1))
    f1 = _divide(2 * precision * recall, precision + recall)
    return {
        "accuracy": tp.sum() / matrix.sum(),
        "precision_macro": precision.mean(),
        "recall_macro": recall.mean(),
        "f1_macro": f1.mean(),
    }


def regression_scores(actual, predicted):
    residuals = actual - predicted
    squared_errors = residuals ** 2
    sst = np.sum((actual - actual.mean()) ** 2)
    # R² is undefined for a constant target under the stated formula.
    return {
        "mae": np.abs(residuals).mean(),
        "mse": squared_errors.mean(),
        "r2": 1 - squared_errors.sum() / sst if sst else np.nan,
    }
