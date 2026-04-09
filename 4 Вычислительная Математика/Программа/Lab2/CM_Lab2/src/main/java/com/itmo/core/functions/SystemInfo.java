package com.itmo.core.functions;

import lombok.AllArgsConstructor;
import lombok.Getter;

@Getter
@AllArgsConstructor
public class SystemInfo {
    private final SystemFunction2D f1;
    private final SystemFunction2D f2;
    private final SystemFunction2D phi1;
    private final SystemFunction2D phi2;
    private final SystemFunction2D dphi1dx;
    private final SystemFunction2D dphi1dy;
    private final SystemFunction2D dphi2dx;
    private final SystemFunction2D dphi2dy;
    private final String eq1String;
    private final String eq2String;
    private final String phi1String;
    private final String phi2String;
}
