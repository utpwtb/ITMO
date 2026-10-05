package com.itmo.util;

import jakarta.servlet.http.HttpServletRequest;

public class RequestValidator {
    // 验证从SVG点击的点（X值只需要在范围内即可）
    public static boolean validatePoint(double x, double y, double r){
        boolean validX = x >= -5 && x <= 3;

        boolean validY = y >= -3 && y <= 5;

        boolean validR = r >= 1 && r <= 4;

        return validX && validY && validR;
    }

    public static boolean hasValidParameters(HttpServletRequest request) {
        String x = request.getParameter("x");
        String y = request.getParameter("y");
        String r = request.getParameter("r");

        return x != null && !x.isEmpty() &&
                y != null && !y.isEmpty() &&
                r != null && !r.isEmpty();
    }
}
