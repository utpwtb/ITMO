"""Train four NumPy MLPs, select on validation, and evaluate on MNIST test."""

import argparse
import csv
from pathlib import Path

import numpy as np

from mnist import load_split, one_hot
from network import Adam, MLP, SoftmaxWithLoss, gradient_check, save_model

ROOT = Path(__file__).resolve().parents[1]
SEED = 42
BATCH_SIZE = 256
EVAL_BATCH_SIZE = 1024
LEARNING_RATE = 0.001
CONFIGS = (
    ("A", (128,), 0.0),
    ("B", (256,), 0.0),
    ("C", (256, 128), 0.0),
    ("D", (256, 128), 0.2),
)


def write_csv(path, columns, rows):
    with path.open("w", encoding="utf-8", newline="") as file:
        writer = csv.writer(file)
        writer.writerow(columns)
        writer.writerows(rows)


def evaluate(model, images, targets):
    """Measure loss and accuracy with a single fixed model and no Dropout."""
    objective = SoftmaxWithLoss()
    loss_sum, predictions = 0.0, []
    for start in range(0, len(images), EVAL_BATCH_SIZE):
        batch = slice(start, start + EVAL_BATCH_SIZE)
        logits = model.forward(images[batch])
        loss_sum += len(logits) * objective.forward(logits, targets[batch])
        predictions.append(np.argmax(logits, axis=1))
    predicted = np.concatenate(predictions)
    accuracy = np.mean(predicted == np.argmax(targets, axis=1))
    return loss_sum / len(images), float(accuracy), predicted


def train(config, train_x, train_y, val_x, val_y, epochs):
    name, widths, dropout = config
    model = MLP(widths, dropout, SEED)
    best_model = MLP(widths, dropout, SEED)
    optimizer = Adam(model.parameters(), lr=LEARNING_RATE)
    objective = SoftmaxWithLoss()
    shuffle = np.random.default_rng(SEED + 1)
    history = []
    best_epoch, best_accuracy = 0, -1.0
    for epoch in range(1, epochs + 1):
        order = shuffle.permutation(len(train_x))
        for start in range(0, len(order), BATCH_SIZE):
            batch = order[start:start + BATCH_SIZE]
            logits = model.forward(train_x[batch], training=True)
            objective.forward(logits, train_y[batch])
            model.backward(objective.backward())
            optimizer.step()

        train_loss, train_acc, _ = evaluate(model, train_x, train_y)
        val_loss, val_acc, _ = evaluate(model, val_x, val_y)
        history.append((name, epoch, train_loss, train_acc, val_loss, val_acc))
        print(f"{name} {epoch:2d}  loss {train_loss:.5f}/{val_loss:.5f}"
              f"  accuracy {train_acc:.4%}/{val_acc:.4%}", flush=True)

        # Strict comparison keeps the earliest checkpoint when accuracy ties.
        if val_acc > best_accuracy:
            best_epoch, best_accuracy = epoch, val_acc
            for (destination, _), (source, _) in zip(best_model.parameters(), model.parameters()):
                destination[...] = source
    return best_model, best_epoch, best_accuracy, history


def run(data_dir, output, weights, epochs):
    error = gradient_check()
    if error >= 1e-7:
        raise RuntimeError(f"Gradient check failed: {error:.3e}")
    print(f"Linear finite-difference max absolute error: {error:.3e}", flush=True)
    output.mkdir(parents=True, exist_ok=True)
    weights.parent.mkdir(parents=True, exist_ok=True)
    source_x, source_labels = load_split(data_dir, "train")
    order = np.random.default_rng(SEED).permutation(len(source_x))
    val_ids, train_ids = order[:6000], order[6000:]
    train_x, val_x = source_x[train_ids], source_x[val_ids]
    train_y, val_y = one_hot(source_labels[train_ids]), one_hot(source_labels[val_ids])
    print(f"MNIST source: {source_x.shape}; train: {train_x.shape}; validation: {val_x.shape}")
    for name, labels in (("train_full", source_labels), ("train", source_labels[train_ids]),
                         ("validation", source_labels[val_ids])):
        print(f"{name}: {np.bincount(labels, minlength=10)}", flush=True)

    all_history, summary = [], []
    winner, winning_model, winning_epoch, winning_accuracy = None, None, 0, -1.0
    for config in CONFIGS:
        name, widths, dropout = config
        best_model, best_epoch, best_accuracy, history = train(
            config, train_x, train_y, val_x, val_y, epochs
        )
        all_history.extend(history)
        parameters = sum(parameter.size for parameter, _ in best_model.parameters())
        summary.append((name, "-".join(map(str, widths)), dropout, parameters,
                        best_epoch, best_accuracy))
        if best_accuracy > winning_accuracy:
            winner, winning_model = name, best_model
            winning_epoch, winning_accuracy = best_epoch, best_accuracy

    save_model(weights, winning_model)
    test_x, test_labels = load_split(data_dir, "t10k")
    print(f"Test: {test_x.shape}; class counts: {np.bincount(test_labels, minlength=10)}")
    test_loss, test_accuracy, test_predictions = evaluate(winning_model, test_x, one_hot(test_labels))
    confusion = np.zeros((10, 10), dtype=np.int64)
    np.add.at(confusion, (test_labels, test_predictions), 1)
    print(f"Selected {winner}, epoch {winning_epoch}; test accuracy {test_accuracy:.4%}", flush=True)
    write_csv(output / "history.csv",
              ("model", "epoch", "train_loss", "train_accuracy", "val_loss", "val_accuracy"),
              all_history)
    write_csv(output / "architectures.csv",
              ("model", "hidden_widths", "dropout", "parameters", "best_epoch", "best_val_accuracy"),
              summary)
    write_csv(output / "test_metrics.csv",
              ("model", "epoch", "loss", "accuracy", "correct", "total"),
              [(winner, winning_epoch, test_loss, test_accuracy, np.trace(confusion), len(test_x))])
    write_csv(output / "confusion_matrix.csv", ("true/predicted", *range(10)),
              [(digit, *row) for digit, row in enumerate(confusion)])
    write_csv(output / "class_counts.csv", ("split", *range(10), "total"), [
        (name, *np.bincount(labels, minlength=10), len(labels))
        for name, labels in (("train_full", source_labels), ("train", source_labels[train_ids]),
                             ("validation", source_labels[val_ids]), ("test", test_labels))
    ])

    from figures import plot_results

    plot_results(output, all_history, source_x, source_labels, test_x,
                 test_labels, test_predictions, confusion, winning_model)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--data", type=Path, default=ROOT / "data/mnist")
    parser.add_argument("--output", type=Path, default=ROOT / "results")
    parser.add_argument("--weights", type=Path, default=ROOT / "models/best_model.npz")
    parser.add_argument("--epochs", type=int, default=12)
    args = parser.parse_args()
    if args.epochs < 1:
        parser.error("--epochs must be positive")
    run(args.data, args.output, args.weights, args.epochs)
