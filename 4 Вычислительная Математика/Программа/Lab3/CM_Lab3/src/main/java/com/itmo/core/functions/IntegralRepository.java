package com.itmo.core.functions;

import java.util.List;

public final class IntegralRepository {
    private static final List<IntegralFunctionInfo> FUNCTIONS = List.of(
        new IntegralFunctionInfo(
            "f(x) = sin(x)",
            x -> Math.sin(x),
            false,
            new double[0]
        ),
        new IntegralFunctionInfo(
            "f(x) = x^2",
            x -> x * x,
            false,
            new double[0]
        ),
        new IntegralFunctionInfo(
            "f(x) = e^x",
            x -> Math.exp(x),
            false,
            new double[0]
        ),
        new IntegralFunctionInfo(
            "f(x) = 1 / (1 + x^2)",
            x -> 1.0 / (1 + x * x),
            false,
            new double[0]
        ),
        new IntegralFunctionInfo(
            "f(x) = sqrt(x)",
            x -> Math.sqrt(x),
            false,
            new double[0]
        ),
        new IntegralFunctionInfo(
            "f(x) = 1 / sqrt(x)",
            x -> x > 0 ? 1.0 / Math.sqrt(x) : Double.POSITIVE_INFINITY,
            true,
            new double[]{0}
        ),
        new IntegralFunctionInfo(
            "f(x) = 1 / x^2",
            x -> x != 0 ? 1.0 / (x * x) : Double.POSITIVE_INFINITY,
            true,
            new double[]{0}
        ),
        new IntegralFunctionInfo(
            "f(x) = 1 / x",
            x -> x != 0 ? 1.0 / x : Double.NaN,
            true,
            new double[]{0}
        ),
        new IntegralFunctionInfo(
            "f(x) = ln(x)",
            x -> x > 0 ? Math.log(x) : Double.NEGATIVE_INFINITY,
            true,
            new double[]{0}
        ),
        new IntegralFunctionInfo(
            "f(x) = 1 / sqrt(1 - x^2)",
            x -> Math.abs(x) < 1 ? 1.0 / Math.sqrt(1 - x * x) : Double.POSITIVE_INFINITY,
            true,
            new double[]{-1, 1}
        )
    );

    private IntegralRepository() {}

    public static List<IntegralFunctionInfo> getAllFunctions() {
        return FUNCTIONS;
    }
}
