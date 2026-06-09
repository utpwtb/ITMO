'use strict';

function getSelectedXValuesForValidation() {
    const xListElement = bySuffix('xHiddenList');
    let values = [];
    if (xListElement) {
        values = splitCsvValues(xListElement.value);
    }
    if (!values.length) {
        const xHidden = bySuffix('xHidden');
        const single = normalizeNumberString(xHidden ? xHidden.value : "");
        if (single !== "") values = [single];
    }
    return values;
}

function validateXInput() {
    const xValues = getSelectedXValuesForValidation();
    if (!xValues.length) {
        setError('errorXClient', "X не выбрано");
        return false;
    }
    for (const xValRaw of xValues) {
        const xVal = normalizeNumberString(xValRaw);
        if (!isNumeric(xVal)) {
            setError('errorXClient', "X не число");
            return false;
        }
        const xNum = parseFloat(xVal);
        if (xNum < -4 || xNum > 4) {
            setError('errorXClient', "X не входит в область допустимых значений (-4, 4)");
            return false;
        }
    }
    setError('errorXClient', "");
    return true;
}
function validateYInput() {
    const yHidden = bySuffix('yHidden');
    const yVal = yHidden ? normalizeNumberString(yHidden.value) : "";
    if (yVal.trim() === "") {
        setError('errorYClient', "Y не введено");
        return false;
    }
    if (!isNumeric(yVal)) {
        setError('errorYClient', "Y не число");
        return false;
    }
    const yNum = parseFloat(yVal);
    if (yNum < -3 || yNum > 5) {
        setError('errorYClient', "Y не входит в область допустимых значений (-5, 5)");
        return false;
    }
    setError('errorYClient', "");
    return true;
}

function getSelectedRValuesForValidation() {
    const rListElement = bySuffix('rHiddenList');
    let values = [];
    if (rListElement) {
        values = splitCsvValues(rListElement.value);
    }
    if (!values.length) {
        const rHidden = bySuffix('rHidden');
        const single = normalizeNumberString(rHidden ? rHidden.value : "");
        if (single !== "") values = [single];
    }
    return values;
}

function validateRInput() {
    const rValues = getSelectedRValuesForValidation();
    if (!rValues.length) {
        setError('errorRClient', "R не выбрано");
        return false;
    }
    for (const rValRaw of rValues) {
        const rVal = normalizeNumberString(rValRaw);
        if (!isNumeric(rVal)) {
            setError('errorRClient', "R не число");
            return false;
        }
        const rNum = parseFloat(rVal);
        if (rNum < 1 || rNum > 4) {
            setError('errorRClient', "R не входит в область допустимых значений (1, 4)");
            return false;
        }
    }
    setError('errorRClient', "");
    return true;
}

function validateRValue(value) {
    const rVal = normalizeNumberString(value);
    if (rVal === "") return false;
    if (!isNumeric(rVal)) return false;
    const rNum = parseFloat(rVal);
    return !(rNum < 1 || rNum > 4);
}

function clearClientErrors() {
    setError('errorXClient', "");
    setError('errorYClient', "");
    setError('errorRClient', "");
}

