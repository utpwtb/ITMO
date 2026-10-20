"""Independent numerical and data-isolation checks, using unittest."""

import json
import unittest

import numpy as np
import pandas as pd

from titanic.data import Preprocessor, stratified_split
from titanic.experiment import ROOT
from titanic.metrics import classification_metrics
from titanic.model import LogisticRegression, derivatives, log_loss, sigmoid


class ModelTests(unittest.TestCase):
    def test_stability(self):
        with np.errstate(over="raise", invalid="raise"):
            np.testing.assert_allclose(sigmoid([-1000, 0, 1000]), [0, 0.5, 1])
            self.assertAlmostEqual(
                log_loss(np.array([1, 0]), np.array([-1000, 1000])), 1000
            )

    def test_gradient_and_hessian_against_finite_differences(self):
        matrix = np.array([[1, -1, 2], [1, 0.5, 1], [1, 2, -0.2], [1, -2, 1.3]])
        target = np.array([0, 1, 1, 0])
        weights = np.array([0.1, -0.2, 0.3])
        gradient, hessian = derivatives(matrix, target, weights)
        epsilon = 1e-5
        numerical_gradient = np.zeros(3)
        numerical_hessian = np.zeros((3, 3))
        for index in range(3):
            delta = np.eye(3)[index] * epsilon
            numerical_gradient[index] = (
                log_loss(target, matrix @ (weights + delta))
                - log_loss(target, matrix @ (weights - delta))
            ) / (2 * epsilon)
            numerical_hessian[:, index] = (
                derivatives(matrix, target, weights + delta)[0]
                - derivatives(matrix, target, weights - delta)[0]
            ) / (2 * epsilon)
        np.testing.assert_allclose(gradient, numerical_gradient, atol=1e-9)
        np.testing.assert_allclose(hessian, numerical_hessian, atol=1e-9)

    def test_optimizers_on_analytic_intercept_solution(self):
        matrix = np.ones((10, 1))
        target = np.array([1] * 7 + [0] * 3)
        for method, iterations in [("gd", 1000), ("newton", 10)]:
            model = LogisticRegression(method, 1.0, iterations).fit(matrix, target)
            self.assertAlmostEqual(model.weights[0], np.log(7 / 3), places=8)
            self.assertLess(model.loss_history[-1], model.loss_history[0])

    def test_metrics(self):
        metrics = classification_metrics([0, 0, 1, 1, 1], [0, 1, 0, 1, 1])
        self.assertEqual(
            [metrics[key] for key in ["tn", "fp", "fn", "tp"]], [1, 1, 1, 2]
        )
        self.assertAlmostEqual(metrics["accuracy"], 0.6)
        for key in ["precision", "recall", "f1"]:
            self.assertAlmostEqual(metrics[key], 2 / 3)
        self.assertEqual(classification_metrics([0, 1], [0, 0])["precision"], 0)


class DataTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.frame = pd.read_csv(ROOT / "data/raw/train.csv")

    def test_disjoint_stratified_split(self):
        train, test = stratified_split(self.frame.Survived)
        self.assertEqual((len(train), len(test)), (713, 178))
        self.assertFalse(set(train) & set(test))
        self.assertEqual(len(set(train) | set(test)), 891)
        np.testing.assert_array_equal(stratified_split(self.frame.Survived)[1], test)
        self.assertEqual(int(self.frame.iloc[test].Survived.sum()), 68)

    def test_preprocessing_freezes_training_statistics(self):
        train, test = stratified_split(self.frame.Survived)
        prep = Preprocessor().fit(self.frame.iloc[train])
        state = json.dumps(prep.to_dict(), sort_keys=True)
        held_out = self.frame.iloc[test].copy()
        held_out["Age"] = 10000.0
        matrix = prep.transform(held_out)
        self.assertEqual(matrix.shape, (178, 10))
        self.assertEqual(state, json.dumps(prep.to_dict(), sort_keys=True))
        np.testing.assert_allclose(
            matrix[:, 1], (10000 - prep.means.Age) / prep.scales.Age
        )
        matrix_train = prep.transform(self.frame.iloc[train])
        np.testing.assert_allclose(matrix_train[:, 1:5].mean(axis=0), 0, atol=1e-14)
        held_out["Age"] = np.nan
        np.testing.assert_allclose(
            prep.transform(held_out)[:, 1],
            (prep.medians.Age - prep.means.Age) / prep.scales.Age,
        )

    def test_reference_categories_and_round_trip(self):
        prep = Preprocessor().fit(self.frame)
        sample = self.frame.iloc[:1].copy()
        sample[["Sex", "Pclass", "Embarked"]] = ["female", 1, "C"]
        np.testing.assert_array_equal(prep.transform(sample)[0, 5:], np.zeros(5))
        sample[["Sex", "Pclass", "Embarked"]] = ["male", 3, "S"]
        np.testing.assert_array_equal(prep.transform(sample)[0, 5:], [1, 0, 1, 0, 1])
        restored = Preprocessor.from_dict(json.loads(json.dumps(prep.to_dict())))
        np.testing.assert_array_equal(
            restored.transform(sample), prep.transform(sample)
        )
        sample["Sex"] = "unknown"
        with self.assertRaises(ValueError):
            prep.transform(sample)

    def test_saved_results_match_model(self):
        state = json.loads((ROOT / "results/model/logistic.json").read_text())
        predictions = pd.read_csv(ROOT / "results/predictions/selected.csv")
        sample = self.frame.set_index("PassengerId").loc[predictions.PassengerId]
        matrix = Preprocessor.from_dict(state["preprocessing"]).transform(sample)
        probabilities = sigmoid(matrix @ np.array(state["weights"]))
        np.testing.assert_allclose(probabilities, predictions.probability, atol=1e-14)
        summary = json.loads((ROOT / "results/summary.json").read_text())
        metrics = classification_metrics(predictions.actual, probabilities >= 0.5)
        for key, value in metrics.items():
            self.assertAlmostEqual(summary["selected"][key], value)
        self.assertEqual(len(pd.read_csv(ROOT / "results/metrics/test.csv")), 21)


if __name__ == "__main__":
    unittest.main()
