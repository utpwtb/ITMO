"""Численные и независимые проверки алгоритма: python test_model.py."""
import unittest
import numpy as np
import pandas as pd
from model import *


class Tests(unittest.TestCase):
    def test_extreme_logits(self):
        with np.errstate(over='raise', invalid='raise'):
            np.testing.assert_allclose(sigmoid([-1000, 0, 1000]), [0, .5, 1])
            self.assertEqual(log_loss(np.array([1, 0]), np.array([-1000, 1000])), 1000)

    def test_gradient_and_hessian(self):
        rng = np.random.default_rng(17)
        X = np.column_stack([np.ones(20), rng.normal(size=(20, 3))])
        y = rng.integers(0, 2, 20)
        w = rng.normal(size=4)
        grad, hess = derivatives(X, y, w)
        epsilon = 1e-5
        numeric_grad, numeric_hess = [], []
        for d in np.eye(4) * epsilon:
            numeric_grad.append((log_loss(y, X @ (w+d)) - log_loss(y, X @ (w-d))) / (2*epsilon))
            numeric_hess.append((derivatives(X,y,w+d)[0] - derivatives(X,y,w-d)[0]) / (2*epsilon))
        np.testing.assert_allclose(grad, numeric_grad, atol=1e-8)
        np.testing.assert_allclose(hess, np.array(numeric_hess).T, atol=1e-8)

    def test_known_metrics(self):
        m = metrics(np.array([0,0,0,1,1,1]), np.array([0,0,1,0,1,1]))
        self.assertEqual([m[k] for k in ['tn','fp','fn','tp']], [2,1,1,2])
        for k in ['accuracy','precision','recall','f1']:
            self.assertAlmostEqual(m[k], 2/3)
        self.assertEqual(metrics(np.array([0,1]), np.array([0,0]))['f1'], 0)

    def test_split(self):
        y = np.array([0]*500 + [1]*268)
        a,b = stratified_split(y)
        self.assertEqual(len(a), 614)
        self.assertEqual(len(b), 154)
        self.assertEqual(len(set(a) & set(b)), 0)
        self.assertEqual(len(set(a) | set(b)), 768)
        np.testing.assert_array_equal(a, stratified_split(y)[0])

    def test_preprocessing(self):
        train = pd.DataFrame(np.arange(32).reshape(4,8)+1, columns=FEATURES)
        train.loc[0,'Glucose'] = 0
        train.loc[0,'Pregnancies'] = 0
        prep = Preprocessor().fit(train)
        before = prep.to_dict()
        transformed = prep.transform(train)
        np.testing.assert_allclose(transformed[:,1:].mean(0), 0, atol=1e-14)
        self.assertEqual(Preprocessor.clean(train).iloc[0,0], 0)
        prep.transform(train*10000)
        self.assertEqual(before, prep.to_dict())

    def test_optimizers_agree(self):
        rng = np.random.default_rng(8)
        X = np.column_stack([np.ones(200), rng.normal(size=(200,3))])
        y = (rng.random(200) < sigmoid(X @ np.array([-.3,.8,-.5,.4]))).astype(int)
        gd = LogisticRegression('gd', .5, 2000).fit(X,y)
        newton = LogisticRegression('newton', 1, 20).fit(X,y)
        np.testing.assert_allclose(gd.weights, newton.weights, atol=1e-7)
        self.assertTrue(np.all(np.diff(gd.loss_history) <= 1e-12))
        self.assertLess(np.max(np.abs(derivatives(X,y,newton.weights)[0])), 1e-10)


if __name__ == '__main__':
    unittest.main(verbosity=2)
