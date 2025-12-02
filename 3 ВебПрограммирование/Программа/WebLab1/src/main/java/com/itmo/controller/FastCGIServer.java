package com.itmo.controller;

import com.fastcgi.FCGIInterface;
import com.itmo.service.PointService;
import com.itmo.entity.PointResult;
import cn.hutool.json.JSONArray;
import cn.hutool.json.JSONObject;

import java.io.IOException;
import java.io.PrintWriter;
import java.time.format.DateTimeFormatter;
import java.util.List;

public class FastCGIServer {
    private static final PointService pointService = new PointService();
    private static final DateTimeFormatter formatter = DateTimeFormatter.ofPattern("yyyy-MM-dd HH:mm:ss");

    public static void main(String[] args) throws IOException {
        FCGIInterface fcgi = new FCGIInterface();

        while (fcgi.FCGIaccept() >= 0) {
            processRequest();
        }
    }

    private static void processRequest() throws IOException {
        String queryString = System.getProperty("QUERY_STRING", "");

        String[] params = queryString.split("&");
        double x = 0, y = 0, r = 0;
        boolean paramsValid = false;

        try {
            for (String param : params) {
                String[] keyValue = param.split("=");
                if (keyValue.length == 2) {
                    String key = keyValue[0];
                    String value = keyValue[1];

                    switch (key) {
                        case "x":
                            x = Double.parseDouble(value);
                            break;
                        case "y":
                            y = Double.parseDouble(value);
                            break;
                        case "r":
                            r = Double.parseDouble(value);
                            break;
                        case "clear":
                            if (value.equals("true")) {
                                pointService.clearAllResults();
                            }
                            break;
                    }
                }
            }
            paramsValid = true;
        } catch (NumberFormatException e) {
            paramsValid = false;
        }

        PointResult result = null;
        if (paramsValid && queryString.contains("x=") && queryString.contains("y=") && queryString.contains("r=") && pointService.validateParameters(x, y, r)) {
            result = pointService.processPoint(x, y, r);
        }

        List<PointResult> allResults = pointService.getAllResults();

        sendJsonResponse(result, allResults);
    }

    private static void sendJsonResponse(PointResult newResult, List<PointResult> allResults) {
        JSONObject response = new JSONObject();

        if (newResult != null) {
            JSONObject newResultJson = new JSONObject();
            newResultJson.put("x", newResult.getX());
            newResultJson.put("y", newResult.getY());
            newResultJson.put("r", newResult.getR());
            newResultJson.put("isHit", newResult.isHit());
            newResultJson.put("currentTime", newResult.getCurrentTime().format(formatter));
            newResultJson.put("executionTime", newResult.getExecutionTime());
            response.put("newResult", newResultJson);
        }

        JSONArray resultsJson = new JSONArray();
        for (PointResult result : allResults) {
            JSONObject resultJson = new JSONObject();
            resultJson.put("x", result.getX());
            resultJson.put("y", result.getY());
            resultJson.put("r", result.getR());
            resultJson.put("isHit", result.isHit());
            resultJson.put("currentTime", result.getCurrentTime().format(formatter));
            resultJson.put("executionTime", result.getExecutionTime());
            resultsJson.add(resultJson);
        }
        response.put("allResults", resultsJson);

        PrintWriter out = new PrintWriter(System.out);
        out.println("Content-Type: application/json; charset=UTF-8");
        out.println();
        out.println(response);
        out.flush();
    }
}