'use strict';

function bySuffix(suffix) {
    return document.querySelector('[id$="' + suffix + '"]');
}

function setError(elementId, message) {
    const target = document.getElementById(elementId) || bySuffix(elementId);
    if (target) target.textContent = message || "";
}

function isNumeric(value) {
    return !isNaN(parseFloat(value)) && isFinite(value);
}

function normalizeNumberString(value) {
    if (value === null || value === undefined) return "";
    return value.toString().replace(",", ".").trim();
}

function splitCsvValues(value) {
    if (!value) return [];
    return value.split(',').map(item => normalizeNumberString(item)).filter(item => item !== "");
}

function highlightSelection(containerId, value) {
    const container = document.getElementById(containerId);
    if (!container) return;
    const buttons = container.querySelectorAll('[data-value]');
    const values = Array.isArray(value) ? value.map(String) : (value === null || value === undefined ? [] : [String(value)]);
    const valueSet = new Set(values);
    buttons.forEach(btn => {
        if (valueSet.has(btn.dataset.value)) {
            btn.classList.add('active');
            btn.setAttribute('aria-pressed', 'true');
        } else {
            btn.classList.remove('active');
            btn.setAttribute('aria-pressed', 'false');
        }
    });
}
