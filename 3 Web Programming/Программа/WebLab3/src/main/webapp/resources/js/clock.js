'use strict';

function updateClock() {
    const now = new Date();
    const dateStr = now.toLocaleDateString('ru-RU', {
        year: 'numeric',
        month: '2-digit',
        day: '2-digit'
    });
    const timeStr = now.toLocaleTimeString('ru-RU', {
        hour: '2-digit',
        minute: '2-digit',
        second: '2-digit'
    });
    const clockElement = document.getElementById('clock');
    if (clockElement) {
        clockElement.textContent = dateStr + ' ' + timeStr;
    }
}

function startClock() {
    updateClock();
    setInterval(updateClock, 8000);
}

if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', startClock);
} else {
    startClock();
}
