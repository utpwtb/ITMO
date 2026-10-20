'use strict';
// Russian interface text: substitute template values and render text safely.
const UiText = (() => {
    function format(key, values = {}) {
        return key.replace(/\{(\w+)\}/g, (_, name) => String(values[name] ?? `{${name}}`));
    }
    function render(node, key, values = {}) {
        node.textContent = typeof key === 'function' ? key() : format(key, values);
        return node;
    }
    const fields = {name:'Название', coordinates:'Координаты', oscarsCount:'Число «Оскаров»', budget:'Бюджет',
        totalBoxOffice:'Общие сборы', mpaaRating:'Рейтинг MPAA', director:'Режиссёр', screenwriter:'Сценарист', operator:'Оператор',
        length:'Продолжительность', goldenPalmCount:'Золотые пальмовые ветви', usaBoxOffice:'Сборы в США', tagline:'Слоган', genre:'Жанр',
        eyeColor:'Цвет глаз', hairColor:'Цвет волос', location:'Место', birthday:'Дата рождения с часовым поясом', height:'Рост', weight:'Вес',
        passportID:'Паспорт (уникальный)', creationDate:'Дата создания', version:'Версия', x:'X', y:'Y', id:'ID'};
    function field(key) { return fields[key] || key; }
    return {format, render, field};
})();
