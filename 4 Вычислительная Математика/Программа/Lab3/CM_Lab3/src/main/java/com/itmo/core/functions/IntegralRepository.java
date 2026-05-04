package com.itmo.core.functions;

import java.util.List;
import java.util.stream.Collectors;

public final class IntegralRepository {
    private static final List<IntegralFunctionInfo> FUNCTIONS = List.of(
        new IntegralFunctionInfo(
            "f(x) = sin(x)",
            "sin(x)",
            x -> Math.sin(x),
            false,
            new double[0],
            0, Math.PI
        ),
        new IntegralFunctionInfo(
            "f(x) = x^2",
            "x^2",
            x -> x * x,
            false,
            new double[0],
            0, 3
        ),
        new IntegralFunctionInfo(
            "f(x) = e^x",
            "e^x",
            x -> Math.exp(x),
            false,
            new double[0],
            0, 1
        ),
        new IntegralFunctionInfo(
            "f(x) = 1 / (1 + x^2)",
            "1/(1+x^2)",
            x -> 1.0 / (1 + x * x),
            false,
            new double[0],
            -1, 1
        ),
        new IntegralFunctionInfo(
            "f(x) = sqrt(x)",
            "sqrt(x)",
            x -> Math.sqrt(x),
            false,
            new double[0],
            0, 4
        ),

        new IntegralFunctionInfo(
            "f(x) = 1 / sqrt(x)  [广义积分]",
            "1/sqrt(x)",
            x -> x > 0 ? 1.0 / Math.sqrt(x) : Double.POSITIVE_INFINITY,
            true,
            new double[]{0},
            0, 1
        ),
        new IntegralFunctionInfo(
            "f(x) = 1 / x^2  [广义积分]",
            "1/x^2",
            x -> x != 0 ? 1.0 / (x * x) : Double.POSITIVE_INFINITY,
            true,
            new double[]{0},
            0, 1
        ),
        new IntegralFunctionInfo(
            "f(x) = 1 / x  [广义积分，对称抵消]",
            "1/x",
            x -> x != 0 ? 1.0 / x : Double.NaN,
            true,
            new double[]{0},
            -1, 2
        ),
        new IntegralFunctionInfo(
            "f(x) = ln(x)  [广义积分]",
            "ln(x)",
            x -> x > 0 ? Math.log(x) : Double.NEGATIVE_INFINITY,
            true,
            new double[]{0},
            0, 1
        ),
        new IntegralFunctionInfo(
            "f(x) = 1 / sqrt(1 - x^2)  [广义积分]",
            "1/sqrt(1-x^2)",
            x -> Math.abs(x) < 1 ? 1.0 / Math.sqrt(1 - x * x) : Double.POSITIVE_INFINITY,
            true,
            new double[]{-1, 1},
            -1, 1
        )
    );

    private IntegralRepository() {}

    public static List<IntegralFunctionInfo> getAllFunctions() {
        return FUNCTIONS;
    }

    public static List<IntegralFunctionInfo> getRegularFunctions() {
        return FUNCTIONS.stream()
                .filter(f -> !f.isImproper())
                .collect(Collectors.toList());
    }

    public static List<IntegralFunctionInfo> getImproperFunctions() {
        return FUNCTIONS.stream()
                .filter(IntegralFunctionInfo::isImproper)
                .collect(Collectors.toList());
    }
}
