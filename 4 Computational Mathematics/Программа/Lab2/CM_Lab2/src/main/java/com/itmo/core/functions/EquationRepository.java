package com.itmo.core.functions;

import java.util.List;

public final class EquationRepository {
    private static final List<EquationInfo> EQUATIONS = List.of(
        new EquationInfo(
            "f(x) = x^3 - 2x - 5",
            x -> Math.pow(x, 3) - 2 * x - 5,
            x -> 3 * Math.pow(x, 2) - 2,
            x -> 6 * x,
            "x^3 - 2x - 5 = 0",
            -3, 3
        ),
        new EquationInfo(
            "f(x) = e^x - x - 2",
            x -> Math.exp(x) - x - 2,
            x -> Math.exp(x) - 1,
            x -> Math.exp(x),
            "e^x - x - 2 = 0",
            -2, 3
        ),
        new EquationInfo(
            "f(x) = sin(x) - x/2",
            x -> Math.sin(x) - x / 2,
            x -> Math.cos(x) - 0.5,
            x -> -Math.sin(x),
            "sin(x) - x/2 = 0",
            -3, 3
        ),
        new EquationInfo(
            "f(x) = x^2 - 10",
            x -> Math.pow(x, 2) - 10,
            x -> 2 * x,
            x -> 2.0,
            "x^2 - 10 = 0",
            -5, 5
        ),
        new EquationInfo(
            "f(x) = ln(x) + x - 2",
            x -> x > 0 ? Math.log(x) + x - 2 : Double.NaN,
            x -> x > 0 ? 1 / x + 1 : Double.NaN,
            x -> x > 0 ? -1 / (x * x) : Double.NaN,
            "ln(x) + x - 2 = 0",
            0.1, 5
        )
    );

    private EquationRepository() {}

    public static List<EquationInfo> getAllEquations() {
        return EQUATIONS;
    }
}
