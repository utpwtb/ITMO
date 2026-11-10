'use strict';
const $ = id => document.getElementById(id);
const {format: t, render: bind} = UiText;
document.querySelectorAll('[data-icon]').forEach(control => addIcon(control, control.dataset.icon));
document.querySelectorAll('form').forEach(Validation.attach);
function showError(element, error) {
    const raw = error.raw || error.message || String(error);
    bind(element, () => raw);
}
const enums = {
    genres: ['WESTERN', 'COMEDY', 'TRAGEDY', 'HORROR'],
    rating: ['G', 'PG', 'PG_13', 'R', 'NC_17'],
    color: ['GREEN', 'BLACK', 'ORANGE', 'WHITE', 'BROWN']
};
// [field, label, type, required, reference/enum, min, max]
const schemas = {
    movies: [['name', 'Название', 'text', true], ['coordinates', 'Координаты', 'ref', true, 'coordinates'], ['oscarsCount', 'Число «Оскаров»', 'integer', true, null, 1, 2147483647], ['budget', 'Бюджет', 'long', true, null, 1], ['totalBoxOffice', 'Общие сборы', 'number', false, null, 0], ['mpaaRating', 'Рейтинг MPAA', 'enum', true, 'rating'], ['director', 'Режиссёр', 'ref', false, 'people'], ['screenwriter', 'Сценарист', 'ref', false, 'people'], ['operator', 'Оператор', 'ref', false, 'people'], ['length', 'Продолжительность', 'integer', true, null, 1, 2147483647], ['goldenPalmCount', 'Золотые пальмовые ветви', 'long', false, null, 1], ['usaBoxOffice', 'Сборы в США', 'integer', true, null, 1, 2147483647], ['tagline', 'Слоган', 'text', true], ['genre', 'Жанр', 'enum', false, 'genres']],
    people: [['name', 'Имя', 'text', true], ['eyeColor', 'Цвет глаз', 'enum', false, 'color'], ['hairColor', 'Цвет волос', 'enum', false, 'color'], ['location', 'Место', 'ref', false, 'locations'], ['birthday', 'Дата рождения с часовым поясом', 'text', true], ['height', 'Рост', 'number', false, null, 0], ['weight', 'Вес', 'number', false, null, 0], ['passportID', 'Паспорт (уникальный)', 'text', true]],
    coordinates: [['x', 'X (≤ 826)', 'integer', true, null, -2147483648, 826], ['y', 'Y', 'integer', true, null, -2147483648, 2147483647]],
    locations: [['x', 'X', 'long', true], ['y', 'Y', 'number', true], ['name', 'Название', 'text', true]]
};
const titles = {movies: 'Фильмы', people: 'Люди', coordinates: 'Координаты', locations: 'Места'};
const createLabels = {movies: 'Добавить фильм', people: 'Добавить человека', coordinates: 'Добавить координаты', locations: 'Добавить место'};
const genreLabels = {WESTERN: 'Вестерн', COMEDY: 'Комедия', TRAGEDY: 'Трагедия', HORROR: 'Ужасы'};
const movieFields = [['actions', 'Действия'], ['name', 'Фильм'], ['genre', 'Жанр'], ['id', 'ID'], ['creationDate', 'Дата создания'],
    ...schemas.movies.filter(([key]) => key !== 'name' && key !== 'genre')];
const compactScreen = matchMedia('(max-width: 900px)');
let state = {
    kind: 'movies',
    page: 0,
    size: 10,
    total: 0,
    revision: null,
    csrf: '',
    busy: false,
    selectedMovie: null,
    editing: null,
    detail: null,
    deleting: null
};
let collectionRequest = 0;
let historyPage = 0;
let historyRequest = 0;

function option(select, value, label) {
    const e = document.createElement('option');
    e.value = value;
    bind(e, label);
    select.append(e);
}

for (const [v, l] of [['name', 'Название'], ['tagline', 'Слоган'], ['genre', 'Жанр'], ['mpaaRating', 'MPAA'], ['director', 'Режиссёр'], ['screenwriter', 'Сценарист'], ['operator', 'Оператор']]) {
    option($('filter-column'), v, l);
    option($('sort-column'), v, l);
}
option($('sort-column'), 'id', 'ID');
$('sort-column').value = 'id';
document.querySelectorAll('.genres').forEach(s => enums.genres.forEach(v => option(s, v, v)));

function updateFilterChoices() {
    const field = $('filter-column').value;
    const values = field === 'genre' ? enums.genres : field === 'mpaaRating' ? enums.rating : [];
    const choices = $('filter-choices');
    choices.replaceChildren();
    for (const value of values) option(choices, value, () => format(value, field));
    $('filter-value').placeholder = values.length ? values.join(', ') : 'Полное совпадение';
}
$('filter-column').onchange = updateFilterChoices;

async function api(path, method = 'GET', body) {
    const r = await fetch('api/' + path, {
        method,
        headers: body instanceof FormData ? {'X-CSRF-Token': state.csrf} : {'Content-Type': 'application/json', 'X-CSRF-Token': state.csrf},
        body: body instanceof FormData ? body : body === undefined ? undefined : JSON.stringify(body)
    });
    const text = await r.text();
    let data;
    try {
        data = JSON.parse(text);
    } catch {
        throw new Error('Сервер вернул некорректный ответ');
    }
    if (!r.ok) {
        if (r.status === 401 && !$('workspace').hidden) showSession({authenticated: false});
        const error = new Error(data.error || t('Ошибка {status}', {status: r.status}));
        error.raw = data.error || error.message;
        error.status = r.status;
        error.data = data;
        throw error;
    }
    return data;
}

function notice(message, error = false) {
    bind($('notice'), typeof message === 'function' ? message : () => error ? message : t(message));
    $('notice').className = error ? 'error' : '';
}

function showSession(data) {
    state.csrf = data.csrf || '';
    $('auth-shell').hidden = !!data.authenticated;
    $('workspace').hidden = !data.authenticated;
    $('session').replaceChildren();
    if (data.authenticated) {
        const user = document.createElement('div');
        user.className = 'session-user';
        user.append(node('strong', data.user), node('small', data.role === 'ADMIN' ? 'Администратор' : 'Пользователь'));
        const logout = button('Выйти', async () => {
            try {
                await api('auth', 'DELETE');
                showSession({authenticated: false});
            } catch (e) {
                notice(e.message, true);
            }
        }, 'secondary');
        $('session').append(user, logout);
    } else {
        collectionRequest++;
        historyRequest++;
        state.selectedMovie = null;
        historyPage = 0;
        $('rows').replaceChildren();
        $('history-rows').replaceChildren();
        $('movie-inspector').replaceChildren();
        $('movie-inspector').hidden = true;
        document.querySelectorAll('dialog[open]').forEach(dialog => dialog.close());
        $('filter-form').reset();
        $('sort-column').value = 'id';
        updateFilterChoices();
        $('import-form').reset();
        $('import-filename').textContent = 'Файл не выбран';
        $('import-result').replaceChildren();
        $('import-result').className = '';
        setFullColumns(false);
        notice('');
        authView(false);
    }
}

function authView(register) {
    $('login-form').hidden = register;
    $('register-form').hidden = !register;
    bind($('auth-heading'), register ? 'Регистрация' : 'Вход в систему');
    bind($('login-error'), '');
    bind($('register-error'), '');
    for (const form of [$('login-form'), $('register-form')]) {
        Validation.clear(form);
        form.querySelectorAll('input[type=password]').forEach(input => input.value = '');
    }
}

$('show-register').onclick = () => {
    authView(true);
    $('register-form').elements.username.focus();
};
$('show-login').onclick = () => {
    authView(false);
    $('login-form').elements.username.focus();
};

$('register-form').onsubmit = async e => {
    e.preventDefault();
    const form = e.target;
    if (!Validation.form(form)) return;
    const data = Object.fromEntries(new FormData(form));
    if (data.password !== data.confirmation) {
        bind($('register-error'), 'Пароли не совпадают');
        return;
    }
    const buttons = [...form.querySelectorAll('button')];
    buttons.forEach(button => button.disabled = true);
    try {
        showSession(await api('auth/register', 'POST', {username: data.username, password: data.password}));
        bind($('register-error'), '');
        form.reset();
        $('login-form').reset();
        state.revision = null;
        await navigate('movies');
    } catch (error) {
        Validation.server(form, error.raw || error.message);
        showError($('register-error'), error);
    } finally {
        buttons.forEach(button => button.disabled = false);
    }
};

$('login-form').onsubmit = async e => {
    e.preventDefault();
    if (!Validation.form(e.target)) return;
    try {
        showSession(await api('auth', 'POST', Object.fromEntries(new FormData(e.target))));
        bind($('login-error'), '');
        e.target.reset();
        state.revision = null;
        await navigate('movies');
    } catch (error) {
        showError($('login-error'), error);
    }
};

function format(value, key) {
    if (value === null || value === undefined) return '—';
    if (typeof value === 'object') return '#' + value.id + ' · ' + (value.name ?? `(${value.x}; ${value.y})`);
    if (key === 'genre') return genreLabels[value] || String(value);
    if (key === 'mpaaRating') return String(value).replace('_', '-');
    return String(value);
}

function node(tag, text, className) {
    const element = document.createElement(tag);
    if (text !== undefined) element.textContent = text;
    if (className) element.className = className;
    return element;
}

function button(text, handler, className) {
    const b = node('button', text, className);
    b.type = 'button';
    b.onclick = handler;
    return b;
}

function addIcon(control, icon) {
    control.prepend($(`${icon}-icon`).content.cloneNode(true));
}

function iconButton(icon, label, handler, className = '') {
    const control = button(undefined, handler, 'icon-button');
    if (className) control.classList.add(className);
    control.setAttribute('aria-label', label);
    control.title = label;
    addIcon(control, icon);
    return control;
}

async function refresh() {
    const request = ++collectionRequest;
    const {kind, page, size} = state;
    if (kind === 'history') return refreshHistory();
    if (!schemas[kind]) return;
    let data;
    if (kind === 'movies') {
        const q = new URLSearchParams({
            page,
            size,
            filter: $('filter-column').value,
            sort: $('sort-column').value,
            desc: $('sort-desc').checked
        });
        if ($('filter-enabled').checked) {
            const value = $('filter-value').value;
            q.set('value', value);
        }
        data = await api('movies?' + q);
    } else {
        const items = await api(kind);
        const lastPage = Math.max(0, Math.ceil(items.length / size) - 1);
        const currentPage = Math.min(page, lastPage);
        data = {items: items.slice(currentPage * size, (currentPage + 1) * size), total: items.length, page: currentPage};
    }
    if (request !== collectionRequest || kind !== state.kind || $('workspace').hidden) return;
    state.page = data.page;
    state.total = data.total;
    renderCollection(kind, data.items);
    bind($('page-info'), 'Страница {page} из {pages} · Объектов: {total}', {page: state.page + 1, pages: Math.max(1, Math.ceil(state.total / state.size)), total: state.total});
    $('previous').disabled = state.page === 0;
    $('next').disabled = (state.page + 1) * state.size >= state.total;
}

function renderCollection(kind, items) {
    const movies = kind === 'movies';
    const selected = movies ? items.find(row => row.id === state.selectedMovie) || items[0] : null;
    const activeRecord = document.activeElement.closest('.film-link, .record-link')?.closest('tr')?.dataset.id;
    const fields = movies ? movieFields : [['actions', 'Действия'], ['id', 'ID'], ...schemas[kind]];
    const columnClass = key => movies && key !== 'name' && key !== 'genre' ? 'movie-extra' : '';
    const header = node('tr');
    for (const [key, label] of fields) {
        const th = node('th', label, columnClass(key));
        th.scope = 'col';
        header.append(th);
    }
    const rows = document.createDocumentFragment();
    for (const row of items) {
        const tr = node('tr');
        tr.className = movies ? 'movie-row' : 'record-row';
        tr.dataset.id = row.id;
        tr.onclick = event => {
            const control = event.target.closest('button');
            if (control && !control.matches('.film-link, .record-link')) return;
            if (movies) {
                selectMovie(row, tr);
            } else {
                tr.querySelector('.record-link').focus({preventScroll: true});
                details(kind, row.id);
            }
        };
        for (const [key] of fields) {
            const td = node('td', undefined, columnClass(key));
            if (key === 'actions') {
                td.classList.add('row-actions');
                td.append(iconButton('edit', 'Изменить', () => edit(kind, row.id), 'secondary'),
                    iconButton('delete', 'Удалить', () => remove(kind, row), 'delete-button'));
            } else if (movies && key === 'name') {
                const film = node('button', undefined, 'film-link');
                film.type = 'button';
                film.setAttribute('aria-pressed', String(row === selected));
                film.append(node('strong', row.name), node('small', `#${row.id} · ${row.length} мин`));
                td.append(film);
            } else if (!movies && key === (kind === 'coordinates' ? 'id' : 'name')) {
                td.append(button(format(row[key], key), null, 'record-link'));
            } else {
                td.textContent = format(row[key], key);
            }
            tr.append(td);
        }
        rows.append(tr);
    }
    if (!items.length) {
        const tr = node('tr'), td = node('td', 'Объектов нет', 'empty-cell');
        td.colSpan = fields.length;
        tr.append(td);
        rows.append(tr);
    }
    $('columns').replaceChildren(header);
    $('rows').replaceChildren(rows);
    if (movies) {
        state.selectedMovie = selected?.id ?? null;
        renderMovieInspector(selected);
    }
    if (activeRecord) {
        const target = [...$('rows').rows].find(row => row.dataset.id === activeRecord)?.querySelector('.film-link, .record-link');
        (target || $('rows').querySelector('.film-link[aria-pressed="true"]') || $('create')).focus({preventScroll: true});
    }
}

function selectMovie(row, tr) {
    state.selectedMovie = row.id;
    const selected = $('rows').querySelector('.film-link[aria-pressed="true"]');
    const target = tr.querySelector('.film-link');
    selected?.setAttribute('aria-pressed', 'false');
    target.setAttribute('aria-pressed', 'true');
    target.focus({preventScroll: true});
    renderMovieInspector(row);
    if (compactScreen.matches || $('collection').classList.contains('full-table')) presentDetails('movies', row);
}

function setFullColumns(show) {
    $('collection').classList.toggle('full-table', show);
    $('full-columns').setAttribute('aria-pressed', String(show));
    $('object-table').parentElement.scrollLeft = 0;
}

async function navigate(kind) {
    state.kind = kind;
    state.page = 0;
    $('collection').hidden = ['operations','import','history'].includes(kind);
    $('import-page').hidden = kind !== 'import';
    $('history-page').hidden = kind !== 'history';
    $('operations').hidden = kind !== 'operations';
    $('filter-form').hidden = kind !== 'movies';
    $('movie-list-heading').hidden = kind !== 'movies';
    $('movie-inspector').hidden = true;
    if (schemas[kind]) {
        $('collection').dataset.kind = kind;
        bind($('heading'), titles[kind]);
        bind($('create-label'), createLabels[kind]);
        $('columns').replaceChildren();
        $('rows').replaceChildren();
        $('page-info').textContent = '';
        $('previous').disabled = true;
        $('next').disabled = true;
    }
    document.querySelectorAll('nav [data-view]').forEach(b => {
        if (b.dataset.view === kind) b.setAttribute('aria-current', 'page');
        else b.removeAttribute('aria-current');
    });
    try {
        await refresh();
    } catch (e) {
        notice(e.message, true);
    }
}

document.querySelectorAll('nav [data-view]').forEach(b => b.onclick = () => {
    navigate(b.dataset.view);
    $('main-content').focus({preventScroll: true});
});
$('full-columns').onclick = () => setFullColumns(!$('collection').classList.contains('full-table'));
$('import-history-link').onclick = () => navigate('history');
$('new-import-link').onclick = () => navigate('import');
$('filter-form').onsubmit = async e => {
    e.preventDefault();
    if (!Validation.form(e.target)) return;
    state.page = 0;
    try {
        await refresh();
    } catch (e) {
        notice(e.message, true);
    }
};
$('previous').onclick = async () => {
    state.page--;
    await refresh().catch(e => notice(e.message, true));
};
$('next').onclick = async () => {
    state.page++;
    await refresh().catch(e => notice(e.message, true));
};
$('page-size').onchange = async () => {
    state.size = Number($('page-size').value);
    state.page = 0;
    await refresh().catch(e => notice(e.message, true));
};
document.querySelectorAll('[data-close]').forEach(b => b.onclick = () => $(b.dataset.close).close());
$('create').onclick = () => edit(state.kind);

async function edit(kind, id) {
    try {
        const row = id ? await api(kind + '/' + id) : {};
        // 编辑快照：保存打开表单时的对象版本，它必须与本次编辑输入一起提交。
        // revision 轮询可以刷新列表，但不能在保留旧输入时把这个版本替换成最新版本。
        state.editing = {kind, id, version: row.version};
        $('fields').replaceChildren();
        bind($('edit-error'), '');
        bind($('edit-title'), () => t(id ? 'Изменить: {kind}' : 'Добавить: {kind}', {kind: t(titles[kind])}));
        bind($('edit-note'), '* Обязательное поле. Связанные объекты создаются в соответствующем разделе меню. ID и дата создания формируются автоматически.');
        const refs = {};
        for (const f of schemas[kind]) if (f[2] === 'ref' && !refs[f[4]]) refs[f[4]] = await api(f[4]);
        for (const [key, label, type, required, list, min, max] of schemas[kind]) {
            const wrapper = document.createElement('label');
            const caption = document.createElement('span');
            bind(caption, () => t(label) + (required ? ' *' : ''));
            wrapper.append(caption);
            let input;
            if (type === 'enum' || type === 'ref') {
                input = document.createElement('select');
                option(input, '', required ? 'Выберите…' : 'Не указано');
                if (type === 'enum') enums[list].forEach(v => option(input, v, v)); else refs[list].forEach(v => option(input, String(v.id), format(v)));
            } else {
                input = document.createElement('input');
                input.type = 'text';
                input.dataset.valueType = type;
                if (['integer', 'long', 'number'].includes(type)) input.inputMode = type === 'number' ? 'decimal' : 'numeric';
                // Long uses decimal text + BigInt validation to avoid JavaScript Number rounding.
                if (min !== undefined) input.dataset.min = min;
                if (max !== undefined) input.dataset.max = max;
                if (type === 'number' && min === 0) input.dataset.positive = 'true';
                if (['height', 'weight'].includes(key)) input.dataset.max = '3.4028235e38';
            }
            input.name = key;
            input.required = required && !['tagline', 'passportID'].includes(key) && !(kind === 'locations' && key === 'name');
            if (key === 'birthday') input.placeholder = '1990-01-01T12:00:00+03:00[Europe/Moscow]';
            input.value = row[key] === null || row[key] === undefined ? '' : type === 'ref' ? String(row[key].id) : row[key];
            wrapper.append(input);
            $('fields').append(wrapper);
        }
        Validation.attach($('edit-form'));
        if (!$('workspace').hidden) $('editor').showModal();
    } catch (e) {
        notice(e.message, true);
    }
}

$('edit-form').onsubmit = async e => {
    e.preventDefault();
    if (!Validation.form(e.target)) { bind($('edit-error'), 'Проверьте поля с красными подсказками.'); return; }
    const {kind, id, version} = state.editing;
    const data = {};
    for (const [key, , type, required] of schemas[kind]) {
        let value = e.target.elements.namedItem(key).value;
        data[key] = value === '' && !required ? null : value;/* preserve int64 as decimal strings */
    }
    // 提交的是编辑快照的版本，而不是列表刷新后可能取得的新版本；后端据此识别过期表单。
    if (id) data.version = version;
    $('save').disabled = true;
    try {
        const saved = await api(kind + (id ? '/' + id : ''), id ? 'PUT' : 'POST', data);
        if (kind === 'movies') state.selectedMovie = saved.id;
        $('editor').close();
        notice('Изменения сохранены');
        await refresh();
        if (state.detail && $('details').open) await details(state.detail.kind, state.detail.id, true);
    } catch (error) {
        Validation.server(e.target, error.raw || error.message);
        showError($('edit-error'), error);
    } finally {
        $('save').disabled = false;
    }
};

function renderObject(row) {
    const dl = document.createElement('dl');
    for (const [key, value] of Object.entries(row)) {
        const dt = document.createElement('dt'), dd = document.createElement('dd');
        bind(dt, () => UiText.field(key));
        if (value && typeof value === 'object') dd.append(renderObject(value)); else bind(dd, () => format(value, key));
        dl.append(dt, dd);
    }
    return dl;
}

const movieFactKeys = ['director', 'length', 'mpaaRating', 'oscarsCount', 'budget', 'usaBoxOffice', 'totalBoxOffice',
    'goldenPalmCount', 'screenwriter', 'operator', 'coordinates', 'creationDate'];
const integerFormat = new Intl.NumberFormat('ru-RU');

function movieFact(row, key) {
    const value = row[key];
    if (value == null) return '—';
    if (key === 'coordinates') return `${value.x}, ${value.y}`;
    if (key === 'length') return `${value} мин`;
    if (['budget', 'goldenPalmCount', 'usaBoxOffice'].includes(key)) return integerFormat.format(BigInt(value));
    return value.name ?? format(value, key);
}

function renderMovieFacts(row) {
    const facts = node('dl', undefined, 'facts');
    for (const key of movieFactKeys) {
        const field = node('div');
        field.append(node('dt', UiText.field(key)), node('dd', movieFact(row, key)));
        facts.append(field);
    }
    const content = document.createDocumentFragment();
    if (row.tagline) content.append(node('blockquote', row.tagline));
    content.append(facts);
    return content;
}

function renderMovieInspector(row) {
    const inspector = $('movie-inspector');
    inspector.hidden = !row;
    if (!row) {
        inspector.replaceChildren();
        return;
    }
    const header = node('header', undefined, 'desk-detail-head');
    const title = node('div');
    const heading = node('h2', row.name);
    heading.id = 'inspector-title';
    title.append(node('p', `Запись #${row.id}`, 'refine-kicker'), heading);
    header.append(title, node('span', format(row.genre, 'genre'), 'genre-text'));
    const actions = node('div', undefined, 'dialog-actions');
    actions.append(iconButton('edit', 'Редактировать', () => edit('movies', row.id)),
        button('Все данные', () => presentDetails('movies', row), 'secondary'),
        iconButton('delete', 'Удалить', () => remove('movies', row), 'delete-button'));
    inspector.replaceChildren(header, renderMovieFacts(row), actions);
}

let detailRequest = 0;

function presentDetails(kind, row) {
    detailRequest++;
    const previous = state.detail;
    state.detail = {kind, id: row.id};
    const movie = kind === 'movies';
    $('detail-title').textContent = movie ? row.name : 'Информация об объекте';
    const content = $('detail-content');
    if (movie) {
        const expanded = node('details', undefined, 'detail-fields');
        expanded.open = previous?.kind === kind && previous.id === row.id && !!content.querySelector('details[open]');
        expanded.append(node('summary', 'Все поля объекта'), renderObject(row));
        content.replaceChildren(node('p', `Запись #${row.id} · ${format(row.genre, 'genre')}`, 'refine-kicker'), renderMovieFacts(row), expanded);
    } else {
        content.replaceChildren(renderObject(row));
    }
    $('detail-edit').onclick = () => edit(kind, row.id);
    $('detail-delete').hidden = !movie;
    $('detail-delete').onclick = movie ? () => remove(kind, row) : null;
    if (!$('details').open) {
        $('details').showModal();
        content.scrollTop = 0;
    }
}

async function details(kind, id, updating = false) {
    const request = ++detailRequest;
    try {
        const row = await api(kind + '/' + id);
        if (request !== detailRequest || $('workspace').hidden || (updating && !$('details').open)) return;
        presentDetails(kind, row);
    } catch (e) {
        if (request !== detailRequest || $('workspace').hidden) return;
        notice(e.message, true);
        if ($('details').open) $('details').close();
    }
}

function remove(kind, row) {
    state.deleting = {kind, row};
    bind($('delete-message'), () => t('Удалить {kind} #{id}? При удалении координат или человека удаляются связанные фильмы; при удалении места — связанные люди и их фильмы. Независимые справочники при удалении фильма сохраняются.', {kind: t(titles[kind]), id: row.id}));
    bind($('delete-error'), '');
    $('delete-dialog').showModal();
}

$('delete-confirm').onclick = async () => {
    const {kind, row} = state.deleting;
    try {
        const r = await api(`${kind}/${row.id}?version=${row.version}`, 'DELETE');
        $('delete-dialog').close();
        if ($('details').open && state.detail?.kind === kind && state.detail.id === row.id) $('details').close();
        notice(() => t('Удалено объектов: {count}', {count: r.deleted}));
        await refresh();
    } catch (e) {
        showError($('delete-error'), e);
    }
};
document.querySelectorAll('[data-operation]').forEach(form => form.onsubmit = async e => {
    e.preventDefault();
    if (!Validation.form(form)) return;
    const op = form.dataset.operation;
    if (op === 'box-office' && !confirm(t('Удалить все фильмы с указанными сборами?'))) return;
    const q = new URLSearchParams(new FormData(form));
    const method = op === 'box-office' ? 'DELETE' : ['average', 'prefix'].includes(op) ? 'GET' : 'POST';
    const submit = form.querySelector('button');
    submit.disabled = true;
    const operationTitles = {'box-office': 'Удалить по сборам в США', average: 'Средние сборы в США', prefix: 'Найти по началу слогана', redistribute: 'Перераспределить «Оскары»', award: 'Дополнительные награды'};
    bind($('result-title'), operationTitles[op]);
    $('operation-result').replaceChildren();
    try {
        const result = await api('operations/' + op + '?' + q, method);
        if (op === 'prefix') {
            const p = document.createElement('p');
            bind(p, 'Найдено: {count}', {count: result.length});
            $('operation-result').append(p);
            result.forEach(row => {
                const d = document.createElement('details'), s = document.createElement('summary');
                s.textContent = format(row);
                d.append(s, renderObject(row), iconButton('edit', 'Изменить', () => { $('result-dialog').close(); edit('movies', row.id); }));
                $('operation-result').append(d);
            });
        } else {
            if (op === 'average') {
                const p = document.createElement('p');
                bind(p, () => t('Среднее: {value}', {value: result.average ?? t('нет данных')}));
                $('operation-result').append(p);
            } else {
                const labels = {deleted:'Удалено фильмов', updated:'Обновлено фильмов', transferred:'Передано наград', recipients:'Получателей', each:'Каждому', remainder:'Остаток'};
                const dl = document.createElement('dl');
                for (const [key, value] of Object.entries(result)) {
                    const term = document.createElement('dt'), valueNode = document.createElement('dd');
                    bind(term, labels[key] || key); valueNode.textContent = String(value); dl.append(term, valueNode);
                }
                $('operation-result').append(dl);
            }
        }
        notice('Операция выполнена');
    } catch (error) {
        const p = document.createElement('p'); p.className = 'error'; showError(p, error);
        $('operation-result').append(p);
    } finally {
        submit.disabled = false;
        if (!$('workspace').hidden && !$('result-dialog').open) $('result-dialog').showModal();
    }
});
setInterval(async () => {
    if ($('workspace').hidden || state.busy) return;
    state.busy = true;
    try {
        if (state.kind === 'history') await refreshHistory();
        const {revision} = await api('revision');
        if (state.revision !== revision) {
            const changed = state.revision !== null;
            // 列表与编辑表单是两份状态：refresh() 不覆盖表单输入，也不更新 state.editing.version。
            if (state.kind !== 'history') await refresh();
            if (changed) {
                const changedAt = new Date();
                notice(() => t('Коллекция обновлена · {time}', {time: changedAt.toLocaleTimeString('ru')}));
                if ($('details').open && state.detail) await details(state.detail.kind, state.detail.id, true);
                // 集合变化未必来自正在编辑的对象；这里只提示并保留草稿，是否过期由保存时的后端比较确定。
                if ($('editor').open) bind($('edit-note'), 'Коллекция изменилась. Ваш ввод сохранён; сервер проверит версию объекта при сохранении.');
            }
            state.revision = revision;
        }
    } catch (e) {
        notice(() => t('Нет связи: {message}', {message: e.message}), true);
    } finally {
        state.busy = false;
    }
}, 2000);
(async () => {
    try {
        const data = await api('auth');
        showSession(data);
        if (data.authenticated) await navigate('movies');
    } catch (e) {
        showError($('login-error'), e);
    }
})();

const importStatuses = {SUCCESS: ['Успешно', 'success'], FAILED: ['Ошибка', 'failure'], RUNNING: ['Выполняется', '']};
async function refreshHistory() {
    const request = ++historyRequest;
    const page = historyPage;
    const data = await api('imports?page=' + page + '&size=10');
    if (request !== historyRequest || state.kind !== 'history' || $('workspace').hidden) return;
    const rows = document.createDocumentFragment();
    for (const op of data.items) {
        const tr = node('tr'), status = node('td');
        const [label, variant] = importStatuses[op.status] || [op.status, ''];
        status.append(node('span', label, `badge ${variant}`));
        tr.append(node('td', op.id), status);
        for (const value of [op.user, op.status === 'SUCCESS' ? op.addedCount : '—', op.filename, op.startedAt, op.errorMessage || '—']) tr.append(node('td', value));
        rows.append(tr);
    }
    if (!data.items.length) {
        const tr = node('tr'), empty = node('td', 'Операций пока нет', 'empty-cell');
        empty.colSpan = 7;
        tr.append(empty);
        rows.append(tr);
    }
    $('history-rows').replaceChildren(rows);
    $('history-info').textContent = (page + 1) + ' / ' + Math.max(1, Math.ceil(data.total / 10)) + ' · ' + data.total;
    $('history-prev').disabled = page === 0;
    $('history-next').disabled = (page + 1) * 10 >= data.total;
}
$('history-prev').onclick = () => { historyPage--; refreshHistory().catch(e => notice(e.message, true)); };
$('history-next').onclick = () => { historyPage++; refreshHistory().catch(e => notice(e.message, true)); };
$('import-choose').onclick = () => $('import-file').click();
$('import-file').onchange = () => {
    $('import-filename').textContent = $('import-file').files[0]?.name || 'Файл не выбран';
    $('import-result').textContent = '';
    $('import-result').className = '';
};
$('dropzone').ondragover = event => {
    event.preventDefault();
    $('dropzone').classList.toggle('dragging', !$('import-submit').disabled && event.dataTransfer.types.includes('Files'));
};
$('dropzone').ondragleave = event => {
    if (!$('dropzone').contains(event.relatedTarget)) $('dropzone').classList.remove('dragging');
};
$('dropzone').ondrop = event => {
    event.preventDefault();
    $('dropzone').classList.remove('dragging');
    const file = event.dataTransfer.files[0];
    if (!file || $('import-submit').disabled) return;
    const transfer = new DataTransfer();
    transfer.items.add(file);
    $('import-file').files = transfer.files;
    $('import-file').onchange();
};
$('import-form').onsubmit = async event => {
    event.preventDefault();
    const file = $('import-file').files[0];
    if (!file) { bind($('import-result'), 'Выберите JSON-файл'); return; }
    if (file.size > 5242880) { bind($('import-result'), 'Файл превышает 5 MiB'); return; }
    const form = new FormData(); form.append('file', file, file.name);
    $('import-result').className = '';
    $('import-submit').disabled = true; bind($('import-result'), 'Импорт выполняется…');
    try {
        const result = await api('imports', 'POST', form);
        bind($('import-result'), 'Операция {id}: добавлено {count}', {id: result.operationId, count: result.addedCount});
        await refresh();
    } catch (error) {
        const data = error.data || {};
        const message = [data.operationId ? '#' + data.operationId : '', data.code, data.path, data.error || error.message].filter(Boolean).join(' · ');
        $('import-result').textContent = message;
        $('import-result').className = 'error';
    } finally { $('import-submit').disabled = false; }
};
