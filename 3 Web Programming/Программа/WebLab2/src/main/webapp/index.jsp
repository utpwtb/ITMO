<%@ page contentType="text/html; charset=UTF-8" pageEncoding="UTF-8" %>
<%@page import="com.itmo.model.dao.PointDao" %>
<%@ page import="com.itmo.model.pojo.Point" %>
<%@ taglib prefix="c" uri="http://java.sun.com/jsp/jstl/core" %>

<!DOCTYPE html>
<html lang="ru-RU">
<head>
    <meta charset="UTF-8"/>
    <meta name="viewport" content="width=device-width, initial-scale=1.0"/>
    <title>Веб-программирование Лабораторная работа #2</title>

    <script src="js/script.js" defer></script>
    <link href="css/style.css" rel="stylesheet">
</head>
<body>
<div class="container">
    <header>
        <h1>Чень Хаолинь Р3216 Вариант:407960</h1>
    </header>

    <div class="graph-container">
        <svg
                width="100%"
                height="500"
                viewBox="0 0 600 600"
                preserveAspectRatio="xMidYMid meet"
                xmlns="http://www.w3.org/2000/svg"
        >
            <!-- Центр координат -->
            <defs>
                <marker
                        id="arrowhead"
                        markerWidth="10"
                        markerHeight="7"
                        refX="9"
                        refY="3.5"
                        orient="auto"
                >
                    <polygon points="0 0, 10 3.5, 0 7" fill="#000"/>
                </marker>
            </defs>

            <!-- Ось X -->
            <line
                    x1="50"
                    y1="300"
                    x2="550"
                    y2="300"
                    class="axis"
                    marker-end="url(#arrowhead)"
            />
            <text x="560" y="290" class="axis-label">X</text>
            <!-- насечки и метки оси X -->
            <line x1="100" y1="295" x2="100" y2="305" class="axis"/>
            <text x="95" y="325" class="label">-R</text>

            <line x1="200" y1="295" x2="200" y2="305" class="axis"/>
            <text x="195" y="325" class="label">-R/2</text>

            <line x1="400" y1="295" x2="400" y2="305" class="axis"/>
            <text x="395" y="325" class="label">R/2</text>

            <line x1="500" y1="295" x2="500" y2="305" class="axis"/>
            <text x="495" y="325" class="label">R</text>

            <!-- Ось Y -->
            <line
                    x1="300"
                    y1="550"
                    x2="300"
                    y2="50"
                    class="axis"
                    marker-end="url(#arrowhead)"
            />
            <text x="310" y="40" class="axis-label">Y</text>
            <!-- насечки и метки оси Y -->
            <line x1="295" y1="100" x2="305" y2="100" class="axis"/>
            <text x="315" y="105" class="label">R</text>

            <line x1="295" y1="200" x2="305" y2="200" class="axis"/>
            <text x="315" y="205" class="label">R/2</text>

            <line x1="295" y1="400" x2="305" y2="400" class="axis"/>
            <text x="315" y="405" class="label">-R/2</text>

            <line x1="295" y1="500" x2="305" y2="500" class="axis"/>
            <text x="315" y="505" class="label">-R</text>

            <!-- Прямоугольная часть -->
            <polygon points="300,300 500,300 500,100 300,100" class="shape"/>

            <!-- Треугольная часть -->
            <polygon points="300,300 100,300 300,100" class="shape"/>

            <!-- Четверть круга -->
            <path
                    d="M 400,300 A 100,100 0 0 1 300,400 L 300,300 Z"
                    class="shape"
            />
        </svg>
            <p id="error-graph" style="color: #f41c52"></p>
    </div>

    <div class="form-container">
        <form method="get" onsubmit="return false">
            <p id="errorX" style="color: #f41c52"></p>
            <!-- Значение X -->
            <div class="form-section select-X">
                <span class="section-title">Выберите значение X:</span>
                <label>
                    <select id="X">
                        <option disabled selected value=""></option>
                        <option value="-5">-5</option>
                        <option value="-4">-4</option>
                        <option value="-3">-3</option>
                        <option value="-2">-2</option>
                        <option value="-1">-1</option>
                        <option value="0">0</option>
                        <option value="1">1</option>
                        <option value="2">2</option>
                        <option value="3">3</option>
                    </select>
                </label>
            </div>

            <p id="errorY" style="color: #f41c52"></p>
            <!-- Значение Y -->
            <div class="form-section text-Y">
                <span class="section-title">Введите значение Y:</span>
                <label>
                    <input
                            type="text"
                            name="Y"
                            placeholder="Введите число от -3 до 5"
                    />
                </label>
            </div>

            <p id="errorR" style="color: #f41c52"></p>
            <!-- Значение R -->
            <div class="form-section text-R">
                <span class="section-title">Выберите значение R:</span>
                <label>
                    <input
                            type="text"
                            name="R"
                            placeholder="Введите число от 1 до 4"
                            value="<%= request.getAttribute("preserveR") != null ? request.getAttribute("preserveR") : "" %>"
                    />
                </label>
            </div>

            <div class="submit-btn">
                <input type="button" id="check-button" value="Отправить"/>
                <input type="button" id="reset-button" value="Отменить"/>
                <input
                        type="button"
                        id="clear-results-button"
                        value="Очистить результаты"
                />
            </div>
        </form>
    </div>
</div>

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

</body>

<script>

</script>
</html>
