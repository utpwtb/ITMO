"""Логистическая регрессия с нуля: только NumPy и Pandas."""
import numpy as np
import pandas as pd

FEATURES = ['Pregnancies', 'Glucose', 'BloodPressure', 'SkinThickness',
            'Insulin', 'BMI', 'DiabetesPedigreeFunction', 'Age']
ZERO_MISSING = ['Glucose', 'BloodPressure', 'SkinThickness', 'Insulin', 'BMI']


def sigmoid(z):
    """Устойчивая сигмоида без переполнения exp для больших |z|."""
    z = np.asarray(z, dtype=float)
    out = np.empty_like(z)
    positive = z >= 0
    out[positive] = 1 / (1 + np.exp(-z[positive]))
    ez = np.exp(z[~positive])
    out[~positive] = ez / (1 + ez)
    return out


def log_loss(y, logits):
    """Средняя бинарная кросс-энтропия, вычисленная по логитам."""
    return float(np.mean(np.logaddexp(0, logits) - y * logits))


def derivatives(X, y, weights):
    p = sigmoid(X @ weights)
    gradient = X.T @ (p - y) / len(y)
    hessian = X.T @ ((p * (1 - p))[:, None] * X) / len(y)
    return gradient, hessian


class LogisticRegression:
    def __init__(self, method='gd', learning_rate=0.1, iterations=1000):
        if method not in ('gd', 'newton'):
            raise ValueError('method must be gd or newton')
        if learning_rate <= 0 or iterations < 1:
            raise ValueError('learning_rate and iterations must be positive')
        self.method = method
        self.learning_rate = learning_rate
        self.iterations = iterations

    def fit(self, X, y):
        """Полный градиент; для Ньютона решается H d = g, без H^{-1}."""
        self.weights = np.zeros(X.shape[1])
        self.loss_history = [log_loss(y, X @ self.weights)]
        for _ in range(self.iterations):
            p = sigmoid(X @ self.weights)
            gradient = X.T @ (p - y) / len(y)
            if self.method == 'gd':
                direction = gradient
            else:
                hessian = X.T @ ((p * (1 - p))[:, None] * X) / len(y)
                # Численная стабилизация системы, не штраф в функции потерь.
                direction = np.linalg.solve(
                    hessian + 1e-8 * np.eye(X.shape[1]), gradient)
            self.weights -= self.learning_rate * direction
            loss = log_loss(y, X @ self.weights)
            if not np.isfinite(loss):
                raise FloatingPointError('Non-finite loss')
            self.loss_history.append(loss)
        return self

    def predict_proba(self, X):
        return sigmoid(X @ self.weights)

    def predict(self, X, threshold=0.5):
        return (self.predict_proba(X) >= threshold).astype(int)


class Preprocessor:
    """Медианы, средние и масштабы оцениваются только на обучении."""
    @staticmethod
    def clean(frame):
        result = frame[FEATURES].astype(float).copy()
        result[ZERO_MISSING] = result[ZERO_MISSING].replace(0, np.nan)
        return result

    def fit(self, frame):
        clean = self.clean(frame)
        self.medians = clean.median()
        if self.medians.isna().any():
            raise ValueError('A feature has no observed training values')
        filled = clean.fillna(self.medians)
        self.means = filled.mean()
        self.scales = filled.std(ddof=0).replace(0, 1)
        return self

    def transform(self, frame):
        values = (self.clean(frame).fillna(self.medians) - self.means) / self.scales
        return np.column_stack([np.ones(len(frame)), values.to_numpy()])

    def to_dict(self):
        return {k: getattr(self, k).to_dict() for k in ('medians', 'means', 'scales')}


def stratified_split(y, fraction=0.2, seed=42):
    """Индексы train/test; доля test округляется отдельно для каждого класса."""
    rng = np.random.default_rng(seed)
    train, test = [], []
    for label in np.unique(y):
        indices = rng.permutation(np.flatnonzero(y == label))
        count = round(len(indices) * fraction)
        test.extend(indices[:count])
        train.extend(indices[count:])
    return rng.permutation(train), rng.permutation(test)


def metrics(y, predictions):
    """Матрица: строки -- истина, столбцы -- прогноз, порядок классов 0, 1."""
    tn = int(np.sum((y == 0) & (predictions == 0)))
    fp = int(np.sum((y == 0) & (predictions == 1)))
    fn = int(np.sum((y == 1) & (predictions == 0)))
    tp = int(np.sum((y == 1) & (predictions == 1)))
    precision = tp / (tp + fp) if tp + fp else 0.
    recall = tp / (tp + fn) if tp + fn else 0.
    return dict(accuracy=(tp + tn) / len(y), precision=precision, recall=recall,
                f1=2 * tp / (2 * tp + fp + fn) if 2 * tp + fp + fn else 0.,
                tn=tn, fp=fp, fn=fn, tp=tp)
