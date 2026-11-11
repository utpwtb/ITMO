"""Полносвязная сеть и обучение без автоматического дифференцирования."""

import numpy as np


class Linear:
    def __init__(self, n_in, n_out, rng, *, relu=True, dtype=np.float32):
        # He для скрытого слоя с ReLU, масштаб 1/sqrt(n_in) для логитов.
        scale = np.sqrt((2 if relu else 1) / n_in)
        self.W = rng.normal(0, scale, (n_in, n_out)).astype(dtype)
        self.b = np.zeros(n_out, dtype=dtype)
        self.dW = np.zeros_like(self.W)
        self.db = np.zeros_like(self.b)

    def forward(self, x, training=True):
        if training:
            self.x = x
        return x @ self.W + self.b

    def backward(self, dy):
        self.dW[:] = self.x.T @ dy
        self.db[:] = dy.sum(axis=0)
        return dy @ self.W.T

    def parameters(self):
        return ((self.W, self.dW), (self.b, self.db))


class ReLU:
    def forward(self, x, training=True):
        if training:
            self.positive = x > 0
        return np.maximum(x, 0)

    def backward(self, dy):
        return dy * self.positive


class Flatten:
    def forward(self, x, training=True):
        if training:
            self.shape = x.shape
        return x.reshape(len(x), -1)

    def backward(self, dy):
        return dy.reshape(self.shape)


class Dropout:
    def __init__(self, probability, rng):
        if not 0 <= probability < 1:
            raise ValueError("Dropout probability must be in [0, 1).")
        self.keep = 1 - probability
        self.rng = rng

    def forward(self, x, training=True):
        if not training:
            return x
        self.scale = (self.rng.random(x.shape, dtype=np.float32) < self.keep).astype(x.dtype)
        self.scale /= self.keep
        return x * self.scale

    def backward(self, dy):
        return dy * self.scale


def _softmax_terms(logits):
    # Вычитание максимума защищает exp от переполнения.
    shifted = logits - logits.max(axis=1, keepdims=True)
    exp = np.exp(shifted)
    total = exp.sum(axis=1, keepdims=True)
    return shifted, exp / total, total


def softmax(logits):
    return _softmax_terms(logits)[1]


class SoftmaxWithLoss:
    def forward(self, logits, one_hot):
        shifted, self.probabilities, total = _softmax_terms(logits)
        self.targets = one_hot
        # log-sum-exp сохраняет конечный loss даже при exp(z) = 0.
        return float((np.log(total[:, 0]) - (one_hot * shifted).sum(axis=1)).mean())

    def backward(self):
        return (self.probabilities - self.targets) / len(self.targets)


class Adam:
    def __init__(self, parameters, lr=0.001, beta1=0.9, beta2=0.999, eps=1e-8):
        self.parameters = list(parameters)
        self.lr, self.beta1, self.beta2, self.eps = lr, beta1, beta2, eps
        self.m = [np.zeros_like(value) for value, _ in self.parameters]
        self.v = [np.zeros_like(value) for value, _ in self.parameters]
        self.t = 0

    def step(self):
        self.t += 1
        first_correction = 1 - self.beta1**self.t
        second_correction = 1 - self.beta2**self.t
        for (value, gradient), m, v in zip(self.parameters, self.m, self.v):
            m *= self.beta1
            m += (1 - self.beta1) * gradient
            v *= self.beta2
            v += (1 - self.beta2) * np.square(gradient)
            m_hat = m / first_correction
            v_hat = v / second_correction
            value -= self.lr * m_hat / (np.sqrt(v_hat) + self.eps)


class MLP:
    def __init__(self, widths, dropout, seed):
        self.widths = tuple(widths)
        self.dropout = dropout
        rng = np.random.default_rng(seed)
        self.layers = [Flatten()]
        n_in = 28 * 28
        for width in self.widths:
            self.layers.extend([Linear(n_in, width, rng), ReLU()])
            if dropout:
                self.layers.append(Dropout(dropout, rng))
            n_in = width
        self.layers.append(Linear(n_in, 10, rng, relu=False))

    def forward(self, x, training=False):
        for layer in self.layers:
            x = layer.forward(x, training=training)
        return x

    def backward(self, dy):
        for layer in reversed(self.layers):
            dy = layer.backward(dy)
        return dy

    def parameters(self):
        for layer in self.layers:
            if isinstance(layer, Linear):
                yield from layer.parameters()


def save_model(path, model):
    parameters = [value for value, _ in model.parameters()]
    np.savez(path, *parameters, widths=np.asarray(model.widths, dtype=np.int64),
             dropout=np.float64(model.dropout))


def load_model(path):
    with np.load(path, allow_pickle=False) as checkpoint:
        model = MLP(tuple(checkpoint["widths"]), checkpoint["dropout"].item(), seed=0)
        for index, (value, _) in enumerate(model.parameters()):
            value[:] = checkpoint[f"arr_{index}"]
    return model


def gradient_check():
    """Сравнивает dX, dW и db с центральными разностями в float64."""
    rng = np.random.default_rng(6)
    layer = Linear(3, 4, rng, relu=False, dtype=np.float64)
    x = rng.normal(size=(2, 3))
    targets = np.eye(4)[[1, 2]]
    criterion = SoftmaxWithLoss()
    criterion.forward(layer.forward(x), targets)
    dx = layer.backward(criterion.backward())

    h = 1e-5
    max_error = 0.0
    for value, analytic in ((x, dx), *layer.parameters()):
        for index in np.ndindex(value.shape):
            original = value[index]
            value[index] = original + h
            plus = criterion.forward(layer.forward(x), targets)
            value[index] = original - h
            minus = criterion.forward(layer.forward(x), targets)
            value[index] = original
            numeric = (plus - minus) / (2 * h)
            max_error = max(max_error, abs(numeric - analytic[index]))
    return float(max_error)
