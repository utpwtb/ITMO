package com.itmo.controller;

import com.itmo.model.dao.PointDao;
import com.itmo.model.pojo.Point;
import com.itmo.model.service.AreaCheckService;
import com.itmo.util.RequestValidator;
import jakarta.servlet.ServletException;
import jakarta.servlet.annotation.WebServlet;
import jakarta.servlet.http.HttpServlet;
import jakarta.servlet.http.HttpServletRequest;
import jakarta.servlet.http.HttpServletResponse;
import jakarta.servlet.http.HttpSession;

import java.io.IOException;

@WebServlet("/checkArea")
public class AreaCheckServlet extends HttpServlet {
    private AreaCheckService areaCheckService;

    @Override
    public void init() {
        areaCheckService = new AreaCheckService();
    }

    @Override
    protected void doPost(HttpServletRequest req, HttpServletResponse resp) throws ServletException, IOException {
        resp.setContentType("text/html;charset=UTF-8");

        try {
            String xParam = req.getParameter("x");
            String yParam = req.getParameter("y");
            String rParam = req.getParameter("r");
            String fromSvg = req.getParameter("fromSvg");

            double x = Double.parseDouble(xParam);
            double y = Double.parseDouble(yParam);
            double r = Double.parseDouble(rParam);

            boolean isValid = RequestValidator.validatePoint(x, y, r);
            
            if (!isValid) {
                req.getRequestDispatcher("index.jsp").forward(req, resp);
                return;
            }

            Point point = areaCheckService.createAndCheckPoint(x, y, r);

            HttpSession session = req.getSession();
            PointDao results = (PointDao) session.getAttribute("results");
            if (results == null) {
                results = new PointDao();
                session.setAttribute("results", results);
            }

            results.addPoint(point);

            // 设置请求属性，用于结果页面显示
            req.setAttribute("point", point);
            req.setAttribute("results", results);

            if ("true".equals(fromSvg)) {
                // 从SVG点击，保留R值以便在页面中恢复
                req.setAttribute("preserveR", rParam);
                req.getRequestDispatcher("index.jsp").forward(req, resp);
            } else {
                req.getRequestDispatcher("result.jsp").forward(req, resp);
            }
        } catch (Exception e) {
            req.getRequestDispatcher("index.jsp").forward(req, resp);
        }
    }
}
