package com.itmo.jmx;

/**
 * MBean interface that calculates the total area of the target figure.
 *
 * <p>The figure consists of three geometric shapes bounded by radius R:</p>
 * <ul>
 *   <li><b>Q1 (x&ge;0, y&ge;0):</b> right triangle, area = R&sup2;/2</li>
 *   <li><b>Q2 (x&le;0, y&ge;0):</b> quarter-circle, area = &pi;R&sup2;/4</li>
 *   <li><b>Q4 (x&ge;0, y&le;0):</b> rectangle, area = R&sup2;</li>
 * </ul>
 *
 * <p>Total area = R&sup2; &times; (6 + &pi;) / 4</p>
 */
public interface AreaCalculatorMBean {

    /**
     * Compute the total area of the figure for the given radius.
     *
     * @param r radius (must be &gt; 0)
     * @return total area of all three regions
     */
    double getArea(double r);

    /** Human-readable description of the figure and its area formula. */
    String getFigureDescription();

    /** Update the shared radius value (called when a point check is performed). */
    void setCurrentR(double r);

    /** Return the most recently used radius value. */
    double getCurrentR();

    /** Return the area computed for the most recently used R value. */
    double getCurrentArea();
}
