# Lab 6: ODE Numerical Solver Implementation Plan

> **Goal:** Java Swing GUI application for solving first-order ODE Cauchy problems using Improved Euler, RK4, and Milne methods (Variant 14).

**Architecture:** Layered design — ODE definitions (interface), numerical methods (pure computation), GUI (Swing, top-bottom layout with input above and results+plot below), model classes for data transfer.

**Tech Stack:** Java 17, Maven, javax.swing, java.awt (Graphics2D for plotting)

---

### Task 1: Project scaffolding and ODE definitions

**Files:**
- Create: `src/main/java/com/itmo/Main.java`
- Create: `src/main/java/com/itmo/ode/ODE.java`
- Create: `src/main/java/com/itmo/ode/ODE1.java`
- Create: `src/main/java/com/itmo/ode/ODE2.java`
- Create: `src/main/java/com/itmo/ode/ODE3.java`

### Task 2: Numerical methods (pure computation)

**Files:**
- Create: `src/main/java/com/itmo/methods/ImprovedEulerMethod.java`
- Create: `src/main/java/com/itmo/methods/RungeKuttaMethod.java`
- Create: `src/main/java/com/itmo/methods/MilneMethod.java`

### Task 3: Data model

**Files:**
- Create: `src/main/java/com/itmo/model/SolveResult.java`

### Task 4: GUI — Main frame and input panel

**Files:**
- Create: `src/main/java/com/itmo/gui/MainFrame.java`
- Create: `src/main/java/com/itmo/gui/InputPanel.java`

### Task 5: GUI — Results table and plot

**Files:**
- Create: `src/main/java/com/itmo/gui/ResultTablePanel.java`
- Create: `src/main/java/com/itmo/gui/PlotPanel.java`

### Task 6: Integration and testing

**Files:**
- Modify: `src/main/java/com/itmo/Main.java` (wire everything together)

### Task 7: LaTeX report

**Files:**
- Create: `report/main.tex`
- Create: `report/title.tex`
- Create: `report/1.tex`
- Create: `report/2.tex`
