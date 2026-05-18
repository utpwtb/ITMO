package com.itmo.core.model;

import lombok.AllArgsConstructor;
import lombok.Getter;

@Getter
@AllArgsConstructor
public class SolveResult {
    private final double root;
    private final double functionValue;
    private final int iterations;
    private final boolean converged;
    private final String message;
}

