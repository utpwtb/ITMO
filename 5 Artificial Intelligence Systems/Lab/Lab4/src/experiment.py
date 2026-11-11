"""Run the Wine classification and Diabetes regression experiments."""

import argparse
import csv
from pathlib import Path

import numpy as np
from sklearn.datasets import load_diabetes, load_wine
from sklearn.model_selection import train_test_split

from knn import DISTANCES, KNN
from metrics import classification_scores, confusion_matrix, regression_scores
from plots import confusion_plot, distributions, regression_plot, validation_curves


ROOT = Path(__file__).resolve().parents[1]
NEIGHBOR_COUNTS = (3, 5, 10, 15)


def write_csv(path, records):
    with path.open("w", newline="", encoding="utf-8") as stream:
        writer = csv.DictWriter(stream, fieldnames=records[0].keys())
        writer.writeheader()
        writer.writerows(records)


def split_indices(targets, classification):
    train, holdout = train_test_split(
        np.arange(len(targets)), test_size=0.4, random_state=42,
        stratify=targets if classification else None,
    )
    validation, test = train_test_split(
        holdout, test_size=0.5, random_state=43,
        stratify=targets[holdout] if classification else None,
    )
    return train, validation, test


def standardize(train, validation, test):
    center = train.mean(axis=0)
    scale = train.std(axis=0, ddof=0)
    # A constant training feature must not cause division by zero.
    scale[scale == 0] = 1
    return tuple((part - center) / scale for part in (train, validation, test))


def describe(columns):
    records = []
    for name, values in columns.items():
        q1, median, q3 = np.percentile(values, [25, 50, 75])
        records.append({
            "variable": name, "n": len(values), "mean": values.mean(),
            "std": values.std(ddof=1), "min": values.min(), "q1": q1,
            "median": median, "q3": q3, "max": values.max(),
        })
    return records


def run(dataset, task, name, results, figures):
    results = results / name.lower()
    results.mkdir(parents=True, exist_ok=True)
    figures.mkdir(parents=True, exist_ok=True)

    features, targets = dataset.data, dataset.target
    if not (np.isfinite(features).all() and np.isfinite(targets).all()):
        raise ValueError(f"{name} contains missing or non-finite values.")
    classification = task == "classification"
    train, validation, test = split_indices(targets, classification)
    x_train, x_validation, x_test = standardize(
        features[train], features[validation], features[test],
    )
    y_train, y_validation, y_test = targets[train], targets[validation], targets[test]

    records = []
    for distance in DISTANCES:
        for k in NEIGHBOR_COUNTS:
            model = KNN(k, task, distance).fit(x_train, y_train)
            predicted = model.predict(x_validation)
            if classification:
                _, matrix = confusion_matrix(y_validation, predicted)
                scores = classification_scores(matrix)
            else:
                scores = regression_scores(y_validation, predicted)
            records.append({"distance": distance, "k": k, **scores})
    write_csv(results / "validation.csv", records)

    if classification:
        score, direction, ylabel = "f1_macro", -1, "Macro F1"
    else:
        score, direction, ylabel = "mse", 1, "MSE"
    # Break equal validation scores by smaller k, then DISTANCES order.
    best = min(records, key=lambda r: (
        direction * r[score], r["k"], DISTANCES.index(r["distance"]),
    ))
    model = KNN(best["k"], task, best["distance"]).fit(x_train, y_train)
    predicted = model.predict(x_test)

    if classification:
        labels, matrix = confusion_matrix(y_test, predicted)
        scores = classification_scores(matrix)
        write_csv(results / "confusion_matrix.csv", [
            {"actual": label, **dict(zip(map(str, labels), row))}
            for label, row in zip(labels, matrix)
        ])
        confusion_plot(labels, matrix, figures / "wine_test.pdf")
    else:
        scores = regression_scores(y_test, predicted)
        regression_plot(y_test, predicted, figures / "diabetes_test.pdf")

    write_csv(results / "test_metrics.csv", [
        {"distance": best["distance"], "k": best["k"], **scores},
    ])
    write_csv(results / "test_predictions.csv", [
        {"row": row, "actual": actual, "predicted": prediction}
        for row, actual, prediction in zip(test, y_test, predicted)
    ])
    write_csv(results / "split.csv", [
        {"row": row, "subset": subset, "target": targets[row]}
        for subset, rows in (("train", train), ("validation", validation), ("test", test))
        for row in rows
    ])
    validation_curves(
        records, DISTANCES, score, ylabel, f"{name} — {ylabel} на валидации",
        figures / f"{name.lower()}_validation.pdf",
    )

    # Full-dataset descriptive statistics are only used for reporting.
    columns = dict(zip(dataset.feature_names, features.T))
    class_counts = None
    if classification:
        labels, counts = np.unique(targets, return_counts=True)
        class_counts = labels, counts
        write_csv(results / "class_counts.csv", [
            {"class": label, "count": count, "fraction": count / len(targets)}
            for label, count in zip(labels, counts)
        ])
    else:
        columns["target"] = targets
    write_csv(results / "descriptive_statistics.csv", describe(columns))
    distributions(
        columns, f"{name} — распределения исходных данных",
        figures / f"{name.lower()}_distributions.pdf", class_counts,
    )
    print(f"{name}: train/validation/test = {len(train)}/{len(validation)}/{len(test)}")
    print(f"  k={best['k']}, {best['distance']}, validation {score}={best[score]:.6f}")
    print("  Test:", ", ".join(f"{key}={value:.6f}" for key, value in scores.items()))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--results", type=Path, default=ROOT / "results")
    parser.add_argument("--figures", type=Path, default=ROOT / "report" / "figures")
    args = parser.parse_args()
    run(load_wine(), "classification", "Wine", args.results, args.figures)
    run(load_diabetes(scaled=False), "regression", "Diabetes", args.results, args.figures)


if __name__ == "__main__":
    main()
