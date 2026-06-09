# GC Pressure Performance Problem — Design

## Scope
Introduce an intentional performance problem (excessive GC pressure via String concatenation in a loop), use VisualVM to locate it, fix it, and document findings for lab task 4.

## Problem Injection
- **Location:** `PointBean.checkPoint()`, before `checkHit()` call
- **Code:** String `+=` concatenation in a 50 000-iteration loop, producing ~50k temporary String/StringBuilder objects per request
- **Effect:** Each request triggers minor GC spikes due to short-lived object allocation churn

## Fix
- Replace `String +=` with `StringBuilder.append()` (or remove the mock code entirely, since it serves no real purpose)
- Before/after comparison via VisualVM

## VisualVM Analysis Flow
1. Connect VisualVM to running JVM process
2. Trigger several point-check requests
3. Monitor → Memory/GC: observe heap sawtooth and frequent minor GC
4. Profiler → CPU: identify `StringBuilder.append()` / `String` constructors as hot methods
5. Stack trace → `PointBean.checkPoint()` — pinpoint the offending line
6. Apply fix, re-run profiler, confirm GC activity normalizes

## Files Changed
- `src/main/java/com/itmo/bean/PointBean.java` — inject then fix the problem

## Report Contents (for lab task 4)
- Problem description (inefficient String concatenation creating GC pressure)
- VisualVM screenshots (CPU profiler hot spots, GC activity, before/after comparison)
- Step-by-step location procedure
- Solution description
