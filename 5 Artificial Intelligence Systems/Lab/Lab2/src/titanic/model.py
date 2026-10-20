"""Numerically stable binary logistic regression implemented with NumPy."""

import numpy as np


def sigmoid(logits):
    """Evaluate the sigmoid without exponential overflow."""
    logits = np.asarray(logits, dtype=float)
    values = np.empty_like(logits)
    positive = logits >= 0
    values[positive] = 1.0 / (1.0 + np.exp(-logits[positive]))
    exponent = np.exp(logits[~positive])
    values[~positive] = exponent / (1.0 + exponent)
    return values


def log_loss(target, logits):
    """Mean Bernoulli negative log likelihood, evaluated from logits."""
    return float(np.mean(np.logaddexp(0.0, logits) - target * logits))


def derivatives(matrix, target, weights):
    probabilities = sigmoid(matrix @ weights)
    gradient = matrix.T @ (probabilities - target) / len(target)
    curvature = probabilities * (1.0 - probabilities)
    hessian = matrix.T @ (curvature[:, None] * matrix) / len(target)
    return gradient, hessian


class LogisticRegression:
    """Full-batch gradient descent or damped Newton with fixed step size."""

    def __init__(self, method="gd", learning_rate=0.1, iterations=1000):
        if method not in {"gd", "newton"}:
            raise ValueError("method must be 'gd' or 'newton'")
        if not np.isfinite(learning_rate) or learning_rate <= 0:
            raise ValueError("learning_rate must be finite and positive")
        if not isinstance(iterations, int) or iterations < 1:
            raise ValueError("iterations must be a positive integer")
        self.method = method
        self.learning_rate = learning_rate
        self.iterations = iterations

    def fit(self, matrix, target):
        matrix = np.asarray(matrix, dtype=float)
        target = np.asarray(target, dtype=float)
        if matrix.ndim != 2 or target.shape != (len(matrix),) or not len(target):
            raise ValueError("Expected a nonempty matrix and matching target")
        if not np.isfinite(matrix).all() or not np.isin(target, [0, 1]).all():
            raise ValueError("Inputs must be finite; target must contain 0 or 1")
        self.weights = np.zeros(matrix.shape[1])
        self.loss_history = [log_loss(target, matrix @ self.weights)]
        for _ in range(self.iterations):
            probabilities = sigmoid(matrix @ self.weights)
            gradient = matrix.T @ (probabilities - target) / len(target)
            if self.method == "newton":
                curvature = probabilities * (1.0 - probabilities)
                hessian = matrix.T @ (curvature[:, None] * matrix) / len(target)
                # Stabilize the linear solve; the objective has no L2 penalty.
                direction = np.linalg.solve(
                    hessian + 1e-8 * np.eye(matrix.shape[1]), gradient
                )
            else:
                direction = gradient
            self.weights -= self.learning_rate * direction
            loss = log_loss(target, matrix @ self.weights)
            if not np.isfinite(loss):
                raise FloatingPointError("Training produced a non-finite loss")
            self.loss_history.append(loss)
        return self

    def predict_proba(self, matrix):
        return sigmoid(np.asarray(matrix, dtype=float) @ self.weights)

    def predict(self, matrix, threshold=0.5):
        return (self.predict_proba(matrix) >= threshold).astype(int)
