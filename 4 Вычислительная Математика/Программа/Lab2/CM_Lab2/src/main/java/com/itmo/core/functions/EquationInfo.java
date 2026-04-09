package com.itmo.core.functions;

import lombok.AllArgsConstructor;
import lombok.Getter;

@Getter
@AllArgsConstructor
public class EquationInfo {
    private final String name;
    private final Function function;
    private final Function derivative;
    private final Function secondDerivative;
    private final String equationString;
    private final double defaultA;
    private final double defaultB;
}

