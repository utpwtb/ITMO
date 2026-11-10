const genres = { COMEDY: 'Комедия', TRAGEDY: 'Трагедия', WESTERN: 'Вестерн', HORROR: 'Ужасы' };
const ratings = ['G', 'PG', 'PG_13', 'R', 'NC_17'];
const people = [
    { id: 1, name: 'Анна Волкова', passportID: 'DEMO-001', city: 'Санкт-Петербург' },
    { id: 2, name: 'Михаил Орлов', passportID: 'DEMO-002', city: 'Москва' },
    { id: 3, name: 'Елена Крылова', passportID: 'DEMO-003', city: 'Казань' },
    { id: 4, name: 'Денис Беляев', passportID: 'DEMO-004', city: 'Екатеринбург' },
    { id: 5, name: 'Софья Лебедева', passportID: 'DEMO-005', city: 'Владивосток' },
    { id: 6, name: 'Артём Соколов', passportID: 'DEMO-006', city: 'Томск' },
];
const coordinates = [
    { id: 1, x: 120, y: -18 }, { id: 2, x: 440, y: 32 }, { id: 3, x: 826, y: 50 },
];
const initialMovies = [
    ['Последний сеанс', 'TRAGEDY', 1, 114, 3, 'PG_13', 'Один зал. Одна ночь. Последний показ.'],
    ['Письма с маяка', 'TRAGEDY', 2, 102, 2, 'PG', 'Море хранит то, о чём молчат письма.'],
    ['Полдень в пустыне', 'WESTERN', 3, 128, 4, 'PG_13', 'Когда солнце в зените, тени исчезают.'],
    ['Второй билет', 'COMEDY', 4, 96, 1, 'PG', 'Случайная встреча по билету на двоих.'],
    ['Дом без окон', 'HORROR', 5, 108, 2, 'R', 'У каждой комнаты есть свой секрет.'],
    ['Ночной экспресс', 'COMEDY', 6, 104, 1, 'PG', 'До утра ещё целая поездка.'],
    ['За линией горизонта', 'WESTERN', 3, 122, 2, 'PG_13', 'Дорога дальше, чем кажется.'],
    ['Тихая вода', 'HORROR', 5, 92, 1, 'R', 'В темноте слышно даже тишину.'],
].map(([name, genre, director, length, oscarsCount, mpaaRating, tagline], index) => ({
    id: 108 - index, name, genre, director: people[director - 1], length, oscarsCount, mpaaRating, tagline,
    coordinates: coordinates[index % coordinates.length], budget: String(2000000 + index * 350000),
    usaBoxOffice: 1700000 + index * 100000, totalBoxOffice: 4200000 + index * 400000,
    goldenPalmCount: index === 0 ? '1' : null, screenwriter: null, operator: null,
}));

const initialHistory = [
    { id: 104, ok: true, user: 'student', count: 2, file: 'premieres.json', date: '27 окт. 2026, 15:42' },
    { id: 103, ok: false, user: 'editor', file: 'october.json', date: '27 окт. 2026, 15:19', error: 'Запись 2: фильм с таким названием и режиссёром уже существует.' },
    { id: 102, ok: true, user: 'admin', count: 4, file: 'archive.json', date: '26 окт. 2026, 18:04' },
    { id: 101, ok: false, user: 'student', file: 'draft.json', date: '26 окт. 2026, 11:28', error: 'Запись 1: поле «Название» обязательно.' },
];

const exampleImport = {
    formatVersion: 1,
    movies: [
        { name: 'Звук проектора', coordinates: { x: 120, y: -18 }, oscarsCount: 1, budget: '1000000',
            totalBoxOffice: 1500000, mpaaRating: 'PG', director: null, screenwriter: null, operator: null,
            length: 88, goldenPalmCount: null, usaBoxOffice: 500000, tagline: 'Всё началось с одного кадра.', genre: 'COMEDY' },
        { name: 'По ту сторону экрана', coordinates: { x: 440, y: 32 }, oscarsCount: 2, budget: '2000000',
            totalBoxOffice: null, mpaaRating: 'PG_13', director: null, screenwriter: null, operator: null,
            length: 103, goldenPalmCount: null, usaBoxOffice: 700000, tagline: 'Следующий кадр всё меняет.', genre: 'TRAGEDY' },
    ],
};

const icons = {
    film: '<rect x="3" y="3" width="18" height="18" rx="2"/><path d="M7 3v18M17 3v18M3 8h4m-4 8h4m10-8h4m-4 8h4M7 12h10"/>',
    user: '<circle cx="12" cy="8" r="3.5"/><path d="M5 21v-2a5 5 0 0 1 5-5h4a5 5 0 0 1 5 5v2"/>',
    users: '<path d="M16 21v-2a4 4 0 0 0-4-4H6a4 4 0 0 0-4 4v2m20 0v-2a4 4 0 0 0-3-4M16 3a4 4 0 0 1 0 8"/><circle cx="9" cy="7" r="4"/>',
    map: '<path d="M20 10c0 5-8 11-8 11s-8-6-8-11a8 8 0 1 1 16 0Z"/><circle cx="12" cy="10" r="2.5"/>',
    grid: '<path d="M3 8h18M3 16h18M8 3v18m8-18v18"/>',
    upload: '<path d="M12 16V3m-5 5 5-5 5 5M4 15v5a1 1 0 0 0 1 1h14a1 1 0 0 0 1-1v-5"/>',
    history: '<path d="M3 11a9 9 0 1 1 2.7 6.5M3 4v7h7m2-4v5l3 2"/>',
    sliders: '<path d="M5 4v16M12 4v16m7-16v16M2 9h6m1 7h6m1-9h6"/>',
    search: '<circle cx="10.5" cy="10.5" r="6"/><path d="m15 15 5 5"/>',
    plus: '<path d="M12 5v14M5 12h14"/>',
    arrow: '<path d="M4 12h15m-6-6 6 6-6 6"/>',
    chevron: '<path d="m9 5 7 7-7 7"/>',
    down: '<path d="m6 9 6 6 6-6"/>',
    clock: '<circle cx="12" cy="12" r="9"/><path d="M12 7v5l3 2"/>',
    award: '<circle cx="12" cy="9" r="6"/><path d="m8 14-2 7 6-3 6 3-2-7"/>',
    file: '<path d="M5 3h9l5 5v13H5zM14 3v6h5M8 13h8m-8 4h6"/>',
    check: '<path d="m5 12 4 4L19 6"/>',
    close: '<path d="m6 6 12 12M6 18 18 6"/>',
    edit: '<path d="m4 16 12-12a2.1 2.1 0 0 1 3 3L7 19l-4 1zm10-10 3 3"/>',
    shield: '<path d="m12 3 8 3v6c0 4-4 7-8 9-4-2-8-5-8-9V6z"/><path d="m9 12 2 2 4-4"/>',
    download: '<path d="M12 3v13m-5-5 5 5 5-5M4 17v4h16v-4"/>',
};
