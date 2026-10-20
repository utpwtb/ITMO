"""Apply the stored training preprocessing and model to a passenger CSV."""

import argparse
import json
from pathlib import Path

import numpy as np
import pandas as pd

from titanic.data import Preprocessor
from titanic.model import sigmoid

ROOT = Path(__file__).resolve().parents[2]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument(
        "--model", type=Path, default=ROOT / "results/model/logistic.json"
    )
    arguments = parser.parse_args()
    if arguments.input.resolve() == arguments.output.resolve():
        parser.error("Output must differ from the input file")
    state = json.loads(arguments.model.read_text(encoding="utf-8"))
    frame = pd.read_csv(arguments.input)
    matrix = Preprocessor.from_dict(state["preprocessing"]).transform(frame)
    probabilities = sigmoid(matrix @ np.asarray(state["weights"]))
    result = pd.DataFrame(
        {
            "PassengerId": frame.PassengerId,
            "probability": probabilities,
            "Survived": (probabilities >= state["threshold"]).astype(int),
        }
    )
    arguments.output.parent.mkdir(parents=True, exist_ok=True)
    result.to_csv(arguments.output, index=False)
    print(f"Saved {len(result)} predictions to {arguments.output}")


if __name__ == "__main__":
    main()
