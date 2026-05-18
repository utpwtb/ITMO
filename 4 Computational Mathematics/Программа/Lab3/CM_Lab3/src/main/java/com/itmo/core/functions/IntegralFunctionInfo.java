package com.itmo.core.functions;

import lombok.AllArgsConstructor;
import lombok.Getter;

@Getter
@AllArgsConstructor
public class IntegralFunctionInfo {
    private final String name;
    private final String expression;
    private final Function function;
    private final boolean isImproper;
    private final double[] discontinuityPoints;
    private final double defaultA;
    private final double defaultB;
}
