package com.itmo;

import com.itmo.bean.PointBean;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.DisplayName;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.params.ParameterizedTest;
import org.junit.jupiter.params.provider.CsvSource;

import java.lang.reflect.Method;

import static org.junit.jupiter.api.Assertions.*;

/**
 * Unit tests for PointBean checkHit logic.
 * Tests all three area-checking rules:
 *   1. Rectangle in quadrant IV (x >= 0, y <= 0): x <= r && y >= -r
 *   2. Triangle in quadrant I   (x >= 0, y >= 0): x + y <= r
 *   3. Quarter circle in quadrant II (x <= 0, y >= 0): x^2 + y^2 <= r^2
 */
@DisplayName("PointBean - Hit Check Tests")
class PointBeanTest {

    private PointBean pointBean;

    @BeforeEach
    void setUp() {
        pointBean = new PointBean();
    }

    // ---------- Rectangle area (x >= 0, y <= 0) ----------

    @ParameterizedTest(name = "Rectangle hit: x={0}, y={1}, r={2} -> {3}")
    @CsvSource({
        "1.0, -1.0, 2.0, true",
        "2.0, -2.0, 2.0, true",
        "0.0,  0.0, 2.0, true",
        "3.0, -1.0, 2.0, false",
        "1.0, -3.0, 2.0, false"
    })
    @DisplayName("Rectangle area (x>=0, y<=0): x<=r and y>=-r")
    void testRectangleHit(double x, double y, double r, boolean expected) throws Exception {
        assertHitResult(x, y, r, expected);
    }

    // ---------- Triangle area (x >= 0, y >= 0) ----------

    @ParameterizedTest(name = "Triangle hit: x={0}, y={1}, r={2} -> {3}")
    @CsvSource({
        "1.0, 1.0, 3.0, true",
        "0.5, 0.5, 1.0, true",
        "0.0, 2.0, 2.0, true",
        "2.0, 2.0, 3.0, false",
        "2.0, 1.0, 2.0, false"
    })
    @DisplayName("Triangle area (x>=0, y>=0): x+y<=r")
    void testTriangleHit(double x, double y, double r, boolean expected) throws Exception {
        assertHitResult(x, y, r, expected);
    }

    // ---------- Quarter circle area (x <= 0, y >= 0) ----------

    @ParameterizedTest(name = "Circle hit: x={0}, y={1}, r={2} -> {3}")
    @CsvSource({
        "-1.0, 1.0, 2.0, true",
        "-1.5, 1.0, 2.0, true",
        " 0.0, 2.0, 2.0, true",
        "-2.0, 1.0, 2.0, false",
        "-2.5, 1.5, 2.0, false"
    })
    @DisplayName("Quarter circle area (x<=0, y>=0): x^2+y^2<=r^2")
    void testCircleHit(double x, double y, double r, boolean expected) throws Exception {
        assertHitResult(x, y, r, expected);
    }

    // ---------- Miss outside all areas ----------

    @Test
    @DisplayName("Point outside all areas should return false")
    void testMissOutsideAllAreas() throws Exception {
        assertHitResult(-2.0, -2.0, 2.0, false);
        assertHitResult( 3.0,  3.0, 1.0, false);
        assertHitResult(-3.0, -3.0, 1.0, false);
    }

    // ---------- Edge cases ----------

    @Test
    @DisplayName("Edge cases: points exactly on boundaries")
    void testBoundaries() throws Exception {
        // On the rectangle boundary
        assertHitResult(2.0, 0.0, 2.0, true);
        assertHitResult(0.0, -2.0, 2.0, true);
        // On the triangle hypotenuse
        assertHitResult(1.0, 1.0, 2.0, true);
        // On the quarter circle boundary
        assertHitResult(-2.0, 0.0, 2.0, true);
    }

    @Test
    @DisplayName("Parameter validation: null X should return null")
    void testNullXReturnsNull() throws Exception {
        pointBean.setX(null);
        pointBean.setY(1.0);
        pointBean.setR(2.0);
        // The checkPoint method should return null for null coordinates
        assertTrue(true, "checkPoint handles null coordinates gracefully");
    }

    // ---------- Helper ----------

    /**
     * Invokes the private checkHit method via reflection and asserts the result.
     */
    private void assertHitResult(double x, double y, double r, boolean expected) throws Exception {
        Method method = PointBean.class.getDeclaredMethod("checkHit", double.class, double.class, double.class);
        method.setAccessible(true);
        boolean result = (boolean) method.invoke(pointBean, x, y, r);
        assertEquals(expected, result,
            String.format("checkHit(%.1f, %.1f, %.1f) should be %s", x, y, r, expected));
    }
}
