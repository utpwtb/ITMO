package com.itmo.core.model;

import lombok.AccessLevel;
import lombok.AllArgsConstructor;
import lombok.Getter;

@Getter
@AllArgsConstructor
public class RootCheckResult {
    @Getter(AccessLevel.NONE)
    private final boolean hasRoot;
    private final int rootCount;
    private final String message;

    public boolean hasRoot() { return hasRoot; }
}

