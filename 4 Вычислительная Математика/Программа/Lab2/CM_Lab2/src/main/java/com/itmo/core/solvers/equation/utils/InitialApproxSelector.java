package com.itmo.core.solvers.equation.utils;

import com.itmo.core.functions.Function;

public class InitialApproxSelector {

    public static final class Result {
        public final boolean valid;
        public final double x0;
        public final String message;

        private Result(boolean valid, double x0, String message) {
            this.valid = valid;
            this.x0 = x0;
            this.message = message;
        }
    }

    public static Result selectByNewtonRule(Function f, Function d2f, double a, double b) {
        double fa = f.evaluate(a);
        double fb = f.evaluate(b);
        double d2fa = d2f.evaluate(a);
        double d2fb = d2f.evaluate(b);

        if (fa * d2fa > 0) {
            return new Result(true, a,
                String.format("f(a)·f''(a) = %.6f > 0: выбрано x₀ = a", fa * d2fa));
        } else if (fb * d2fb > 0) {
            return new Result(true, b,
                String.format("f(b)·f''(b) = %.6f > 0: выбрано x₀ = b", fb * d2fb));
        } else {
            return new Result(false, Double.NaN,
                String.format("Условие f(x₀)·f''(x₀) > 0 не выполняется ни на a, ни на b. " +
                    "f(a)·f''(a) = %.6f, f(b)·f''(b) = %.6f. " +
                    "Невозможно гарантировать сходимость метода.",
                    fa * d2fa, fb * d2fb));
        }
    }
}
