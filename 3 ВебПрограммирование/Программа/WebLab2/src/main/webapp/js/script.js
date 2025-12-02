'use strict'

let x, y, r
let svg = null;

function drawPoint(x, y, r, result) {
    if (!svg) svg = document.querySelector("svg");
    if (!svg) return;

    const cx = x * 200 / r + 300;
    const cy = -y * 200 / r + 300;
    const circle = document.createElementNS("http://www.w3.org/2000/svg", "circle");
    circle.setAttribute("cx", cx);
    circle.setAttribute("cy", cy);
    circle.setAttribute("r", 5);
    circle.style.fill = result ? "#09a53d" : "#a50909";
    circle.style.stroke = "#000";
    circle.style.strokeWidth = "1";
    svg.appendChild(circle);
}

function transformSvgToPlane(svgX, svgY, r) {
    return {
        x: (svgX - 300) * r / 200,
        y: (300 - svgY) * r / 200
    };
}

function sendCoordinatesToServer(x, y, r, fromSvg = false) {
    sendPointRequest(x, y, r, fromSvg);
}

function initializePage() {
    svg = document.querySelector("svg");

    redrawAllPoints();

    document.querySelector("input[name=R]").onchange = function () {
        redrawAllPoints();
    }

    if (svg) {
        svg.removeEventListener("click", handleSvgClick);
        svg.addEventListener("click", handleSvgClick);
    }

    bindButtonEvents();
}

function handleSvgClick(event) {
    const rInputElement = document.querySelector("input[name=R]");
    if (!rInputElement) return;

    const rInput = rInputElement.value.replace(",", ".");
    const errorElement = document.getElementById("error-graph");

    if (!validateRValue(rInput)) {
        if (errorElement) errorElement.textContent = "R не введено";
        return;
    }

    if (errorElement) errorElement.textContent = "";

    if (!svg) svg = document.querySelector("svg");
    if (!svg) return;

    const svgPoint = svg.createSVGPoint();
    svgPoint.x = event.clientX;
    svgPoint.y = event.clientY;

    const ctm = svg.getScreenCTM();
    if (!ctm) return;

    const pointInSvgCoords = svgPoint.matrixTransform(ctm.inverse());
    const planeCoords = transformSvgToPlane(pointInSvgCoords.x, pointInSvgCoords.y, parseFloat(rInput));

    sendCoordinatesToServer(planeCoords.x.toFixed(2), planeCoords.y.toFixed(2), rInput, true);
}

document.addEventListener("DOMContentLoaded", initializePage);
if (document.readyState !== 'loading') initializePage();

function reset() {
    document.getElementById("X").selectedIndex = -1;
    document.querySelector("input[name=Y]").value = "";
    document.querySelector("input[name=R]").value = "";
    document.getElementById("errorX").textContent = "";
    document.getElementById("errorY").textContent = "";
    document.getElementById("errorR").textContent = "";
    const errorGraph = document.getElementById("error-graph");
    if (errorGraph) errorGraph.textContent = "";
}

function bindButtonEvents() {
    document.getElementById("reset-button").onclick = reset;
    document.getElementById("clear-results-button").onclick = () => window.location.href = "index.jsp?clear=1";
    document.getElementById("check-button").onclick = function () {
        if (checkFrom()) {
            x = document.getElementById("X").value;
            y = document.querySelector("input[name=Y]").value.replace(",", ".");
            r = document.querySelector("input[name=R]").value.replace(",", ".");
            sendPointRequest(x, y, r, false);
            reset();
        }
    };
}

function sendPointRequest(x, y, r, fromSvg = false) {
    const form = document.createElement('form');
    form.method = 'POST';
    form.action = '/WebLab2/controller';

    const addInput = (name, value) => {
        const input = document.createElement('input');
        input.type = 'hidden';
        input.name = name;
        input.value = value;
        form.appendChild(input);
    };

    addInput('x', x);
    addInput('y', y);
    addInput('r', r);
    if (fromSvg) addInput('fromSvg', 'true');

    document.body.appendChild(form);
    form.submit();
}

function checkFrom() {
    document.getElementById("errorX").textContent = "";
    document.getElementById("errorY").textContent = "";
    document.getElementById("errorR").textContent = "";
    return validateX() && validateY() && validateR();
}

function isNumeric(n) {
    return !isNaN(parseFloat(n)) && isFinite(n);
}

function validateX() {
    x = document.getElementById("X").value;
    if (x === "") {
        document.getElementById("errorX").textContent = "X не выбрано";
        return false;
    }
    if (!isNumeric(x)) {
        document.getElementById("errorX").textContent = "X не число";
        return false;
    }
    const xNum = parseFloat(x);
    if (![-5, -4, -3, -2, -1, 0, 1, 2, 3].includes(xNum)) {
        document.getElementById("errorX").textContent = "Неверное значение";
        return false;
    }
    return true;
}

function validateY() {
    y = document.querySelector("input[name=Y]").value.replace(",", ".");
    if (y.trim() === "") {
        document.getElementById("errorY").textContent = "Y не введено";
        return false;
    }
    if (!isNumeric(y)) {
        document.getElementById("errorY").textContent = "Y не число";
        return false;
    }
    const yNum = parseFloat(y);
    if (yNum < -3 || yNum > 5) {
        document.getElementById("errorY").textContent = "Y не входит в область допустимых значений (-3, 5)";
        return false;
    }
    return true;
}

function validateR() {
    r = document.querySelector("input[name=R]").value.replace(",", ".");
    if (r.trim() === "") {
        document.getElementById("errorR").textContent = "R не введено";
        return false;
    }
    if (!isNumeric(r)) {
        document.getElementById("errorR").textContent = "R не число";
        return false;
    }
    const rNum = parseFloat(r);
    if (rNum < 1 || rNum > 4) {
        document.getElementById("errorR").textContent = "R не входит в область допустимых значений (1, 4)";
        return false;
    }
    return true;
}

function validateRValue(rValue) {
    if (rValue.trim() === "") return false;
    if (!isNumeric(rValue)) return false;
    const rNum = parseFloat(rValue);
    return rNum >= 1 && rNum <= 4;
}

function redrawAllPoints() {
    if (!svg) svg = document.querySelector('svg');
    if (!svg) return;

    svg.querySelectorAll('circle').forEach(circle => {
        if (circle.getAttribute('r') === '5') circle.remove();
    });

    const currentR = parseFloat(document.querySelector("input[name=R]").value.replace(",", "."));

    const table = document.getElementById('result-body');
    if (!table) return;

    for (const row of table.rows) {
        if (row.cells.length !== 6 || row.cells[0].colSpan > 1) continue;

        const x = parseFloat(row.cells[0].innerText.trim());
        const y = parseFloat(row.cells[1].innerText.trim());
        const r = parseFloat(row.cells[2].innerText.trim());

        if (isNaN(x) || isNaN(y) || isNaN(r)) continue;
        if (!isNaN(currentR) && r !== currentR) continue;

        drawPoint(x, y, r, row.cells[3].innerText.trim() === "Попадание");

    }
}


