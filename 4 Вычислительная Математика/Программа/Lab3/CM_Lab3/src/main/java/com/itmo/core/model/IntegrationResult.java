package com.itmo.core.model;

import lombok.AllArgsConstructor;
import lombok.Getter;

@Getter
@AllArgsConstructor
public class IntegrationResult {
    private final double integralValue;
    private final int subdivisions;
    private final double estimatedError;
    private final String methodName;
    private final String functionName;
}
