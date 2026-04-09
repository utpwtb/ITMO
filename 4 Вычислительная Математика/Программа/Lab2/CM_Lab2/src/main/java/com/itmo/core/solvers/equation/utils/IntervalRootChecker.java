package com.itmo.core.solvers.equation.utils;

import com.itmo.core.model.RootCheckResult;
import com.itmo.core.functions.Function;

public class IntervalRootChecker {
    public RootCheckResult checkRoot(Function f, double a, double b, int samplePoints) {
        double h = (b - a) / samplePoints;
        int signChanges = 0;
        double prevValue = f.evaluate(a);

        if (Double.isNaN(prevValue) || Double.isInfinite(prevValue)) {
            return new RootCheckResult(false, 0,
                "Функция не определена на границе a = " + a);
        }

        for (int i = 1; i <= samplePoints; i++) {
            double x = a + i * h;
            double value = f.evaluate(x);

            if (Double.isNaN(value) || Double.isInfinite(value)) {
                continue;
            }

            if (prevValue * value < 0) {
                signChanges++;
            }
            prevValue = value;
        }

        if (signChanges == 0) {
            double fa = f.evaluate(a);
            double fb = f.evaluate(b);
            if (Math.abs(fa) < 1e-10) {
                return new RootCheckResult(true, 1,
                    "Корень находится на границе a = " + a);
            }
            if (Math.abs(fb) < 1e-10) {
                return new RootCheckResult(true, 1,
                    "Корень находится на границе b = " + b);
            }
            return new RootCheckResult(false, 0,
                "На указанном интервале корней не обнаружено.");
        } else if (signChanges == 1) {
            return new RootCheckResult(true, 1,
                "На интервале обнаружен один корень.");
        } else {
            return new RootCheckResult(true, signChanges,
                "На интервале обнаружено несколько корней (примерно " + signChanges +
                "). Рекомендуется сузить интервал.");
        }
    }
}
