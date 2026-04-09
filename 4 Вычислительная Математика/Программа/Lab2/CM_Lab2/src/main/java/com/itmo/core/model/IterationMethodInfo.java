package com.itmo.core.model;

import lombok.AllArgsConstructor;
import lombok.Getter;

import java.util.function.DoubleUnaryOperator;

@Getter
@AllArgsConstructor
public class IterationMethodInfo {
    private final DoubleUnaryOperator phi;
    private final DoubleUnaryOperator phiDerivative;
    private final String message;
    private final boolean canApply;
}
