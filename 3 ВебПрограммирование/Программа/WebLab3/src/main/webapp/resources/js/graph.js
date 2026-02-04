'use strict';

let svg = null;
let resultObserver = null;

function drawPoint(x, y, r, result) {
    if (!svg) svg = document.getElementById("graph-svg");
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

function getPrimaryRForDrawing() {
    const rList = bySuffix('rHiddenList');
    if (rList) {
        const values = splitCsvValues(rList.value);
        if (values.length) {
            const first = parseFloat(values[0]);
            if (!isNaN(first)) return first;
        }
    }
    const rInput = bySuffix('rHidden') || document.getElementById('pointForm:rHidden');
    if (!rInput || !rInput.value) return null;
    const currentR = parseFloat(normalizeNumberString(rInput.value));
    return isNaN(currentR) ? null : currentR;
}

function redrawAllPoints() {
    if (!svg) svg = document.getElementById('graph-svg');
    if (!svg) return;

    svg.querySelectorAll('circle').forEach(circle => {
        if (circle.getAttribute('r') === '5') circle.remove();
    });

    const currentR = getPrimaryRForDrawing();
    if (currentR === null) return;

    const table = document.querySelector('table[id$="result-table"]');
    if (!table) return;

    const rows = table.querySelectorAll('tbody tr');
    for (const row of rows) {
        const cells = row.querySelectorAll('td');
        if (cells.length < 4) continue;

        const x = parseFloat(cells[0].innerText.trim());
        const y = parseFloat(cells[1].innerText.trim());
        const r = parseFloat(cells[2].innerText.trim());

        if (isNaN(x) || isNaN(y) || isNaN(r)) continue;
        if (Math.abs(r - currentR) > 1e-6) continue;

        const resultText = cells[3].innerText.trim().toLowerCase();
        const result = resultText === "hit" || resultText === "попадание";
        drawPoint(x, y, r, result);
    }
}

function attachObserver() {
    if (resultObserver) {
        resultObserver.disconnect();
    }
    resultObserver = new MutationObserver(function() {
        redrawAllPoints();
    });
    const resultContainer = bySuffix('resultContainer');
    if (resultContainer && resultObserver) {
        resultObserver.observe(resultContainer, {
            childList: true,
            subtree: true
        });
    }
}
