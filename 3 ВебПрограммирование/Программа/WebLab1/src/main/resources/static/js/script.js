'use strict';

let x, r;
let rArray = [];

document.querySelectorAll("input[name=X]").forEach(btn => {
    btn.addEventListener("click", () => {
        x = btn.value;
        document.querySelectorAll("input[name=X]").forEach(b => b.classList.remove("selected"));
        btn.classList.add("selected");
        document.getElementById("errorX").textContent = "";
    });
});

window.onload = function() {
    loadResults();
};

document.getElementById("check-button").onclick = function () {
    if (checkFrom()) {
        let y = document.querySelector("input[name=Y]").value.replace(",", ".");
        sendPointRequest(x, y, rArray);
        reset();
    }
};

let reset =  document.getElementById("reset-button").onclick = function () {
    x = undefined;
    document.querySelectorAll("input[name=X]").forEach(btn => btn.classList.remove("selected"));

    document.querySelector("input[name=Y]").value = "";

    r = undefined;
    document.querySelectorAll("input[name=R]").forEach(cb => cb.checked = false);

    document.getElementById("errorX").textContent = "";
    document.getElementById("errorY").textContent = "";
    document.getElementById("errorR").textContent = "";
};

document.getElementById("clear-results-button").onclick = function() {
    clearResults();
};

// 线程锁
let isLock = false;
let lockList = [];
async function lock() {
    function unlock() {
        let waitFunc = lockList.shift();
        if (waitFunc) {
            waitFunc.resolve(unlock);
        } else {
            isLock = false;
        }
    }
    if (isLock) {
        return new Promise((resolve, reject) => {
            lockList.push({ resolve, reject });
        });
    } else {
        isLock = true;
        return unlock;
    }
}

async function sendPointRequest(x, y, rArray) {
    for (let i = 0; i < rArray.length; i++) {
        let unlock = await lock();
        const xhr = new XMLHttpRequest();

        const url = `http://localhost:24888/fcgi-bin/WebLab1.jar?x=${x}&y=${y}&r=${rArray[i]}`;

        xhr.open('GET', url, true);

        xhr.onload = function () {
            if (xhr.status === 200) {
                try {
                    const response = JSON.parse(xhr.responseText);
                    updateResultsTable(response.allResults);
                    console.log('Проверка прошла успешно');
                } catch (error) {
                    console.error('Ошибка при разборе ответа:', error);
                }
            } else {
                console.error(`Запрос не удался: ${xhr.status}`);
            }
        };

        xhr.onerror = function () {
            console.error('Сетевая ошибка, проверьте, работает ли сервер');
        };

        xhr.send();
        unlock();
    }
}

function loadResults() {
    const xhr = new XMLHttpRequest();
    const url = 'http://localhost:24888/fcgi-bin/WebLab1.jar';

    xhr.open('GET', url, true);

    xhr.onload = function() {
        if (xhr.status === 200) {
            try {
                const response = JSON.parse(xhr.responseText);
                updateResultsTable(response.allResults);
            } catch (error) {
                console.error('Ошибка при загрузке результатов:', error);
            }
        }
    };

    xhr.send();
}

function clearResults() {
    const xhr = new XMLHttpRequest();
    const url = 'http://localhost:24888/fcgi-bin/WebLab1.jar?clear=true';

    xhr.open('GET', url, true);

    xhr.onload = function() {
        if (xhr.status === 200) {
            try {
                const response = JSON.parse(xhr.responseText);
                updateResultsTable(response.allResults);
                console.log('Результаты очищены');
            } catch (error) {
                console.error('Ошибка при очистке результатов:', error);
            }
        } else {
            console.error(`Очистка не удалась: ${xhr.status}`);
        }
    };

    xhr.send();
}

async function updateResultsTable(results) {
    let unlock = await lock();
    const resultsBody = document.getElementById('result-body');
    resultsBody.innerHTML = '';

    if (results && results.length > 0) {
        results.reverse().forEach(result => {
            const row = document.createElement('tr');
            const hitText = result.isHit ? 'Попадание' : 'Промах';
            const hitClass = result.isHit ? 'hit' : 'miss';

            row.innerHTML = `
                <td>${result.x}</td>
                <td>${result.y}</td>
                <td>${result.r}</td>
                <td class="${hitClass}">${hitText}</td>
                <td>${result.currentTime}</td>
                <td>${result.executionTime}</td>
            `;

            resultsBody.appendChild(row);
        });
    } else {
        const emptyRow = document.createElement('tr');
        emptyRow.innerHTML = '<td colspan="6">Нет результатов, пожалуйста, введите координаты точки для проверки</td>';
        resultsBody.appendChild(emptyRow);
    }
    unlock();
}

