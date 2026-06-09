# GC Pressure Performance Problem — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Inject an intentional GC pressure problem (String `+=` in loop) into `PointBean.checkPoint()`, document VisualVM-based location steps, then fix it with `StringBuilder`.

**Architecture:** Single-file change in `PointBean.java`. The problem code lives just before `checkHit()` call — the hot path for every point-check request. The fix replaces `+=` with `StringBuilder.append()`.

**Tech Stack:** Java EE (JSF + EJB), no new dependencies.

---

### Task 1: Inject GC Pressure Problem

**Files:**
- Modify: `src/main/java/com/itmo/bean/PointBean.java:41`

- [ ] **Step 1: Add the String concatenation loop before `checkHit()` call**

Open `src/main/java/com/itmo/bean/PointBean.java` and replace the `checkPoint()` method's body from line 40 (`boolean hit = checkHit(x, y, r);`) to include the problem code before it:

```java
// ═══════════════════════════════════════════════════════════════
// ИСКУССТВЕННАЯ ПРОБЛЕМА: конкатенация String в цикле
// Создает ~50 000 временных объектов за один запрос → GC pressure
// Будет найдена через VisualVM CPU Profiler и исправлена
// ═══════════════════════════════════════════════════════════════
String debugLog = "";
for (int i = 0; i < 50000; i++) {
    debugLog += "Point[" + i + "]=(" + x + "," + y + "," + r + ") ";
}
// ═══════════════════════════════════════════════════════════════

long startTime = System.currentTimeMillis();
boolean hit = checkHit(x, y, r);
```

- [ ] **Step 2: Verify compilation**

Run: `mvn compile -q`
Expected: BUILD SUCCESS

- [ ] **Step 3: Commit the problem injection**

```bash
git add src/main/java/com/itmo/bean/PointBean.java
git commit -m "feat: inject intentional GC pressure problem (String += in loop) for lab task 4"
```

---

### Task 2: Fix the Problem

**Files:**
- Modify: `src/main/java/com/itmo/bean/PointBean.java:41-48`

- [ ] **Step 1: Replace String `+=` with `StringBuilder`**

Replace the injected problem block:

```java
// Исправлено: StringBuilder вместо String += в цикле
// StringBuilder мутабелен — не создает временных объектов при каждой конкатенации
StringBuilder debugLog = new StringBuilder();
for (int i = 0; i < 50000; i++) {
    debugLog.append("Point[").append(i).append("]=(")
            .append(x).append(",").append(y).append(",").append(r).append(") ");
}
```

- [ ] **Step 2: Verify compilation**

Run: `mvn compile -q`
Expected: BUILD SUCCESS

- [ ] **Step 3: Commit the fix**

```bash
git add src/main/java/com/itmo/bean/PointBean.java
git commit -m "fix: replace String += with StringBuilder to eliminate GC pressure"
```

---

### VisualVM Analysis Guide (for lab report)

**Setup:**
1. Запустить приложение (Payara/GlassFish/TomEE)
2. Открыть VisualVM, найти процесс сервера приложений
3. Подключиться к процессу

**До исправления (Task 1):**
1. Вкладка **Monitor** → наблюдать пилообразный график памяти и частые GC
2. Вкладка **Profiler → CPU** → нажать "Profile", выполнить 5-10 запросов в веб-интерфейсе
3. Горячие методы: `StringBuilder.append()`, `String.toString()` с высоким Self Time
4. Через стек-трейс перейти к `PointBean.checkPoint()` — строка `debugLog += ...`
5. Сделать скриншоты: Monitor (память + GC), CPU Profiler, стек-трейс

**После исправления (Task 2):**
1. Перезапустить приложение с исправленным кодом
2. Повторить те же 5-10 запросов
3. Вкладка **Monitor** — GC активность снижена, память стабильнее
4. Вкладка **Profiler → CPU** — `StringBuilder.append()` больше не в топе
5. Сделать скриншоты для сравнения "до/после"
