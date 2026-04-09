package com.itmo.core.functions;

import java.util.List;

public final class SystemRepository {
    private static final List<SystemInfo> SYSTEMS = List.of(
        new SystemInfo(
            (x, y) -> 2 * x + Math.sin(y) - 0.4,
            (x, y) -> 2 * y - Math.cos(x) - 1,
            (x, y) -> (0.4 - Math.sin(y)) / 2,
            (x, y) -> (1 + Math.cos(x)) / 2,
            (x, y) -> 0,
            (x, y) -> -Math.cos(y) / 2,
            (x, y) -> -Math.sin(x) / 2,
            (x, y) -> 0,
            "2x + sin(y) - 0.4 = 0",
            "2y - cos(x) - 1 = 0",
            "φ₁(x,y) = (0.4 - sin(y)) / 2",
            "φ₂(x,y) = (1 + cos(x)) / 2"
        ),
        new SystemInfo(
            (x, y) -> Math.sin(y) + 2 * x - 2,
            (x, y) -> y + Math.cos(x) - 1.4 * x - 0.7,
            (x, y) -> (2 - Math.sin(y)) / 2,
            (x, y) -> 1.4 * x + 0.7 - Math.cos(x),
            (x, y) -> 0,
            (x, y) -> -Math.cos(y) / 2,
            (x, y) -> 1.4 + Math.sin(x),
            (x, y) -> 0,
            "sin(y) + 2x = 2",
            "y + cos(x) - 1.4x = 0.7",
            "φ₁(x,y) = (2 - sin(y)) / 2",
            "φ₂(x,y) = 1.4x + 0.7 - cos(x)"
        ),
        new SystemInfo(
            (x, y) -> Math.sin(x + y) - 1.4 * x,
            (x, y) -> x * x + y * y - 1,
            (x, y) -> Math.sin(x + y) / 1.4,
            (x, y) -> Math.sqrt(Math.max(0, 1 - x * x)),
            (x, y) -> Math.cos(x + y) / 1.4,
            (x, y) -> Math.cos(x + y) / 1.4,
            (x, y) -> x == 0 ? 0 : (x < 0 ? 1 / Math.sqrt(1 - x * x) : -x / Math.sqrt(1 - x * x)),
            (x, y) -> 0,
            "sin(x+y) - 1.4x = 0",
            "x² + y² = 1",
            "φ₁(x,y) = sin(x+y) / 1.4",
            "φ₂(x,y) = √(1 - x²)"
        )
    );

    private SystemRepository() {}

    public static List<SystemInfo> getAllSystems() {
        return SYSTEMS;
    }
}
