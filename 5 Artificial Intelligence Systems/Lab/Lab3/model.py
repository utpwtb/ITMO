"""Linear regression with unpenalized intercept and proximal gradient descent.

Objective: MSE / 2 + lam * (ratio * ||w||_1 + (1-ratio) * ||w||_2^2 / 2).
Only NumPy and Pandas are used for model fitting and preprocessing.
"""
import numpy as np
import pandas as pd

FEATURES = ['Hours Studied', 'Previous Scores', 'Extracurricular Activities',
            'Sleep Hours', 'Sample Question Papers Practiced']
TARGET = 'Performance Index'
INTERACTION = 'Hours x Previous Scores'
MODELS = {'M1': FEATURES[:1], 'M2': FEATURES[:2], 'M3': FEATURES,
          'M4': FEATURES + [INTERACTION]}


def encode(frame):
    result = frame[FEATURES].copy()
    category = result[FEATURES[2]]
    if (category.notna() & ~category.isin(['Yes', 'No'])).any():
        raise ValueError('Unknown extracurricular category')
    result[FEATURES[2]] = category.map({'Yes': 1., 'No': 0.})
    return result.astype(float)


def engineer(frame, fill):
    result = encode(frame).fillna(pd.Series(fill))
    result[INTERACTION] = result[FEATURES[0]] * result[FEATURES[1]]
    return result


def fit_preprocessor(train):
    encoded = encode(train)
    fill = encoded.median()
    mode = encoded[FEATURES[2]].mode()
    if len(mode):
        fill[FEATURES[2]] = mode.iloc[0]
    if fill.isna().any():
        raise ValueError('No observed training values for a feature')
    filled = engineer(train, fill.to_dict())
    scale = filled.std(ddof=0).replace(0, 1.)
    return {'fill': fill.to_dict(), 'mean': filled.mean().to_dict(),
            'scale': scale.to_dict()}


def transform(frame, params):
    return ((engineer(frame, params['fill']) - pd.Series(params['mean']))
            / pd.Series(params['scale']))


def split_data(raw):
    # Match Lab1: remove full duplicates, keep its exact 20% test partition.
    clean = raw.drop_duplicates().dropna(subset=[TARGET]).copy()
    ids = np.random.default_rng(42).permutation(len(clean))
    cut = int(.8 * len(clean))
    pool, test = clean.iloc[ids[:cut]], clean.iloc[ids[cut:]]
    inner = np.random.default_rng(43).permutation(len(pool))
    n_val = len(test)
    return pool.iloc[inner[n_val:]], pool.iloc[inner[:n_val]], test


def metrics(y, prediction):
    residual = np.asarray(prediction) - y
    mse = float(np.mean(residual ** 2))
    variance = float(np.mean((y - np.mean(y)) ** 2))
    return {'mse': mse, 'r2': 1 - mse / variance if variance else np.nan,
            'rmse': float(np.sqrt(mse)), 'mae': float(np.mean(abs(residual)))}


def objective(x, y, beta, lam=0., ratio=0.):
    w = beta[1:]
    return float(np.mean((beta[0] + x @ w - y) ** 2) / 2
                 + lam * (ratio * abs(w).sum() + (1-ratio) * (w @ w) / 2))


def optimality_residual(x, y, beta, lam=0., ratio=0.):
    """Maximum absolute KKT residual; handles the L1 subgradient at zero."""
    error = beta[0] + x @ beta[1:] - y
    g = x.T @ error / len(y) + lam * (1-ratio) * beta[1:]
    residual = np.where(beta[1:] != 0, abs(g + lam * ratio * np.sign(beta[1:])),
                        np.maximum(abs(g) - lam * ratio, 0.))
    return float(max(abs(error.mean()), np.max(residual)))


def fit(x, y, *, lam=0., ratio=0., learning_rate=.05, iterations=15000,
        validation=None, record=False):
    """Full batch (proximal) GD. Every configuration starts at identical zeros.

    Sufficient statistics evaluate the same full-batch gradient with O(p^2)
    work per step. MSE history is unpenalized. Iteration 0 is recorded too.
    """
    x, y = np.asarray(x, float), np.asarray(y, float)
    if lam < 0 or not 0 <= ratio <= 1 or learning_rate <= 0 or iterations < 1:
        raise ValueError('Invalid optimization parameters')
    if x.ndim != 2 or len(y) != len(x) or not np.isfinite(x).all() or not np.isfinite(y).all():
        raise ValueError('Invalid training data')
    design = np.column_stack([np.ones(len(x)), x])
    gram, cross = design.T @ design / len(y), design.T @ y / len(y)
    # Safe upper bound on the smooth Hessian spectral norm.
    bound = np.max(abs(gram).sum(axis=1)) + lam * (1-ratio)
    if learning_rate * bound > 1:
        raise ValueError('Learning rate exceeds conservative stability bound')
    beta = np.zeros(design.shape[1])
    stats = [(gram, cross, float(y @ y / len(y)), float(np.var(y)))]
    if validation is not None:
        xv, yv = validation
        dv = np.column_stack([np.ones(len(xv)), xv])
        stats.append((dv.T @ dv / len(yv), dv.T @ yv / len(yv),
                      float(yv @ yv / len(yv)), float(np.var(yv))))
    history = []
    for step in range(iterations + 1):
        if record:
            row = {'iteration': step}
            for name, (g, c, yy, variance) in zip(['train', 'validation'], stats):
                mse = max(0., float(beta @ g @ beta - 2 * beta @ c + yy))
                row[name + '_mse'] = mse
                row[name + '_r2'] = 1 - mse / variance if variance else np.nan
            history.append(row)
        if step == iterations:
            break
        gradient = gram @ beta - cross
        gradient[1:] += lam * (1-ratio) * beta[1:]
        beta -= learning_rate * gradient
        threshold = learning_rate * lam * ratio
        beta[1:] = np.sign(beta[1:]) * np.maximum(abs(beta[1:]) - threshold, 0.)
    return beta, pd.DataFrame(history)
