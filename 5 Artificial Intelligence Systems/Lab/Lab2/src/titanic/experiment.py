"""Run all Titanic configurations and save reproducible, auditable results."""

import argparse
import hashlib
import json
import platform
from pathlib import Path

import numpy as np
import pandas as pd

from titanic.data import FEATURES, Preprocessor, stratified_split
from titanic.metrics import classification_metrics
from titanic.model import LogisticRegression, log_loss

ROOT = Path(__file__).resolve().parents[2]


def save_json(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, ensure_ascii=False), encoding="utf-8")


def parameter_grid():
    return [
        {"method": method, "learning_rate": rate, "iterations": count}
        for method, rates, counts in [
            ("gd", [0.001, 0.01, 0.1, 1.0], [100, 1000, 5000]),
            ("newton", [0.1, 0.5, 1.0], [3, 10, 30]),
        ]
        for rate in rates
        for count in counts
    ]


def run(data_path, output):
    frame = pd.read_csv(data_path)
    if "Survived" not in frame or not frame.Survived.isin([0, 1]).all():
        raise ValueError("Input must contain real binary Survived labels")
    if not frame.PassengerId.is_unique:
        raise ValueError("PassengerId must be unique")
    folders = {
        name: output / name
        for name in ["statistics", "metrics", "predictions", "model", "figures"]
    }
    for path in folders.values():
        path.mkdir(parents=True, exist_ok=True)
    frame.describe().T.to_csv(folders["statistics"] / "numeric.csv")
    frame.isna().sum().rename("missing").to_csv(folders["statistics"] / "missing.csv")
    categories = []
    for column in ["Survived", "Sex", "Pclass", "Embarked"]:
        for category, count in frame[column].fillna("Missing").value_counts().items():
            categories.append(
                {"feature": column, "category": category, "count": int(count)}
            )
    pd.DataFrame(categories).to_csv(
        folders["statistics"] / "categorical.csv", index=False
    )
    target = frame.Survived.to_numpy()
    train, test = stratified_split(target, seed=42)
    inner_train, inner_val = stratified_split(target[train], seed=43)
    fit, validation = train[inner_train], train[inner_val]
    splits = np.full(len(frame), "fit", dtype=object)
    splits[validation], splits[test] = "validation", "test"
    pd.DataFrame({"PassengerId": frame.PassengerId, "split": splits}).to_csv(
        output / "split.csv", index=False
    )

    inner_prep = Preprocessor().fit(frame.iloc[fit])
    fit_matrix = inner_prep.transform(frame.iloc[fit])
    val_matrix = inner_prep.transform(frame.iloc[validation])
    configurations = parameter_grid()
    val_rows = []
    for index, config in enumerate(configurations):
        model = LogisticRegression(**config).fit(fit_matrix, target[fit])
        val_rows.append(
            {
                "config_id": index,
                **config,
                "log_loss": log_loss(target[validation], val_matrix @ model.weights),
                **classification_metrics(target[validation], model.predict(val_matrix)),
            }
        )
    val_table = pd.DataFrame(val_rows)
    # Freeze the choice before any access to test metrics. Ties use grid order.
    selected_id = int(val_table.log_loss.idxmin())
    val_table.to_csv(folders["metrics"] / "validation.csv", index=False)
    prep = Preprocessor().fit(frame.iloc[train])
    train_matrix = prep.transform(frame.iloc[train])
    test_matrix = prep.transform(frame.iloc[test])
    rows, histories = [], []
    all_predictions = pd.DataFrame(
        {"PassengerId": frame.iloc[test].PassengerId.to_numpy(), "actual": target[test]}
    )
    selected_model = None
    for index, config in enumerate(configurations):
        model = LogisticRegression(**config).fit(train_matrix, target[train])
        probability = model.predict_proba(test_matrix)
        rows.append(
            {
                "config_id": index,
                **config,
                "selected": index == selected_id,
                "train_log_loss": model.loss_history[-1],
                "test_log_loss": log_loss(target[test], test_matrix @ model.weights),
                **classification_metrics(target[test], probability >= 0.5),
            }
        )
        all_predictions[f"probability_{index:02d}"] = probability
        histories.extend(
            {"config_id": index, "iteration": step, "train_log_loss": value}
            for step, value in enumerate(model.loss_history)
        )
        if index == selected_id:
            selected_model = model
    table = pd.DataFrame(rows)
    table.to_csv(folders["metrics"] / "test.csv", index=False)
    pd.DataFrame(histories).to_csv(
        folders["metrics"] / "learning_curves.csv", index=False
    )
    all_predictions.to_csv(
        folders["predictions"] / "all_configurations.csv", index=False
    )
    selected_predictions = all_predictions[
        ["PassengerId", "actual", f"probability_{selected_id:02d}"]
    ].rename(columns={f"probability_{selected_id:02d}": "probability"})
    selected_predictions["predicted"] = (
        selected_predictions.probability >= 0.5
    ).astype(int)
    selected_predictions.to_csv(folders["predictions"] / "selected.csv", index=False)
    pd.DataFrame(
        {
            "feature": ["Intercept"] + FEATURES,
            "weight": selected_model.weights,
            "odds_ratio": np.exp(selected_model.weights),
        }
    ).to_csv(folders["model"] / "coefficients.csv", index=False)
    save_json(
        folders["model"] / "logistic.json",
        {
            "config": configurations[selected_id],
            "threshold": 0.5,
            "weights": selected_model.weights.tolist(),
            "preprocessing": prep.to_dict(),
        },
    )
    summary = {
        "dataset": "Titanic labelled train.csv",
        "rows": len(frame),
        "sha256": hashlib.sha256(data_path.read_bytes()).hexdigest(),
        "duplicates": int(frame.duplicated().sum()),
        "missing": frame.isna().sum().to_dict(),
        "splits": {
            name: {
                "total": len(indices),
                "class_0": int(np.sum(target[indices] == 0)),
                "class_1": int(np.sum(target[indices] == 1)),
            }
            for name, indices in [
                ("train", train),
                ("test", test),
                ("fit", fit),
                ("validation", validation),
            ]
        },
        "selected_id": selected_id,
        "selected": rows[selected_id],
        "selected_validation": val_rows[selected_id],
        "baseline": classification_metrics(
            target[test], np.zeros(len(test), dtype=int)
        ),
        "versions": {
            "python": platform.python_version(),
            "numpy": np.__version__,
            "pandas": pd.__version__,
        },
    }
    save_json(output / "summary.json", summary)
    from titanic.visualization import make_figures

    make_figures(frame, output)
    print(json.dumps(summary, indent=2))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--data", type=Path, default=ROOT / "data/raw/train.csv")
    parser.add_argument("--output", type=Path, default=ROOT / "results")
    arguments = parser.parse_args()
    run(arguments.data, arguments.output)


if __name__ == "__main__":
    main()
