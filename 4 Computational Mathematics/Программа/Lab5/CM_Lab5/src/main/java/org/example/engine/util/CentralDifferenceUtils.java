package org.example.engine.util;

public class CentralDifferenceUtils {

    public static double factorial(int k) {
        double f = 1.0;
        for (int i = 2; i <= k; i++) {
            f *= i;
        }
        return f;
    }

    /** Gauss forward coefficient for k-th term, with parameter t = (x - a)/h */
    public static double gaussForwardCoeff(double t, int k) {
        double prod = 1.0;
        if (k % 2 == 1) {
            // odd: shifts from -(k-1)/2 to (k-1)/2
            int m = (k - 1) / 2;
            for (int s = -m; s <= m; s++) {
                prod *= (t + s);
            }
        } else {
            // even: shifts from -k/2 to k/2-1
            int start = -k / 2;
            int end = k / 2 - 1;
            for (int s = start; s <= end; s++) {
                prod *= (t + s);
            }
        }
        return prod / factorial(k);
    }

    /** Gauss backward coefficient for k-th term, with parameter t = (x - a)/h */
    public static double gaussBackwardCoeff(double t, int k) {
        double prod = 1.0;
        if (k % 2 == 1) {
            // odd: shifts from -(k-1)/2 to (k-1)/2
            int m = (k - 1) / 2;
            for (int s = -m; s <= m; s++) {
                prod *= (t + s);
            }
        } else {
            // even: shifts from -(k/2-1) to k/2
            int start = -(k / 2 - 1);
            int end = k / 2;
            for (int s = start; s <= end; s++) {
                prod *= (t + s);
            }
        }
        return prod / factorial(k);
    }
}
