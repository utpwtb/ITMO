<%@ page import="com.itmo.model.dao.PointDao" %>
<%@ page import="com.itmo.model.pojo.Point" %>
<%@ page contentType="text/html;charset=UTF-8" language="java" %>
<%@ taglib prefix="c" uri="http://java.sun.com/jsp/jstl/core" %>
<html>
<head>
    <title>Результат</title>
    <link rel="stylesheet" href="css/styleResult.css">
</head>
<body>
<div class="result-container">
    <h2>Результаты</h2>
    <table class="result-table">
        <thead>
        <tr>
            <th>X</th>
            <th>Y</th>
            <th>R</th>
            <th>Результат</th>
            <th>Текущее время</th>
            <th>Время выполнения (мс)</th>
        </tr>
        </thead>
        <tbody id="result-body">
        <%
            String clear = request.getParameter("clear");
            if ("1".equals(clear)) {
                session.removeAttribute("results");
            }

            PointDao dao = (PointDao) session.getAttribute("results");

            if (dao == null || dao.getPoints().isEmpty()) {
        %>
        <tr>
            <td colspan="6">
                Нет результатов, пожалуйста, введите координаты точки для проверки
            </td>
        </tr>
        <%
        } else {
            for (Point point : dao.getPoints()) {
        %>
        <tr>
            <td><%= point.getX() %></td>
            <td><%= point.getY() %></td>
            <td><%= point.getR() %></td>
            <td><%= point.isHit() ? "Попадание" : "Промах" %></td>
            <td><%= point.getCurrentTime() %></td>
            <td><%= point.getExecutionTime() %></td>
        </tr>
        <%
                }
            }
        %>
        </tbody>
    </table>
</div>

<div class="back-link">
    <input type="button" onclick="window.location.href='index.jsp'" value="Вернуться к форме" />
</div>

</body>
</html>
