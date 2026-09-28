import numpy as np


def gauss_solve(a, b):
    """Метод Гаусса с выбором максимального по модулю ведущего элемента."""
    a, b = np.asarray(a, dtype=float).copy(), np.asarray(b, dtype=float).copy()
    n = len(b)
    if a.shape != (n, n):
        raise ValueError('Expected a square matrix')
    tolerance = 1e-12 * max(1.0, float(np.max(np.abs(a))))
    for k in range(n):
        pivot = k + int(np.argmax(np.abs(a[k:, k])))
        if abs(a[pivot, k]) <= tolerance:
            raise ValueError('Singular or nearly singular normal matrix')
        a[[k, pivot]], b[[k, pivot]] = a[[pivot, k]], b[[pivot, k]]
        for i in range(k + 1, n):
            factor = a[i, k] / a[k, k]
            a[i, k:] -= factor * a[k, k:]
            b[i] -= factor * b[k]
    x = np.zeros(n)
    for k in range(n - 1, -1, -1):
        x[k] = (b[k] - a[k, k + 1:] @ x[k + 1:]) / a[k, k]
    return x


def fit_ols(x, y):
    """Минимизация SSE: X^T X beta = X^T y; без готовых решателей."""
    design = np.column_stack([np.ones(len(x)), x])
    return gauss_solve(design.T @ design, design.T @ y)


def predict(x, beta):
    return beta[0] + x @ beta[1:]


def metrics(y, prediction):
    residual = y - prediction
    sse = float(residual @ residual)
    sst = float(np.sum((y - y.mean()) ** 2))
    return {'r2': 1 - sse / sst if sst > 0 else None,
            'rmse': float(np.sqrt(sse / len(y))),
            'mae': float(np.mean(np.abs(residual))), 'sse': sse}


