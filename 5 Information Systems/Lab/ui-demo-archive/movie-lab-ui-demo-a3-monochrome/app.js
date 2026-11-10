const navigation = {
    movies: ['Фильмы', 'film'], people: ['Люди', 'users'], coordinates: ['Координаты', 'grid'], locations: ['Места', 'map'],
    import: ['Импорт JSON', 'upload'], history: ['История импорта', 'history'], operations: ['Спецоперации', 'sliders'],
};
const state = {
    view: 'movies', role: 'student', query: '', genre: '', sort: 'recent', page: 1, selected: 108,
    movies: structuredClone(initialMovies), history: structuredClone(initialHistory), nextMovie: 109, nextImport: 105,
    draft: null, importResult: null,
};

const app = document.querySelector('#app');
const dialog = document.querySelector('#dialog');
const toast = document.querySelector('#toast');
const escapeHtml = value => String(value ?? '').replace(/[&<>"']/g, char => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' })[char]);
const icon = (name, size = 18) => `<svg width="${size}" height="${size}" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.65" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">${icons[name]}</svg>`;
const number = new Intl.NumberFormat('ru-RU', { maximumFractionDigits: 2 });
const ratingLabel = rating => rating?.replace('_', '-') || '—';
const genreLabel = key => genres[key] || 'Без жанра';
const movieCode = id => `#${String(id).padStart(3, '0')}`;
const options = (entries, selected) => entries.map(([value, label]) => `<option value="${escapeHtml(value)}" ${String(selected ?? '') === String(value) ? 'selected' : ''}>${escapeHtml(label)}</option>`).join('');
const genreOptions = Object.entries(genres);
const action = (label, command, glyph, css = 'secondary', id = '') => `<button type="button" class="button ${css}" data-action="${command}" data-id="${id}">${glyph ? icon(glyph) : ''}${label}</button>`;

function nav(items) {
    return items.map(key => `<button class="nav-item" type="button" data-action="navigate" data-id="${key}" ${state.view === key ? 'aria-current="page"' : ''}>${icon(navigation[key][1])}<span>${navigation[key][0]}</span></button>`).join('');
}

function brand() {
    return `<button class="brand" type="button" data-action="navigate" data-id="movies"><span class="brand-mark">${icon('film', 21)}</span><span><strong>Кинотека</strong><small>ИТМО · Лабораторная № 2</small></span></button>`;
}

function session() {
    return `<div class="session"><label class="account"><span>Роль в демо</span><select aria-label="Роль в демо" id="role">${options([['student', 'Пользователь'], ['admin', 'Администратор']], state.role)}</select></label></div>`;
}

function render() {
    const keys = Object.keys(navigation);
    const shell = `<aside class="sidebar">${brand()}<nav aria-label="Главное меню">
        <div class="nav-group" role="group" aria-labelledby="nav-catalogue"><p class="nav-label" id="nav-catalogue">Коллекция</p>${nav(keys.slice(0, 4))}</div>
        <div class="nav-group" role="group" aria-labelledby="nav-tools"><p class="nav-label" id="nav-tools">Инструменты</p>${nav(keys.slice(4))}</div>
        </nav><div class="sidebar-foot">Локальный прототип</div></aside>`;
    app.innerHTML = `${shell}<div class="workspace"><div class="topbar"><div class="crumb">Демо-данные</div>${session()}</div><main id="main-content" tabindex="-1">${view()}</main></div>`;
}

function view() {
    if (state.view === 'movies') return catalog();
    if (state.view === 'import') return importPage();
    if (state.view === 'history') return historyPage();
    if (state.view === 'operations') return operationsPage();
    return referencePage();
}

function pageTitle(title, description, actions = '') {
    return `<section class="refine-heading"><div><h1 id="page-title">${title}</h1>${description ? `<p class="lede">${description}</p>` : ''}</div>${actions ? `<div class="title-actions">${actions}</div>` : ''}</section>`;
}

function catalog() {
    const add = action('Добавить фильм', 'create', 'plus', 'primary');
    return `${pageTitle('Фильмы', '', add)}<section class="catalog-panel refine-catalog" aria-labelledby="page-title">
        <div class="filters"><label class="search">${icon('search')}<input type="search" id="query" value="${escapeHtml(state.query)}" placeholder="Найти фильм или режиссёра" aria-label="Поиск по фильму или режиссёру"></label>
        <label class="filter-select"><span>Жанр</span><select id="genre" aria-label="Жанр">${options([['', 'Все жанры'], ...genreOptions], state.genre)}</select></label>
        <label class="filter-select"><span>Сортировка</span><select id="sort" aria-label="Сортировка">${options([['recent', 'Новые сначала'], ['title', 'По названию'], ['oscars', 'По наградам']], state.sort)}</select></label></div>
        <p id="catalog-status" class="sr-only" role="status"></p><div id="catalog-results"></div></section>`;
}

function visibleMovies() {
    const query = state.query.trim().toLocaleLowerCase('ru');
    return state.movies.filter(movie => (!state.genre || state.genre === movie.genre) &&
        `${movie.name} ${movie.director?.name ?? ''}`.toLocaleLowerCase('ru').includes(query))
        .sort((a, b) => state.sort === 'title' ? a.name.localeCompare(b.name, 'ru') : state.sort === 'oscars' ? b.oscarsCount - a.oscarsCount || b.id - a.id : b.id - a.id);
}

function refreshCatalog() {
    const results = document.querySelector('#catalog-results');
    if (!results) return;
    const status = document.querySelector('#catalog-status');
    const movies = visibleMovies();
    if (!movies.length) {
        status.textContent = 'Фильмы не найдены';
        results.innerHTML = `<div class="empty"><h2>Фильмы не найдены</h2><p>Измените запрос или сбросьте фильтры.</p>${action('Сбросить фильтры', 'reset-filter')}</div>`;
        return;
    }
    const pageSize = 10;
    const pages = Math.ceil(movies.length / pageSize);
    state.page = Math.min(state.page, pages);
    const start = (state.page - 1) * pageSize;
    const slice = movies.slice(start, start + pageSize);
    const summary = `Показано ${start + 1}–${start + slice.length} из ${movies.length}`;
    status.textContent = summary;
    const pagination = `<div class="panel-foot"><span>${summary}</span><div class="pagination"><button type="button" data-action="prev-page" aria-label="Предыдущая страница" ${state.page === 1 ? 'disabled' : ''}>‹</button><span>${state.page} / ${pages}</span><button type="button" data-action="next-page" aria-label="Следующая страница" ${state.page === pages ? 'disabled' : ''}>›</button></div></div>`;
    results.innerHTML = deskCatalog(slice, pagination);
}

function genreText(genre) {
    return `<span class="genre-text">${genreLabel(genre)}</span>`;
}

function deskCatalog(movies, pagination) {
    const selected = movies.find(movie => movie.id === state.selected) || movies[0];
    state.selected = selected.id;
    return `<div class="desk-grid"><section class="desk-records" aria-labelledby="desk-list-title"><header class="desk-list-head"><h2 id="desk-list-title">Список фильмов</h2></header>
        <div class="table-scroll"><table class="desk-table"><thead><tr><th scope="col">Фильм</th><th scope="col">Жанр</th></tr></thead><tbody>${movies.map(movie => `
            <tr data-action="select-movie" data-id="${movie.id}">
                <td><button class="film-link" type="button" aria-pressed="${movie.id === selected.id}"><span><strong>${escapeHtml(movie.name)}</strong><small>${movieCode(movie.id)} · ${movie.length} мин</small></span></button></td>
                <td>${genreLabel(movie.genre)}</td>
            </tr>`).join('')}</tbody></table></div>${pagination}</section>
        <article class="desk-detail" aria-labelledby="inspect-title"><header class="desk-detail-head"><div><p class="refine-kicker">Запись ${movieCode(selected.id)}</p><h2 id="inspect-title">${escapeHtml(selected.name)}</h2></div>${genreText(selected.genre)}</header>${movieFacts(selected)}<div class="dialog-actions">${action('Редактировать', 'edit', 'edit', 'primary', selected.id)}${action('Удалить', 'delete', '', 'secondary', selected.id)}</div></article></div>`;
}

function movieFacts(movie) {
    const fields = [
        ['Режиссёр', movie.director?.name], ['Продолжительность', `${movie.length} мин`], ['Рейтинг MPAA', ratingLabel(movie.mpaaRating)],
        ['«Оскары»', movie.oscarsCount], ['Бюджет', number.format(BigInt(movie.budget))], ['Сборы в США', number.format(movie.usaBoxOffice)],
        ['Общие сборы', movie.totalBoxOffice == null ? null : number.format(movie.totalBoxOffice)], ['Золотые пальмовые ветви', movie.goldenPalmCount],
        ['Сценарист', movie.screenwriter?.name], ['Оператор', movie.operator?.name],
        ['Координаты', `${movie.coordinates.x}, ${movie.coordinates.y}`],
    ];
    return `<blockquote>${escapeHtml(movie.tagline)}</blockquote><dl class="facts">${fields.map(([label, value]) => `<div><dt>${label}</dt><dd>${escapeHtml(value ?? '—')}</dd></div>`).join('')}</dl>`;
}

function refresh() {
    render();
    refreshCatalog();
}

function navigate(view) {
    state.view = view;
    refresh();
    window.scrollTo(0, 0);
    app.querySelector('main').focus({ preventScroll: true });
}

function importPage() {
    const draft = state.draft;
    const result = state.importResult;
    return `${pageTitle('Импорт JSON', 'Добавьте несколько фильмов из одного файла.', action('История импорта', 'navigate', '', 'secondary', 'history'))}
        <div class="utility-layout"><section class="surface"><div class="surface-head"><h2>Файл с фильмами</h2></div>
        <div class="dropzone" id="dropzone"><span class="upload-mark">${icon('upload', 23)}</span><strong>${draft ? escapeHtml(draft.name) : 'Перетащите сюда JSON-файл'}</strong><p>${draft?.pending ? 'Читаем файл…' : draft ? 'Файл выбран. Запустите пробный импорт.' : 'Один файл в UTF-8, до 5 МиБ'}</p>${action(draft ? 'Заменить файл' : 'Выбрать файл', 'pick-file')}
        <input id="file-input" type="file" accept=".json,application/json" hidden></div>
        <div class="import-actions"><div class="example-actions">${action('Взять пример', 'sample', 'file', 'text-button')}${action('Пример с ошибкой', 'bad-sample', '', 'text-button')}</div><button type="button" class="button primary" data-action="commit-import" ${draft && !draft.pending ? '' : 'disabled'}>${icon('upload')}Импортировать</button></div>
        ${result ? `<div class="import-result ${result.ok ? 'success' : 'failure'}" role="status">${icon(result.ok ? 'check' : 'close')}<div><strong>${result.ok ? `Добавлено фильмов: ${result.count}` : 'Импорт отменён'}</strong><p>${result.ok ? `Операция ${movieCode(result.id)} записана в историю.` : `${escapeHtml(result.error)} В коллекции ничего не изменилось.`}</p></div></div>` : ''}
        </section><aside class="surface guide"><span class="guide-icon">${icon('shield', 22)}</span><h2>Как проходит импорт</h2><ol><li><strong>Выберите файл</strong><span>Формат версии 1, от 1 до 1000 фильмов.</span></li><li><strong>Проверьте результат</strong><span>Ошибка в одной записи отменяет весь пакет.</span></li><li><strong>Откройте историю</strong><span>Там сохраняются и успешные, и отклонённые операции.</span></li></ol>${action('Скачать пример JSON', 'download', 'download', 'text-button')}</aside></div>`;
}

function historyPage() {
    const entries = state.history.filter(item => state.role === 'admin' || item.user === 'student');
    return `${pageTitle('История импорта', state.role === 'admin' ? 'Операции всех пользователей.' : 'Только ваши операции.', action('Новый импорт', 'navigate', 'upload', 'primary', 'import'))}
    <section class="catalog-panel" aria-labelledby="page-title">
    <div class="table-scroll"><table class="history-table"><thead><tr>${['ID', 'Статус', 'Файл', 'Пользователь', 'Добавлено', 'Время', ''].map(label => `<th scope="col">${label || '<span class="sr-only">Карточка</span>'}</th>`).join('')}</tr></thead><tbody>${entries.map(item => `<tr><td class="mono">${movieCode(item.id)}</td><td><span class="badge ${item.ok ? 'success' : 'failure'}"><i></i>${item.ok ? 'Успешно' : 'Ошибка'}</span></td><td><strong>${escapeHtml(item.file)}</strong></td><td>${item.user}</td><td>${item.ok ? item.count : '—'}</td><td>${escapeHtml(item.date)}</td><td><button class="icon-button" type="button" data-action="history-detail" data-id="${item.id}" aria-label="Операция ${movieCode(item.id)}">${icon('chevron', 15)}</button></td></tr>`).join('')}</tbody></table></div></section>`;
}

function referencePage() {
    const records = {
        people: ['Создатели фильмов в демо-коллекции.', ['ID', 'Имя', 'Место', 'Паспорт'], people.map(item => [item.id, item.name, item.city, item.passportID])],
        coordinates: ['Координаты, доступные в карточках фильмов.', ['ID', 'X', 'Y'], coordinates.map(item => [item.id, item.x, item.y])],
        locations: ['Города, связанные с участниками коллекции.', ['ID', 'Название'], people.map(item => [item.id, item.city])],
    };
    const [description, columns, rows] = records[state.view];
    return `${pageTitle(navigation[state.view][0], description)}<section class="catalog-panel" aria-labelledby="page-title"><div class="table-scroll"><table><thead><tr>${columns.map(label => `<th scope="col">${label}</th>`).join('')}</tr></thead><tbody>${rows.map(row => `<tr>${row.map(value => `<td>${escapeHtml(value)}</td>`).join('')}</tr>`).join('')}</tbody></table></div></section>`;
}

const operationSpecs = [
    ['average', 'Средние сборы в США', 'Среднее по всем фильмам в коллекции.', 'Рассчитать'],
    ['prefix', 'Поиск по слогану', 'Найдите фильм по первым буквам его слогана.', 'Найти'],
    ['award', 'Дополнительные награды', 'Добавьте «Оскары» фильмам длиннее заданного порога.', 'Наградить'],
    ['redistribute', 'Перераспределение наград', 'Каждый фильм-источник сохраняет одну награду.', 'Перераспределить'],
    ['delete', 'Удаление по сборам в США', 'Удалите фильмы с указанной суммой сборов.', 'Найти совпадения'],
];

function operationsPage() {
    return `${pageTitle('Специальные операции', 'Запускайте выборки и пакетные действия на демо-данных.')}<div class="operations-grid">${operationSpecs.map(([key, title, description, label]) => `<section class="surface operation"><h2>${title}</h2><p>${description}</p>${action(label, 'operation', '', 'secondary', key)}</section>`).join('')}</div>`;
}

function dialogHeader(kicker, title) {
    return `<header class="dialog-head"><div><p class="eyebrow"><span></span>${kicker}</p><h2 id="dialog-title">${title}</h2></div><button type="button" class="icon-button" data-action="close" aria-label="Закрыть">${icon('close')}</button></header>`;
}

function openDialog(html) {
    dialog.innerHTML = html;
    if (!dialog.open) dialog.showModal();
    dialog.scrollTop = 0;
}

function flash(message) {
    toast.textContent = message;
    toast.classList.add('visible');
    clearTimeout(flash.timer);
    flash.timer = setTimeout(() => toast.classList.remove('visible'), 2600);
}

function showMovie(movie) {
    state.selected = movie.id;
    openDialog(`${dialogHeader(`Запись ${movieCode(movie.id)}`, escapeHtml(movie.name))}<div class="dialog-body">${genreText(movie.genre)}${movieFacts(movie)}</div><div class="dialog-actions">${action('Редактировать', 'edit', 'edit', 'primary', movie.id)}${action('Удалить', 'delete', '', 'secondary', movie.id)}</div>`);
}

function input(label, key, value = '', settings = '') {
    return `<label>${label}<input name="${key}" value="${escapeHtml(value)}" ${settings}></label>`;
}

function select(label, key, entries, value) {
    return `<label>${label}<select name="${key}">${options(entries, value)}</select></label>`;
}

function editMovie(movie = {}) {
    const personEntries = [['', 'Не указан'], ...people.map(person => [person.id, person.name])];
    const coordEntries = coordinates.map(coord => [coord.id, `${coord.x}, ${coord.y}`]);
    if (movie.coordinates && !movie.coordinates.id) coordEntries.push(['imported', `${movie.coordinates.x}, ${movie.coordinates.y}`]);
    openDialog(`${dialogHeader(movie.id ? `КАРТОЧКА ${movieCode(movie.id)}` : 'КОЛЛЕКЦИЯ', movie.id ? 'Редактирование фильма' : 'Новый фильм')}
    <form id="movie-form" data-id="${movie.id || ''}"><div class="dialog-body editor"><fieldset><legend>Основное</legend><div class="field-grid">
    ${input('Название', 'name', movie.name, 'required maxlength="200"')}${select('Жанр', 'genre', [['', 'Не указан'], ...genreOptions], movie.genre)}
    ${input('Слоган', 'tagline', movie.tagline, 'required maxlength="240"')}${input('Продолжительность, мин', 'length', movie.length, 'type="number" min="1" max="2147483647" required')}
    ${select('Рейтинг MPAA', 'mpaaRating', ratings.map(rating => [rating, ratingLabel(rating)]), movie.mpaaRating)}${select('Координаты', 'coordinates', coordEntries, movie.coordinates?.id ?? (movie.coordinates ? 'imported' : ''))}</div></fieldset>
    <fieldset><legend>Создатели</legend><div class="field-grid">${[['Режиссёр', 'director'], ['Сценарист', 'screenwriter'], ['Оператор', 'operator']].map(([label, key]) => select(label, key, movie[key]?.id === undefined && movie[key] ? [...personEntries, ['imported', movie[key].name]] : personEntries, movie[key]?.id ?? (movie[key] ? 'imported' : ''))).join('')}</div></fieldset>
    <fieldset><legend>Награды и сборы</legend><div class="field-grid">
    ${input('«Оскары»', 'oscarsCount', movie.oscarsCount ?? 1, 'type="number" min="1" max="2147483647" required')}${input('Золотые пальмовые ветви', 'goldenPalmCount', movie.goldenPalmCount, 'inputmode="numeric" pattern="[0-9]+"')}
    ${input('Бюджет', 'budget', movie.budget, 'inputmode="numeric" pattern="[0-9]+" required')}${input('Сборы в США', 'usaBoxOffice', movie.usaBoxOffice, 'type="number" min="1" max="2147483647" required')}
    ${input('Общие сборы', 'totalBoxOffice', movie.totalBoxOffice, 'type="number" min="0" step="any"')}</div></fieldset><p class="form-error" role="alert" hidden></p></div>
    <div class="dialog-actions"><button class="button primary" type="submit">${icon('check')}Сохранить фильм</button>${action('Отмена', 'close')}</div></form>`);
}

function positiveLong(value) {
    return (typeof value === 'string' || Number.isSafeInteger(value)) && /^\d+$/.test(value) && BigInt(value) > 0n && BigInt(value) <= 9223372036854775807n;
}

function positiveInt(value) {
    return Number.isInteger(value) && value > 0 && value <= 2147483647;
}

function validateMovie(movie, collection, id) {
    if (typeof movie.name !== 'string' || !movie.name.trim()) return 'Укажите название фильма.';
    if (typeof movie.tagline !== 'string' || !movie.tagline.trim()) return 'Укажите слоган.';
    if (!movie.coordinates || !Number.isInteger(movie.coordinates.x) || movie.coordinates.x > 826 || !Number.isInteger(movie.coordinates.y)) return 'Проверьте координаты (целые X ≤ 826 и Y).';
    if (!positiveInt(movie.length) || !positiveInt(movie.oscarsCount) || !positiveInt(movie.usaBoxOffice)) return 'Продолжительность, награды и сборы в США должны быть положительными целыми числами.';
    if (!positiveLong(movie.budget) || (movie.goldenPalmCount != null && !positiveLong(movie.goldenPalmCount))) return 'Бюджет и число пальмовых ветвей должны быть положительными целыми числами в диапазоне Long.';
    if (movie.totalBoxOffice != null && (!Number.isFinite(movie.totalBoxOffice) || movie.totalBoxOffice < movie.usaBoxOffice)) return 'Общие сборы должны быть не меньше сборов в США.';
    if (!ratings.includes(movie.mpaaRating) || (movie.genre != null && !Object.hasOwn(genres, movie.genre))) return 'Проверьте рейтинг MPAA и жанр.';
    for (const key of ['director', 'screenwriter', 'operator']) {
        const person = movie[key];
        if (person != null && (typeof person.name !== 'string' || !person.name.trim() || typeof person.passportID !== 'string' || !person.passportID.trim())) return 'Для создателя фильма укажите имя и номер паспорта.';
    }
    if (collection.some(item => item.id !== id && item.name === movie.name && item.director?.passportID === movie.director?.passportID)) return 'Фильм с таким названием и режиссёром уже существует.';
    return '';
}

function saveMovie(form) {
    const id = Number(form.dataset.id);
    const previous = state.movies.find(movie => movie.id === id);
    const fields = Object.fromEntries(new FormData(form));
    const movie = {
        id: id || state.nextMovie, name: fields.name.trim(), tagline: fields.tagline.trim(), genre: fields.genre || null,
        length: Number(fields.length), oscarsCount: Number(fields.oscarsCount), mpaaRating: fields.mpaaRating,
        coordinates: fields.coordinates === 'imported' ? previous.coordinates : coordinates.find(item => item.id === Number(fields.coordinates)),
        budget: fields.budget, goldenPalmCount: fields.goldenPalmCount || null, usaBoxOffice: Number(fields.usaBoxOffice),
        totalBoxOffice: fields.totalBoxOffice ? Number(fields.totalBoxOffice) : null,
    };
    for (const key of ['director', 'screenwriter', 'operator']) movie[key] = fields[key] === 'imported' ? previous[key] : people.find(person => person.id === Number(fields[key])) || null;
    const error = validateMovie(movie, state.movies, id);
    if (error) {
        const alert = form.querySelector('.form-error');
        alert.textContent = error;
        alert.hidden = false;
        alert.scrollIntoView({ block: 'nearest' });
        return;
    }
    if (id) state.movies = state.movies.map(item => item.id === id ? movie : item);
    else {
        state.movies.push(movie);
        state.nextMovie++;
        state.page = 1;
        state.query = '';
        state.genre = '';
        state.sort = 'recent';
    }
    state.selected = movie.id;
    dialog.close();
    refresh();
    flash(id ? 'Изменения сохранены' : 'Фильм добавлен');
}

async function stageFile(file) {
    if (!file) return;
    state.importResult = null;
    const draft = { name: file.name, text: '', pending: true };
    state.draft = draft;
    if (state.view === 'import') refresh();
    try {
        if (file.size > 5 * 1024 * 1024) throw new Error('Размер файла превышает 5 МиБ.');
        draft.text = new TextDecoder('utf-8', { fatal: true }).decode(await file.arrayBuffer());
    } catch (error) {
        draft.error = error instanceof TypeError ? 'Файл должен быть в кодировке UTF-8.' : error.message;
    }
    draft.pending = false;
    if (state.view === 'import' && state.draft === draft) refresh();
}

function stageExample(bad) {
    const data = structuredClone(exampleImport);
    if (bad) data.movies[1].name = '';
    state.draft = { name: bad ? 'example-error.json' : 'example.json', text: JSON.stringify(data, null, 2) };
    state.importResult = null;
    refresh();
}

function parseImport(draft) {
    if (draft.error) throw new Error(draft.error);
    let data;
    try { data = JSON.parse(draft.text); }
    catch { throw new Error('Не удалось прочитать JSON. Проверьте синтаксис файла.'); }
    if (data?.formatVersion !== 1 || !Array.isArray(data.movies) || !data.movies.length || data.movies.length > 1000) {
        throw new Error('Укажите formatVersion: 1 и массив movies из 1–1000 записей.');
    }
    const staged = [];
    for (const [index, raw] of data.movies.entries()) {
        const prefix = `Запись ${index + 1}: `;
        if (!raw || typeof raw !== 'object' || Array.isArray(raw)) throw new Error(`${prefix}ожидался объект фильма.`);
        const movie = {
            id: state.nextMovie + index, name: raw.name, tagline: raw.tagline, genre: raw.genre,
            length: raw.length, oscarsCount: raw.oscarsCount, mpaaRating: raw.mpaaRating, budget: raw.budget,
            usaBoxOffice: raw.usaBoxOffice, totalBoxOffice: raw.totalBoxOffice, goldenPalmCount: raw.goldenPalmCount,
            coordinates: { x: raw.coordinates?.x, y: raw.coordinates?.y },
        };
        for (const key of ['director', 'screenwriter', 'operator']) {
            const person = raw[key];
            movie[key] = person == null ? null : { name: person.name, passportID: person.passportID };
        }
        const error = validateMovie(movie, state.movies.concat(staged));
        if (error) throw new Error(prefix + error);
        staged.push(movie);
    }
    return staged;
}

function commitImport() {
    if (!state.draft || state.draft.pending) return;
    const entry = { id: state.nextImport++, user: state.role, file: state.draft.name, date: new Date().toLocaleString('ru-RU', { dateStyle: 'short', timeStyle: 'short' }) };
    try {
        const movies = parseImport(state.draft);
        state.movies.push(...movies);
        state.nextMovie += movies.length;
        entry.ok = true;
        entry.count = movies.length;
    } catch (error) {
        entry.ok = false;
        entry.error = error.message;
    }
    state.history.unshift(entry);
    state.importResult = entry;
    state.draft = null;
    refresh();
}

function downloadExample() {
    const link = document.createElement('a');
    link.href = URL.createObjectURL(new Blob([JSON.stringify(exampleImport, null, 2)], { type: 'application/json' }));
    link.download = 'example.json';
    link.click();
    setTimeout(() => URL.revokeObjectURL(link.href), 1000);
}

function showHistory(id) {
    const entry = state.history.find(item => item.id === id);
    if (!entry || (state.role !== 'admin' && entry.user !== 'student')) return;
    openDialog(`${dialogHeader('ЖУРНАЛ ИМПОРТА', `Операция ${movieCode(id)}`)}<div class="dialog-body"><span class="badge ${entry.ok ? 'success' : 'failure'}"><i></i>${entry.ok ? 'Успешно' : 'Ошибка'}</span><dl class="facts"><div><dt>Пользователь</dt><dd>${entry.user}</dd></div><div><dt>Файл</dt><dd>${escapeHtml(entry.file)}</dd></div><div><dt>Время</dt><dd>${escapeHtml(entry.date)}</dd></div>${entry.ok ? `<div><dt>Добавлено</dt><dd>${entry.count}</dd></div>` : ''}</dl>${entry.error ? `<p class="form-error">${escapeHtml(entry.error)}</p>` : ''}</div><div class="dialog-actions">${action('Закрыть', 'close')}</div>`);
}

function showOperation(key) {
    const [, title, description, label] = operationSpecs.find(item => item[0] === key);
    const fields = {
        average: '', prefix: input('Начало слогана', 'prefix'),
        award: input('Длиннее, мин', 'length', '100', 'type="number" min="0" max="2147483647" required') + input('Число наград', 'count', '1', 'type="number" min="1" max="2147483647" required'),
        redistribute: select('Из жанра', 'from', genreOptions, 'TRAGEDY') + select('В жанр', 'to', genreOptions, 'COMEDY'),
        delete: input('Сборы в США', 'value', '1700000', 'type="number" min="1" max="2147483647" required'),
    };
    openDialog(`${dialogHeader('СПЕЦОПЕРАЦИИ', title)}<form id="operation-form" data-id="${key}"><div class="dialog-body"><p class="lede">${description}</p>${fields[key] ? `<div class="field-grid">${fields[key]}</div>` : ''}<p class="operation-result" role="status" hidden></p></div><div class="dialog-actions"><button class="button primary" type="submit">${label}</button>${action('Закрыть', 'close')}</div></form>`);
}

function runOperation(form) {
    const key = form.dataset.id;
    const data = Object.fromEntries(new FormData(form));
    const movies = state.movies;
    const result = form.querySelector('.operation-result');
    if (key === 'average') {
        result.textContent = movies.length ? `Среднее: ${number.format(movies.reduce((sum, movie) => sum + movie.usaBoxOffice, 0) / movies.length)}` : 'В коллекции пока нет фильмов.';
    } else if (key === 'prefix') {
        const matches = movies.filter(movie => movie.tagline.startsWith(data.prefix)).map(movie => movie.name);
        result.textContent = matches.length ? `Найдено: ${matches.join(', ')}.` : 'Совпадений нет.';
    } else if (key === 'award') {
        const matches = movies.filter(movie => movie.length > Number(data.length));
        if (matches.some(movie => !positiveInt(movie.oscarsCount + Number(data.count)))) result.textContent = 'Число наград превышает допустимый предел.';
        else {
            matches.forEach(movie => { movie.oscarsCount += Number(data.count); });
            result.textContent = `Обновлено фильмов: ${matches.length}.`;
        }
    } else if (key === 'redistribute') {
        const source = movies.filter(movie => movie.genre === data.from);
        const target = movies.filter(movie => movie.genre === data.to).sort((a, b) => a.id - b.id);
        if (data.from === data.to || !source.length || !target.length) result.textContent = 'Выберите два разных жанра, в каждом из которых есть фильмы.';
        else {
            const pool = source.reduce((sum, movie) => sum + movie.oscarsCount - 1, 0);
            const totals = target.map((movie, index) => movie.oscarsCount + Math.floor(pool / target.length) + Number(index < pool % target.length));
            if (totals.some(total => !positiveInt(total))) result.textContent = 'Число наград превышает допустимый предел.';
            else {
                target.forEach((movie, index) => { movie.oscarsCount = totals[index]; });
                source.forEach(movie => { movie.oscarsCount = 1; });
                result.textContent = `Перенесено наград: ${pool}. Фильмов-получателей: ${target.length}.`;
            }
        }
    } else {
        const matches = movies.filter(movie => movie.usaBoxOffice === Number(data.value));
        if (matches.length) return confirmDelete(matches);
        result.textContent = 'Совпадений нет.';
    }
    result.hidden = false;
}

function confirmDelete(movies) {
    const ids = movies.map(movie => movie.id);
    openDialog(`${dialogHeader('КОЛЛЕКЦИЯ', movies.length === 1 ? 'Удалить фильм?' : 'Удалить фильмы?')}<div class="dialog-body"><p>Из демо-коллекции будут удалены: <strong>${movies.map(movie => escapeHtml(movie.name)).join(', ')}</strong>.</p></div><div class="dialog-actions">${action('Подтвердить удаление', 'confirm-delete', '', 'danger', ids.join(','))}${action('Отмена', 'close')}</div>`);
}

document.addEventListener('click', event => {
    const trigger = event.target.closest('[data-action]');
    if (!trigger) return;
    const { action: command, id } = trigger.dataset;
    const movie = state.movies.find(item => item.id === Number(id));
    switch (command) {
        case 'navigate': navigate(id); break;
        case 'prev-page': case 'next-page': {
            state.page += command === 'prev-page' ? -1 : 1;
            refreshCatalog();
            document.querySelector(`[data-action="${command}"]:enabled, .film-link`)?.focus({ preventScroll: true });
            break;
        }
        case 'reset-filter': state.query = ''; state.genre = ''; state.page = 1; refresh(); document.querySelector('#query').focus(); break;
        case 'select-movie':
            state.selected = movie.id;
            refreshCatalog();
            document.querySelector(`.desk-table [data-id="${id}"] .film-link`).focus({ preventScroll: true });
            if (matchMedia('(max-width: 900px)').matches) showMovie(movie);
            break;
        case 'create': editMovie(); break;
        case 'edit': editMovie(movie); break;
        case 'delete': confirmDelete([movie]); break;
        case 'confirm-delete': {
            const ids = id.split(',').map(Number);
            state.movies = state.movies.filter(item => !ids.includes(item.id));
            dialog.close(); refresh(); flash(`Удалено фильмов: ${ids.length}`); break;
        }
        case 'close': dialog.close(); break;
        case 'pick-file': document.querySelector('#file-input').click(); break;
        case 'sample': case 'bad-sample': stageExample(command === 'bad-sample'); break;
        case 'commit-import': commitImport(); break;
        case 'download': downloadExample(); break;
        case 'history-detail': showHistory(Number(id)); break;
        case 'operation': showOperation(id); break;
    }
});

document.addEventListener('input', event => {
    if (event.target.id !== 'query') return;
    state.query = event.target.value;
    state.page = 1;
    refreshCatalog();
});

document.addEventListener('change', event => {
    const { id, value } = event.target;
    if (id === 'role') {
        state.role = value;
        refresh();
        document.querySelector('#role').focus({ preventScroll: true });
    }
    if (id === 'sort' || id === 'genre') {
        state[id] = value;
        state.page = 1;
        refreshCatalog();
    }
    if (id === 'file-input') stageFile(event.target.files[0]);
});

document.addEventListener('submit', event => {
    event.preventDefault();
    if (event.target.id === 'movie-form') saveMovie(event.target);
    if (event.target.id === 'operation-form') runOperation(event.target);
});

for (const name of ['dragover', 'dragleave', 'drop']) {
    document.addEventListener(name, event => {
        const zone = event.target.closest('#dropzone');
        if (!zone) return;
        event.preventDefault();
        zone.classList.toggle('dragging', name === 'dragover');
        if (name === 'drop') stageFile(event.dataTransfer.files[0]);
    });
}

refresh();
