const variants = { A: 'Каталог', B: 'Инспектор', C: 'Витрина' };
const navigation = {
    movies: ['Фильмы', 'film'], people: ['Люди', 'users'], coordinates: ['Координаты', 'grid'], locations: ['Места', 'map'],
    import: ['Импорт JSON', 'upload'], history: ['История импорта', 'history'], operations: ['Спецоперации', 'sliders'],
};
const hashVariant = location.hash.slice(1);
const state = {
    variant: Object.hasOwn(variants, hashVariant) ? hashVariant : new URL(location.href).searchParams.get('variant'),
    view: 'movies', role: 'student', query: '', genre: '', sort: 'recent', page: 1, selected: 108,
    movies: structuredClone(initialMovies), history: structuredClone(initialHistory), nextMovie: 109, nextImport: 105,
    draft: null, importResult: null,
};
if (!Object.hasOwn(variants, state.variant)) state.variant = 'A';

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
    return `<button class="brand" type="button" data-action="navigate" data-id="movies"><span class="brand-mark">${icon('film', 22)}</span><span><strong>Кинотека</strong><small>ИТМО · ИНФОРМАЦИОННЫЕ СИСТЕМЫ</small></span></button>`;
}

function session() {
    return `<div class="session"><span class="demo-tag"><i></i>Демо-данные</span><label class="account"><span class="avatar" aria-hidden="true">${state.role === 'admin' ? 'A' : 'S'}</span><span><small>РОЛЬ В ДЕМО</small><select aria-label="Роль в демо" id="role">${options([['student', 'Пользователь'], ['admin', 'Администратор']], state.role)}</select></span></label></div>`;
}

function render() {
    document.body.dataset.variant = state.variant;
    document.querySelector('#variant-label').textContent = `${state.variant} · ${variants[state.variant]}`;
    const keys = Object.keys(navigation);
    const shell = state.variant === 'A'
        ? `<aside class="sidebar">${brand()}<nav aria-label="Главное меню"><p class="nav-label">КОЛЛЕКЦИЯ</p>${nav(keys.slice(0, 4))}<p class="nav-label">ИНСТРУМЕНТЫ</p>${nav(keys.slice(4))}</nav><div class="sidebar-foot"><span class="side-led"></span><span>Лабораторная работа № 2<small>Локальный прототип</small></span></div></aside>`
        : `<header class="mast"><div class="mast-top">${brand()}${session()}</div><nav aria-label="Главное меню" class="top-nav">${nav(keys)}</nav></header>`;
    const heading = `<div class="crumb"><span>Рабочая область</span>${icon('chevron', 12)}<strong>${navigation[state.view][0]}</strong></div>`;
    app.innerHTML = `${shell}<div class="workspace"><div class="topbar">${heading}${state.variant === 'A' ? session() : ''}</div><main id="main-content" tabindex="-1">${view()}</main><footer><span>Кинотека · Лабораторная работа № 2</span><span>Прототип интерфейса</span></footer></div>`;
    const menu = app.querySelector('nav');
    if (menu.scrollWidth > menu.clientWidth) {
        const current = menu.querySelector('[aria-current]');
        const overflow = current.getBoundingClientRect().right - menu.getBoundingClientRect().right;
        if (overflow > 0) menu.scrollLeft = overflow + 10;
    }
}

function view() {
    if (state.view === 'movies') return catalog();
    if (state.view === 'import') return importPage();
    if (state.view === 'history') return historyPage();
    if (state.view === 'operations') return operationsPage();
    return referencePage();
}

function filmStrip() {
    return `<svg class="hero-film" viewBox="0 0 540 204" fill="none" aria-hidden="true" preserveAspectRatio="xMidYMid slice">
        <defs><pattern id="perf" width="27" height="20" patternUnits="userSpaceOnUse"><rect x="4" y="4" width="12" height="8" rx="2" fill="#211b23"/></pattern><pattern id="frames" width="115" height="80" patternUnits="userSpaceOnUse"><path d="M2 1h111v78H2z" stroke="#f3c39d" stroke-opacity=".55"/><path d="m2 79 61-78m-17 78 61-78" stroke="#f3c39d" stroke-opacity=".2"/><circle cx="66" cy="40" r="25" stroke="#f3c39d" stroke-opacity=".38"/></pattern></defs>
        <g stroke="#b79089" opacity=".33"><circle cx="357" cy="99" r="142"/><circle cx="357" cy="99" r="102"/><circle cx="357" cy="99" r="58"/><path d="M357-36v272M221 99h272" stroke-dasharray="3 6"/></g>
        <g transform="translate(144 135) rotate(-25)"><rect width="440" height="117" rx="4" fill="#7a3040" stroke="#bb655f"/><rect x="8" y="0" width="425" height="20" fill="url(#perf)"/><rect x="8" y="99" width="425" height="18" fill="url(#perf)"/><rect x="10" y="19" width="422" height="80" fill="url(#frames)"/><path d="M148 59h37m-18-18v36" stroke="#ffd0a9" stroke-opacity=".65"/><circle cx="167" cy="59" r="33" stroke="#ffd0a9" stroke-opacity=".65"/></g>
        <text x="426" y="181" fill="#d7b0aa" font-family="monospace" font-size="10" letter-spacing="2">35 MM / 02</text>
    </svg>`;
}

function pageTitle(kicker, title, description, actions = '') {
    return `<section class="page-title"><div><p class="eyebrow"><span></span>${kicker}</p><h1>${title}</h1><p class="lede">${description}</p></div>${actions ? `<div class="title-actions">${actions}</div>` : ''}</section>`;
}

function catalog() {
    const add = action('Добавить фильм', 'create', 'plus', 'primary');
    const upload = action('Импорт JSON', 'navigate', 'upload', 'secondary', 'import');
    const intro = state.variant === 'A'
        ? `<section class="catalog-hero">${filmStrip()}<div class="hero-inner"><p class="eyebrow"><span></span>МЕДИАТЕКА / ЛАБОРАТОРНАЯ № 2</p><h1>Каталог фильмов</h1><p>Фильмы, их создатели и данные коллекции.</p><div class="hero-actions">${add}${upload}</div></div></section>`
        : pageTitle('МЕДИАТЕКА / ЛАБОРАТОРНАЯ № 2', 'Каталог фильмов', state.variant === 'B' ? 'Выберите фильм, чтобы открыть его карточку рядом со списком.' : 'Просматривайте коллекцию по названиям и жанрам.', add + upload);
    return `${intro}<section class="catalog-panel" aria-labelledby="collection-title"><div class="panel-head"><div><h2 id="collection-title">Все фильмы</h2><span id="catalog-count" class="count"></span></div><span class="panel-caption">${icon('film', 15)} Коллекция</span></div>
        <div class="filters"><label class="search">${icon('search')}<input type="search" id="query" value="${escapeHtml(state.query)}" placeholder="Найти фильм или режиссёра" aria-label="Поиск по фильму или режиссёру"></label>
        <label class="filter-select"><span>Жанр</span><select id="genre" aria-label="Жанр">${options([['', 'Все жанры'], ...genreOptions], state.genre)}</select></label>
        <label class="filter-select"><span>Сортировка</span><select id="sort" aria-label="Сортировка">${options([['recent', 'Новые сначала'], ['title', 'По названию'], ['oscars', 'По наградам']], state.sort)}</select></label></div>
        <div id="catalog-results"></div></section>`;
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
    const movies = visibleMovies();
    document.querySelector('#catalog-count').textContent = movies.length;
    if (!movies.length) {
        results.innerHTML = `<div class="empty">${icon('search', 27)}<h3>Фильмы не найдены</h3><p>Измените запрос или сбросьте фильтры.</p>${action('Сбросить фильтры', 'reset-filter')}</div>`;
        return;
    }
    const pageSize = state.variant === 'A' ? 6 : 9;
    const pages = Math.ceil(movies.length / pageSize);
    state.page = Math.min(state.page, pages);
    const start = (state.page - 1) * pageSize;
    const slice = movies.slice(start, start + pageSize);
    const layout = state.variant === 'A' ? tableCatalog(slice) : state.variant === 'B' ? inspectorCatalog(slice) : galleryCatalog(slice);
    results.innerHTML = `${layout}<div class="panel-foot"><span>Показано ${start + 1}–${start + slice.length} из ${movies.length}</span><div class="pagination"><button type="button" data-action="prev-page" aria-label="Предыдущая страница" ${state.page === 1 ? 'disabled' : ''}>‹</button><span>${state.page} / ${pages}</span><button type="button" data-action="next-page" aria-label="Следующая страница" ${state.page === pages ? 'disabled' : ''}>›</button></div></div>`;
}

function genreBadge(genre) {
    return `<span class="badge genre-${genre?.toLowerCase() ?? 'none'}">${genreLabel(genre)}</span>`;
}

function reel(movie) {
    return `<span class="reel reel-${movie.genre?.toLowerCase() ?? 'none'}">${icon('film', 17)}</span>`;
}

function tableCatalog(movies) {
    return `<div class="table-scroll"><table class="film-table"><thead><tr><th scope="col">Фильм</th><th scope="col">Жанр</th><th scope="col">Режиссёр</th><th scope="col">Рейтинг</th><th scope="col">«Оскары»</th><th scope="col"><span class="sr-only">Карточка</span></th></tr></thead><tbody>${movies.map(movie => `<tr>
        <td><button class="film-link" type="button" data-action="detail" data-id="${movie.id}">${reel(movie)}<span><strong>${escapeHtml(movie.name)}</strong><small>${movieCode(movie.id)} · ${movie.length} мин</small></span></button></td>
        <td>${genreBadge(movie.genre)}</td><td>${escapeHtml(movie.director?.name || '—')}</td><td><span class="rating">${ratingLabel(movie.mpaaRating)}</span></td><td><span class="awards">${icon('award', 15)}${movie.oscarsCount}</span></td><td><button class="icon-button" type="button" data-action="detail" data-id="${movie.id}" aria-label="Открыть карточку: ${escapeHtml(movie.name)}">${icon('chevron', 15)}</button></td>
        </tr>`).join('')}</tbody></table></div>`;
}

function inspectorCatalog(movies) {
    const selected = movies.find(movie => movie.id === state.selected) || movies[0];
    state.selected = selected.id;
    return `<div class="inspector"><div class="inspector-list" aria-label="Список фильмов">${movies.map(movie => `<button class="inspect-link ${movie.id === selected.id ? 'active' : ''}" type="button" data-action="select-movie" data-id="${movie.id}" aria-pressed="${movie.id === selected.id}">${reel(movie)}<span><strong>${escapeHtml(movie.name)}</strong><small>${genreLabel(movie.genre)} · ${movie.length} мин</small></span>${icon('chevron', 15)}</button>`).join('')}</div><article class="inspect-main" aria-labelledby="inspect-title"><div class="inspect-heading"><div><p class="eyebrow"><span></span>КАРТОЧКА ${movieCode(selected.id)}</p><h3 id="inspect-title">${escapeHtml(selected.name)}</h3></div>${genreBadge(selected.genre)}</div>${movieFacts(selected)}<div class="dialog-actions">${action('Редактировать', 'edit', 'edit', 'primary', selected.id)}${action('Удалить', 'delete', '', 'secondary', selected.id)}</div></article></div>`;
}

function galleryCatalog(movies) {
    return `<div class="gallery">${movies.map(movie => `<button class="gallery-card" type="button" data-action="detail" data-id="${movie.id}"><span class="poster poster-${movie.genre?.toLowerCase() ?? 'none'}" data-motif="${movie.id % 3}"><span class="poster-code">КИНОТЕКА / ${movieCode(movie.id)}</span><span class="poster-figure"></span><span class="poster-rating">${ratingLabel(movie.mpaaRating)}</span></span><span class="gallery-info"><span><strong>${escapeHtml(movie.name)}</strong><small>${genreLabel(movie.genre)} · ${movie.length} мин</small></span>${icon('arrow', 19)}</span></button>`).join('')}</div>`;
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

function switchVariant(delta) {
    const keys = Object.keys(variants);
    state.variant = keys[(keys.indexOf(state.variant) + delta + keys.length) % keys.length];
    const url = new URL(location.href);
    url.searchParams.set('variant', state.variant);
    url.hash = '';
    try { window.history.replaceState(null, '', url); }
    catch { location.hash = state.variant; }
    state.page = 1;
    refresh();
    window.scrollTo(0, 0);
}

function importPage() {
    const draft = state.draft;
    const result = state.importResult;
    return `${pageTitle('ИНСТРУМЕНТЫ / ИМПОРТ', 'Импорт JSON', 'Добавьте несколько фильмов из одного файла.', action('История импорта', 'navigate', 'history', 'secondary', 'history'))}
        <div class="utility-layout"><section class="surface"><div class="surface-head"><div><p class="eyebrow"><span></span>ПАКЕТНАЯ ЗАГРУЗКА</p><h2>Файл с фильмами</h2></div><span class="format-tag">.JSON</span></div>
        <div class="dropzone" id="dropzone"><span class="upload-mark">${icon('upload', 23)}</span><strong>${draft ? escapeHtml(draft.name) : 'Перетащите сюда JSON-файл'}</strong><p>${draft?.pending ? 'Читаем файл…' : draft ? 'Файл выбран. Запустите пробный импорт.' : 'Один файл в UTF-8, до 5 МиБ'}</p>${action(draft ? 'Заменить файл' : 'Выбрать файл', 'pick-file')}
        <input id="file-input" type="file" accept=".json,application/json" hidden></div>
        <div class="import-actions"><div class="example-actions">${action('Взять пример', 'sample', 'file', 'text-button')}${action('Пример с ошибкой', 'bad-sample', '', 'text-button')}</div><button type="button" class="button primary" data-action="commit-import" ${draft && !draft.pending ? '' : 'disabled'}>${icon('upload')}Импортировать</button></div>
        ${result ? `<div class="import-result ${result.ok ? 'success' : 'failure'}" role="status">${icon(result.ok ? 'check' : 'close')}<div><strong>${result.ok ? `Добавлено фильмов: ${result.count}` : 'Импорт отменён'}</strong><p>${result.ok ? `Операция ${movieCode(result.id)} записана в историю.` : `${escapeHtml(result.error)} В коллекции ничего не изменилось.`}</p></div></div>` : ''}
        </section><aside class="surface guide"><span class="guide-icon">${icon('shield', 22)}</span><h2>Как проходит импорт</h2><ol><li><strong>Выберите файл</strong><span>Формат версии 1, от 1 до 1000 фильмов.</span></li><li><strong>Проверьте результат</strong><span>Ошибка в одной записи отменяет весь пакет.</span></li><li><strong>Откройте историю</strong><span>Там сохраняются и успешные, и отклонённые операции.</span></li></ol>${action('Скачать пример JSON', 'download', 'download', 'text-button')}</aside></div>`;
}

function historyPage() {
    const entries = state.history.filter(item => state.role === 'admin' || item.user === 'student');
    return `${pageTitle('ИНСТРУМЕНТЫ / ЖУРНАЛ', 'История импорта', state.role === 'admin' ? 'В режиме администратора видны операции всех пользователей.' : 'В режиме пользователя видны только ваши операции.', action('Новый импорт', 'navigate', 'upload', 'primary', 'import'))}
    <section class="catalog-panel"><div class="panel-head"><div><h2>${state.role === 'admin' ? 'Все операции' : 'Мои операции'}</h2><span class="count">${entries.length}</span></div><span class="panel-caption">${icon('shield', 15)} ${state.role === 'admin' ? 'Администратор' : 'Пользователь'}</span></div>
    <div class="table-scroll"><table class="history-table"><thead><tr>${['ID', 'Статус', 'Файл', 'Пользователь', 'Добавлено', 'Время', ''].map(label => `<th scope="col">${label || '<span class="sr-only">Карточка</span>'}</th>`).join('')}</tr></thead><tbody>${entries.map(item => `<tr><td class="mono">${movieCode(item.id)}</td><td><span class="badge ${item.ok ? 'success' : 'failure'}"><i></i>${item.ok ? 'Успешно' : 'Ошибка'}</span></td><td><strong>${escapeHtml(item.file)}</strong></td><td>${item.user}</td><td>${item.ok ? item.count : '—'}</td><td>${escapeHtml(item.date)}</td><td><button class="icon-button" type="button" data-action="history-detail" data-id="${item.id}" aria-label="Операция ${movieCode(item.id)}">${icon('chevron', 15)}</button></td></tr>`).join('')}</tbody></table></div></section>`;
}

function referencePage() {
    const records = {
        people: ['Создатели фильмов в демо-коллекции.', ['ID', 'Имя', 'Место', 'Паспорт'], people.map(item => [item.id, item.name, item.city, item.passportID])],
        coordinates: ['Координаты, доступные в карточках фильмов.', ['ID', 'X', 'Y'], coordinates.map(item => [item.id, item.x, item.y])],
        locations: ['Города, связанные с участниками коллекции.', ['ID', 'Название'], people.map(item => [item.id, item.city])],
    };
    const [description, columns, rows] = records[state.view];
    return `${pageTitle('КОЛЛЕКЦИЯ / СПРАВОЧНИК', navigation[state.view][0], description)}<section class="catalog-panel"><div class="panel-head"><div><h2>Записи</h2><span class="count">${rows.length}</span></div><span class="panel-caption">Только просмотр</span></div><div class="table-scroll"><table><thead><tr>${columns.map(label => `<th scope="col">${label}</th>`).join('')}</tr></thead><tbody>${rows.map(row => `<tr>${row.map(value => `<td>${escapeHtml(value)}</td>`).join('')}</tr>`).join('')}</tbody></table></div></section>`;
}

const operationSpecs = [
    ['average', 'Средние сборы в США', 'Среднее по всем фильмам в коллекции.', 'Рассчитать', 'grid'],
    ['prefix', 'Поиск по слогану', 'Найдите фильм по первым буквам его слогана.', 'Найти', 'search'],
    ['award', 'Дополнительные награды', 'Добавьте «Оскары» фильмам длиннее заданного порога.', 'Наградить', 'award'],
    ['redistribute', 'Перераспределение наград', 'Каждый фильм-источник сохраняет одну награду.', 'Перераспределить', 'sliders'],
    ['delete', 'Удаление по сборам в США', 'Удалите фильмы с указанной суммой сборов.', 'Найти совпадения', 'film'],
];

function operationsPage() {
    return `${pageTitle('ИНСТРУМЕНТЫ / КОЛЛЕКЦИЯ', 'Специальные операции', 'Запускайте выборки и пакетные действия на демо-данных.')}<div class="operations-grid">${operationSpecs.map(([key, title, description, label, glyph]) => `<section class="surface operation"><span class="guide-icon">${icon(glyph)}</span><h2>${title}</h2><p>${description}</p>${action(label, 'operation', 'arrow', 'secondary', key)}</section>`).join('')}</div>`;
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
    openDialog(`${dialogHeader(`КАРТОЧКА ${movieCode(movie.id)}`, escapeHtml(movie.name))}<div class="dialog-body">${genreBadge(movie.genre)}${movieFacts(movie)}</div><div class="dialog-actions">${action('Редактировать', 'edit', 'edit', 'primary', movie.id)}${action('Удалить', 'delete', '', 'secondary', movie.id)}</div>`);
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
    const button = event.target.closest('[data-action]');
    if (!button) return;
    const { action: command, id } = button.dataset;
    const movie = state.movies.find(item => item.id === Number(id));
    switch (command) {
        case 'navigate': navigate(id); break;
        case 'variant-prev': switchVariant(-1); break;
        case 'variant-next': switchVariant(1); break;
        case 'prev-page': case 'next-page': {
            state.page += command === 'prev-page' ? -1 : 1;
            refreshCatalog();
            document.querySelector(`[data-action="${command}"]:enabled, .film-link, .inspect-link, .gallery-card`)?.focus({ preventScroll: true });
            break;
        }
        case 'reset-filter': state.query = ''; state.genre = ''; state.page = 1; refresh(); document.querySelector('#query').focus(); break;
        case 'select-movie': state.selected = movie.id; refreshCatalog(); document.querySelector(`[data-action="select-movie"][data-id="${id}"]`).focus({ preventScroll: true }); break;
        case 'detail': showMovie(movie); break;
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

document.addEventListener('keydown', event => {
    if (dialog.open || event.altKey || event.ctrlKey || event.metaKey || event.target.closest('input, select, textarea, [contenteditable]')) return;
    if (event.key !== 'ArrowLeft' && event.key !== 'ArrowRight') return;
    event.preventDefault();
    switchVariant(event.key === 'ArrowLeft' ? -1 : 1);
});

refresh();
