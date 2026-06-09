'use strict';

function getSelectedXValues() {
    const xList = bySuffix('xHiddenList');
    let values = [];
    if (xList) {
        values = splitCsvValues(xList.value);
    }
    if (!values.length) {
        const xHidden = bySuffix('xHidden');
        const single = normalizeNumberString(xHidden ? xHidden.value : "");
        if (single !== "") values = [single];
    }
    return values;
}

function setSelectedXValues(values) {
    const normalized = (values || []).map(normalizeNumberString).filter(v => v !== "");
    const xList = bySuffix('xHiddenList');
    if (xList) xList.value = normalized.join(',');
    const xHidden = bySuffix('xHidden');
    if (xHidden) xHidden.value = normalized.length ? normalized[0] : "";
    highlightSelection('xButtons', normalized);
}

function syncXSelection() {
    const xList = bySuffix('xHiddenList');
    const values = xList ? splitCsvValues(xList.value) : [];
    const xHidden = bySuffix('xHidden');
    const primary = normalizeNumberString(xHidden ? xHidden.value : "");
    if (!values.length) {
        if (primary !== "") {
            setSelectedXValues([primary]);
        }
        return;
    }
    if (xHidden && primary !== values[0]) xHidden.value = values[0];
    highlightSelection('xButtons', values);
}

function getSelectedRValues() {
    const rList = bySuffix('rHiddenList');
    if (!rList) return [];
    return splitCsvValues(rList.value);
}

function setSelectedRValues(values) {
    const normalized = (values || []).map(normalizeNumberString).filter(v => v !== "");
    const rList = bySuffix('rHiddenList');
    if (rList) rList.value = normalized.join(',');
    const rHidden = bySuffix('rHidden');
    if (rHidden) rHidden.value = normalized.length ? normalized[0] : "";
    lastSelectedRValues = normalized.slice();
    highlightSelection('rLinks', normalized);
    redrawAllPoints();
}

function syncRSelection() {
    const values = getSelectedRValues();
    const rHidden = bySuffix('rHidden');
    const primary = normalizeNumberString(rHidden ? rHidden.value : "");
    if (!values.length) {
        if (lastSelectedRValues.length) {
            setSelectedRValues(lastSelectedRValues);
            return;
        }
        if (primary) {
            setSelectedRValues([primary]);
            return;
        }
    }
    if (values.length) {
        if (rHidden && primary !== values[0]) rHidden.value = values[0];
        highlightSelection('rLinks', values);
    }
}

function getPrimaryRValue() {
    const values = getSelectedRValues();
    if (values.length) return values[0];
    const rHidden = bySuffix('rHidden');
    return normalizeNumberString(rHidden ? rHidden.value : "");
}

function clearFormValues(options) {
    const opts = options || {};
    const preserveErrors = opts.preserveErrors === true;
    // 默认不保留 R，除非显式要求
    const preserveR = opts.preserveR === true;

    const xHidden = bySuffix('xHidden');
    const xList = bySuffix('xHiddenList');
    const yHidden = bySuffix('yHidden');
    const yInputText = document.getElementById('yInputText');

    if (xHidden) xHidden.value = '';
    if (xList) xList.value = '';
    if (yHidden) yHidden.value = '';
    if (yInputText) yInputText.value = '';

    if (!preserveR) {
        const rHidden = bySuffix('rHidden');
        const rList = bySuffix('rHiddenList');
        if (rHidden) rHidden.value = '';
        if (rList) rList.value = '';
        lastSelectedRValues = [];
        highlightSelection('rLinks', []);
    } else {
        const currentValues = getSelectedRValues();
        const valuesToKeep = currentValues.length ? currentValues : lastSelectedRValues;
        const rHidden = bySuffix('rHidden');
        const rList = bySuffix('rHiddenList');
        if (valuesToKeep.length) {
            if (rList) rList.value = valuesToKeep.join(',');
            if (rHidden) rHidden.value = valuesToKeep[0];
        }
        highlightSelection('rLinks', valuesToKeep);
    }

    highlightSelection('xButtons', []);

    if (!preserveErrors) {
        clearClientErrors();
        const errorElement = document.getElementById("error-graph");
        if (errorElement) errorElement.textContent = "";
    }

    redrawAllPoints();
}

let pendingSubmissions = [];
let isSubmitting = false;
let lastSubmissionSource = null;
let lastSelectedRValues = [];

function runAllValidation() {
    const okX = validateXInput();
    const okY = validateYInput();
    const okR = validateRInput();
    return okX && okY && okR;
}

function handleFormSubmit(evt) {
    const yInput = document.getElementById('yInputText');
    const yHidden = bySuffix('yHidden');

    if (!isSubmitting) {
        syncXSelection();
        syncRSelection();
        if (yInput && yHidden) yHidden.value = normalizeNumberString(yInput.value);
    }

    const valid = runAllValidation();
    if (!valid) {
        clearFormValues({ preserveErrors: true, preserveR: true });
        return false;
    }

    const xList = getSelectedXValues();
    const rList = getSelectedRValues();
    const yVal = yHidden ? yHidden.value : null;

    // 如果正在处理队列，放行本次提交（用于 processNextSubmission 触发的点击）
    if (isSubmitting) {
        return true;
    }

    // 只有一个 R/X 时，走默认提交；多个 R/X 时拦截并排队多次提交
    if (xList.length <= 1 && rList.length <= 1) {
        return true;
    }

    if (evt && typeof evt.preventDefault === 'function') {
        evt.preventDefault();
    }
    enqueueSubmissions(xList, yVal, rList, 'form');
    return false;
}

function handleFormAjaxEvent(data) {
    if (!data || data.status !== 'success') return;
    if (!isSubmitting) {
        // 单次表单提交（非队列）默认清空 X/Y/R
        lastSubmissionSource = 'form';
    }
    processNextSubmission();
}

function enqueueSubmissions(xValues, yValue, rValues, source) {
    const normalizedX = (Array.isArray(xValues) ? xValues : [xValues]).map(normalizeNumberString).filter(v => v !== "");
    const normalizedR = (Array.isArray(rValues) ? rValues : [rValues]).map(normalizeNumberString).filter(v => v !== "");
    const normalizedY = normalizeNumberString(yValue);
    if (!normalizedX.length || !normalizedR.length || normalizedY === "") return;
    normalizedX.forEach(xVal => {
        normalizedR.forEach(rVal => pendingSubmissions.push({ x: xVal, y: normalizedY, r: rVal, source }));
    });
    if (!isSubmitting) {
        processNextSubmission();
    }
}

function processNextSubmission() {
    if (pendingSubmissions.length === 0) {
        isSubmitting = false;
        const preserveR = lastSubmissionSource === 'svg';
        clearFormValues({ preserveErrors: false, preserveR });
        if (preserveR && lastSelectedRValues.length) {
            setSelectedRValues(lastSelectedRValues);
        }
        return;
    }
    isSubmitting = true;
    const next = pendingSubmissions.shift();
    lastSubmissionSource = next.source;

    const xHidden = bySuffix('xHidden');
    const yHidden = bySuffix('yHidden');
    const rHidden = bySuffix('rHidden');

    if (xHidden) xHidden.value = next.x;
    if (yHidden) yHidden.value = next.y;
    if (rHidden) rHidden.value = next.r;

    highlightSelection('xButtons', getSelectedXValues());
    highlightSelection('rLinks', getSelectedRValues());

    if (!runAllValidation()) {
        processNextSubmission();
        return;
    }

    const buttonToUse = next.source === 'svg' ? bySuffix('graph-submit-button') : bySuffix('check-button');
    const fallback = bySuffix('check-button');
    const btn = buttonToUse || fallback;
    if (btn) btn.click();
}

function sendCoordinatesToServer(x, y, r, options) {
    const opts = options || {};
    clearClientErrors();

    const selectedR = getSelectedRValues();
    const toSend = selectedR.length ? selectedR : (r ? [r] : []);

    if (opts.source === 'svg' && selectedR.length) {
        lastSelectedRValues = selectedR.slice();
    }
    enqueueSubmissions([x], y, toSend, opts.source);
}

function initializePage() {
    svg = document.getElementById("graph-svg");

    const rHidden = bySuffix('rHidden');
    if (rHidden) {
        rHidden.onchange = function () {
            redrawAllPoints();
        };
    }

    const yInput = document.getElementById('yInputText');
    if (yInput) {
        yInput.addEventListener('input', function() {
            setError('errorYClient', "");
        });
    }

    if (svg) {
        svg.removeEventListener("click", handleSvgClick);
        svg.addEventListener("click", handleSvgClick);
    }

    syncXSelection();
    syncRSelection();
    redrawAllPoints();
}

function handleSvgClick(event) {
    const rInput = getPrimaryRValue();
    const errorElement = document.getElementById("error-graph");

    if (!validateRValue(rInput)) {
        if (errorElement) errorElement.textContent = "R 扶快 志抑忌把忘扶抉";
        return;
    }

    if (errorElement) errorElement.textContent = "";

    if (!svg) svg = document.getElementById("graph-svg");
    if (!svg) return;

    const svgPoint = svg.createSVGPoint();
    svgPoint.x = event.clientX;
    svgPoint.y = event.clientY;

    const ctm = svg.getScreenCTM();
    if (!ctm) return;

    const pointInSvgCoords = svgPoint.matrixTransform(ctm.inverse());
    const planeCoords = transformSvgToPlane(pointInSvgCoords.x, pointInSvgCoords.y, parseFloat(rInput));

    sendCoordinatesToServer(planeCoords.x.toFixed(2), planeCoords.y.toFixed(2), rInput, { source: 'svg' });
}

function selectX(value) {
    const normalized = normalizeNumberString(value);
    const values = getSelectedXValues();
    const index = values.indexOf(normalized);
    if (index === -1) {
        values.push(normalized);
    } else {
        values.splice(index, 1);
    }
    setSelectedXValues(values);
    setError('errorXClient', "");
}

function selectR(value) {
    const normalized = normalizeNumberString(value);
    const values = getSelectedRValues();
    const index = values.indexOf(normalized);
    if (index === -1) {
        values.push(normalized);
    } else {
        values.splice(index, 1);
    }
    setSelectedRValues(values);
    setError('errorRClient', "");
}

function resetForm() {
    clearFormValues({ preserveErrors: false, preserveR: false });
}
