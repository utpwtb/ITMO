"""Brute-force k-nearest neighbors for numeric features and targets."""

import numpy as np


DISTANCES = ("euclidean", "manhattan", "chebyshev")


class KNN:
    def __init__(self, k, task, distance):
        if not isinstance(k, (int, np.integer)) or k < 1:
            raise ValueError("k must be a positive integer.")
        if task not in ("classification", "regression"):
            raise ValueError("Unknown task.")
        if distance not in DISTANCES:
            raise ValueError("Unknown distance.")
        self.k = k
        self.task = task
        self.distance = distance
        self._features = None

    def fit(self, features, targets):
        features = np.asarray(features, dtype=float)
        targets = np.asarray(targets)
        if features.ndim != 2 or features.shape[1] == 0:
            raise ValueError("Expected a nonempty feature matrix.")
        if targets.shape != (len(features),) or len(features) < self.k:
            raise ValueError("Expected one target per row and at least k rows.")
        self._features = features.copy()
        self._targets = targets.copy()
        return self

    def predict(self, features):
        if self._features is None:
            raise ValueError("Fit the model before predicting.")
        features = np.asarray(features, dtype=float)
        if features.ndim != 2 or features.shape[1] != self._features.shape[1]:
            raise ValueError("Unexpected feature matrix shape.")
        dtype = self._targets.dtype if self.task == "classification" else float
        predictions = np.empty(len(features), dtype=dtype)
        for row, query in enumerate(features):
            distances = self._distances(query)
            # Stable sorting keeps training row order at equal distances.
            neighbors = np.argsort(distances, kind="stable")[:self.k]
            targets = self._targets[neighbors]
            if self.task == "classification":
                predictions[row] = self._vote(targets, distances[neighbors])
            else:
                predictions[row] = targets.mean()
        return predictions

    def _distances(self, query):
        difference = np.abs(self._features - query)
        if self.distance == "euclidean":
            return np.sqrt(np.sum(difference ** 2, axis=1))
        if self.distance == "manhattan":
            return difference.sum(axis=1)
        return difference.max(axis=1)

    @staticmethod
    def _vote(targets, distances):
        labels, counts = np.unique(targets, return_counts=True)
        leaders = labels[counts == counts.max()]
        # Among vote leaders, prefer the smallest distance sum, then label.
        return min(leaders, key=lambda c: (distances[targets == c].sum(), c))
