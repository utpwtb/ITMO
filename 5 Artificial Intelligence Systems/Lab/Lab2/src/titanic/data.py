"""Training-only imputation, fixed reference coding, and stratified splitting."""

import numpy as np
import pandas as pd

NUMERIC = ["Age", "SibSp", "Parch", "Fare"]
CATEGORIES = {
    "Sex": ["female", "male"],
    "Pclass": [1, 2, 3],
    "Embarked": ["C", "Q", "S"],
}
FEATURES = NUMERIC + ["Sex_male", "Pclass_2", "Pclass_3", "Embarked_Q", "Embarked_S"]


def stratified_split(target, fraction=0.2, seed=42):
    """Return disjoint positional indices, retaining both classes in each part."""
    target = np.asarray(target)
    if not 0 < fraction < 1:
        raise ValueError("fraction must lie strictly between zero and one")
    rng = np.random.default_rng(seed)
    train, test = [], []
    for label in np.unique(target):
        indices = rng.permutation(np.flatnonzero(target == label))
        count = round(len(indices) * fraction)
        if count < 1 or count >= len(indices):
            raise ValueError("Each class needs observations in both splits")
        test.extend(indices[:count])
        train.extend(indices[count:])
    return rng.permutation(train), rng.permutation(test)


class Preprocessor:
    """Impute numeric medians and categorical modes; scale numeric columns only."""

    @staticmethod
    def validate(frame):
        missing = set(NUMERIC + list(CATEGORIES)) - set(frame.columns)
        if missing:
            raise ValueError(f"Missing columns: {sorted(missing)}")
        numeric = frame[NUMERIC].astype(float)
        if np.isinf(numeric.to_numpy()).any() or (numeric < 0).any().any():
            raise ValueError("Numeric features must be nonnegative and not infinite")
        for name, allowed in CATEGORIES.items():
            if not frame[name].dropna().isin(allowed).all():
                raise ValueError(f"Unsupported category in {name}; expected {allowed}")

    def fit(self, frame):
        self.validate(frame)
        self.medians = frame[NUMERIC].astype(float).median()
        if self.medians.isna().any():
            raise ValueError("A numeric feature is entirely missing")
        self.modes = {}
        for name in CATEGORIES:
            mode = frame[name].mode()
            if mode.empty:
                raise ValueError(f"Categorical feature {name} is entirely missing")
            value = mode.iloc[0]
            self.modes[name] = value.item() if hasattr(value, "item") else value
        filled = frame[NUMERIC].astype(float).fillna(self.medians)
        self.means = filled.mean()
        self.scales = filled.std(ddof=0).replace(0.0, 1.0)
        return self

    def transform(self, frame):
        self.validate(frame)
        numeric = frame[NUMERIC].astype(float).fillna(self.medians)
        blocks = [
            np.ones((len(frame), 1)),
            ((numeric - self.means) / self.scales).to_numpy(),
        ]
        for name, allowed in CATEGORIES.items():
            values = frame[name].fillna(self.modes[name])
            blocks.extend(
                (values == category).to_numpy(dtype=float)[:, None]
                for category in allowed[1:]
            )
        matrix = np.column_stack(blocks)
        if not np.isfinite(matrix).all():
            raise ValueError("Preprocessing produced non-finite features")
        return matrix

    def to_dict(self):
        return {
            "medians": self.medians.to_dict(),
            "modes": self.modes,
            "means": self.means.to_dict(),
            "scales": self.scales.to_dict(),
            "features": FEATURES,
        }

    @classmethod
    def from_dict(cls, state):
        if state["features"] != FEATURES:
            raise ValueError("Model feature schema does not match this implementation")
        result = cls()
        for name in ["medians", "means", "scales"]:
            setattr(result, name, pd.Series(state[name]).reindex(NUMERIC))
        result.modes = state["modes"]
        return result
