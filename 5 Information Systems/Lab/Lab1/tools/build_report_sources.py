from pathlib import Path
import re, shutil, json
base=Path(__file__).resolve().parents[1]
report=base/'report'; report.mkdir(exist_ok=True)
def put(name,text): (report/name).write_text(text,encoding='utf-8')
put('report.tex',r'''% XeLaTeX: два запуска; либо tectonic report.tex
\documentclass[12pt,a4paper]{article}
\usepackage{fontspec}
\IfFontExistsTF{Times New Roman}{\setmainfont{Times New Roman}}{\setmainfont{CMU Serif}}
\IfFontExistsTF{Arial}{\setsansfont{Arial}}{\setsansfont{CMU Sans Serif}}
\IfFontExistsTF{Consolas}{\setmonofont{Consolas}[Scale=0.85]}{\setmonofont{DejaVu Sans Mono}[Scale=0.8]}
\usepackage{polyglossia}
\setdefaultlanguage{russian}
\setotherlanguage{english}
\usepackage[left=30mm,right=15mm,top=20mm,bottom=20mm]{geometry}
\usepackage{amsmath,amssymb,array,longtable,booktabs,enumitem}
\usepackage{tikz}
\usetikzlibrary{arrows.meta,positioning,fit,calc}
\usepackage{setspace,graphicx,float,fvextra,xurl,needspace}
\usepackage{hyperref}
\hypersetup{unicode=true,colorlinks=true,linkcolor=black,urlcolor=blue,citecolor=black,
pdftitle={Лабораторная работа № 1. Информационная система управления фильмами. Вариант 4101},pdfauthor={Чэнь Хаолинь}}
\onehalfspacing
\setlength{\parindent}{1.25cm}
\setlength{\emergencystretch}{3em}
\setlist{nosep,leftmargin=*}
\renewcommand{\arraystretch}{1.15}
\newcolumntype{L}[1]{>{\raggedright\arraybackslash}p{#1}}
\setcounter{tocdepth}{2}
\fvset{fontsize=\scriptsize,breaklines=true,breakanywhere=true,tabsize=2,numbersep=6pt}
\begin{document}
\input{titlepage.tex}
\setcounter{page}{2}
\tableofcontents
\clearpage
\input{body.tex}
\clearpage
\appendix
\input{source-code.tex}
\end{document}
''')
put('titlepage.tex',r'''\begin{titlepage}
\centering
Федеральное государственное автономное \\
образовательное учреждение высшего образования \\
\textbf{«Национальный исследовательский университет ИТМО»} \\
\vfill
Информационные системы\\
\vspace{0.5\baselineskip}
\textbf{Лабораторная работа № 1} \\
\vspace{0.5\baselineskip}
Информационная система управления фильмами\\
Вариант 4101\\
\vfill
\begin{flushright}
Выполнил:\\
Чэнь Хаолинь P3216 407960\\
Преподаватель:\\
Коновалов Арсений Антонович\\
\end{flushright}
\vspace{4\baselineskip}
\centering
г. Санкт-Петербург, 2026
\end{titlepage}
''')
def esc(s):
 return ''.join({'\\':r'\textbackslash{}','&':r'\&','%':r'\%','$':r'\$','#':r'\#','_':r'\_','{':r'\{','}':r'\}','~':r'\textasciitilde{}','^':r'\textasciicircum{}'}.get(c,c) for c in s)
def inline(s):
 pieces=re.split(r'(`[^`]+`|\*\*.*?\*\*)',s)
 return ''.join(r'\texttt{'+esc(p[1:-1])+'}' if p.startswith('`') else r'\textbf{'+esc(p[2:-2])+'}' if p.startswith('**') else esc(p) for p in pieces)
text=(base/'Lab1.md').read_text(encoding='utf-8')
lines=text[text.index('## 1.'):text.index('## 7.')].splitlines()
result=[];code=False;bullets=False
for line in lines:
 if line.startswith('```'):
  if bullets:result.append(r'\end{itemize}');bullets=False
  result.append(r'\begin{Verbatim}' if not code else r'\end{Verbatim}');code=not code;continue
 if code:result.append(line);continue
 if line.startswith('- '):
  if not bullets:result.append(r'\begin{itemize}');bullets=True
  result.append(r'\item '+inline(line[2:]));continue
 if bullets:result.append(r'\end{itemize}');bullets=False
 if line.startswith('## '): result.append(r'\subsection{'+esc(re.sub(r'^\d+\.\s*','',line[3:]))+'}')
 elif line.startswith('> '):result.append(inline(line[2:]))
 else:result.append(inline(line))
if bullets:result.append(r'\end{itemize}')
put('assignment.tex','\n'.join(result))
put('classes.tex',r'''\begin{figure}[H]
\centering
\begin{tikzpicture}[font=\scriptsize,box/.style={draw,rounded corners=1pt,align=left,inner sep=7pt,anchor=north west},link/.style={-{Stealth[length=2mm]},thick}]
\node[box,text width=6.0cm] (movie) at (0,0) {\textbf{\large Movie}\\\rule{6cm}{0.4pt}\\
id: Long \{identity\}\\
name: String\\
coordinates: Coordinates\\
creationDate: LocalDate \{DB default\}\\
oscarsCount: int\\budget: long\\totalBoxOffice: Double\\
mpaaRating: MpaaRating\\director: Person\\screenwriter: Person\\operator: Person\\length: Integer\\goldenPalmCount: Long\\usaBoxOffice: int\\tagline: String\\genre: MovieGenre\\\rule{6cm}{0.4pt}\\version: long \{optimistic lock\}};
\node[box,text width=5.6cm] (person) at (8,0) {\textbf{\large Person}\\\rule{5.6cm}{0.4pt}\\
id: Long \{identity\}\\name: String\\eyeColor: Color\\hairColor: Color\\location: Location\\birthday: ZonedDateTime\\height: Float\\weight: Float\\passportID: String \{unique\}\\version: long};
\node[box,text width=5.6cm,below=1.4cm of person.south west,anchor=north west] (location) {\textbf{\large Location}\\\rule{5.6cm}{0.4pt}\\id: Long \{identity\}\\x: Long\\y: Double\\name: String\\version: long};
\node[box,text width=6cm,below=1.0cm of movie.south west,anchor=north west] (coordinates) {\textbf{\large Coordinates}\\\rule{6cm}{0.4pt}\\id: Long \{identity\}\\x: Integer \{x $\leq$ 826\}\\y: Integer\\version: long};
\draw[link] (movie.east |- person.center) -- node[above,align=center]{3 роли} node[below]{0..* : 0..1} (person.west);
\draw[link] (person.south) -- node[right]{0..* : 0..1} (location.north);
\draw[link] (movie.south) -- node[right]{0..* : 1} (coordinates.north);
\end{tikzpicture}
\caption{UML-диаграмма сущностей. Стрелки показывают навигацию; каскад удаления направлен от справочного объекта к зависимым объектам.}
\end{figure}
\noindent Перечисления: \texttt{MpaaRating \{G, PG, PG\_13, R, NC\_17\}}, \texttt{MovieGenre \{WESTERN, COMEDY, TRAGEDY, HORROR\}}, \texttt{Color \{GREEN, BLACK, ORANGE, WHITE, BROWN\}}. Тип \texttt{Country \{GERMANY, VATICAN, ITALY, NORTH\_KOREA\}} включён в исходники, но не имеет связей в модели варианта.
''')
put('packages.tex',r'''\begin{figure}[H]
\centering
\begin{tikzpicture}[font=\small,pkg/.style={draw,align=center,minimum width=5.4cm,minimum height=1.45cm,fill=gray!5},dep/.style={dashed,-{Stealth},thick}]
\node[pkg] (ui) at (0,0) {\textit{«artifact»}\; webapp\\index.html, app.js, style.css};
\node[pkg] (web) at (0,-2.6) {\textit{«package»}\; web\\MovieResource, AuthResource\\AuthFilter, ErrorMapper};
\node[pkg] (svc) at (0,-5.4) {\textit{«package»}\; service\\MovieService, Problem};
\node[pkg] (repo) at (0,-8) {\textit{«package»}\; persistence\\Database};
\node[pkg,minimum width=4.4cm] (model) at (7,-5.4) {\textit{«package»}\; domain\\Movie, Person, Coordinates\\Location, AppState, enum\\конвертеры};
\node[pkg] (db) at (0,-10.6) {\textit{«database»}\; PostgreSQL\\movie, person, coordinates\\location, app\_state};
\draw[dep] (ui)--node[right]{HTTP / JSON} (web);
\draw[dep] (web)--node[right]{CDI @Inject} (svc);
\draw[dep] (svc)--node[right]{read / write} (repo);
\draw[dep] (repo)--node[right]{JPA / EclipseLink / JDBC} (db);
\draw[dep] (svc)--(model);
\draw[dep] (web.east) -| (model.north);
\draw[dep] (repo.east) -| (model.south);
\end{tikzpicture}
\caption{UML-диаграмма пакетов и внешних компонентов. Зависимости направлены от использующего компонента к используемому.}
\end{figure}
''')
put('body.tex',r'''\section{Цель работы и исходное задание}
Цель работы: разработать многопользовательскую информационную систему управления фильмами, реализовать ограничения предметной области на уровне ORM и PostgreSQL, обеспечить транзакционные операции и автоматическое обновление интерфейсов. Вариант: \textbf{4101}.

Ниже приведён текст задания из файла \texttt{Lab1.md}; далее отдельно описаны решения, принятые при реализации.
\input{assignment.tex}

\section{Принятые решения и архитектура}
\subsection{Технологический стек и управляемые компоненты}
Приложение упаковано в WAR и развёрнуто в Payara Micro 6.2025.1. Используется Jakarta EE 10: CDI, Jakarta REST, Servlet, JSON-B, Bean Validation и Jakarta Persistence 3.1. Jakarta EE является продолжением Java EE; компоненты приложения являются управляемыми CDI-бинами. \texttt{MovieResource} и \texttt{AuthResource} имеют область \texttt{@RequestScoped}; \texttt{MovieService} и \texttt{Database} имеют область \texttt{@ApplicationScoped}. Зависимости передаются контейнером через \texttt{@Inject}.

ORM-провайдер явно задан: \texttt{org.eclipse.persistence.jpa.PersistenceProvider}. Используется EclipseLink 4.0.5. Наличие Hibernate Validator в тестах относится только к Bean Validation; Hibernate ORM в проекте не используется. Код компилируется с \texttt{release=17}; проверка выполнена на JDK 21.0.6 и PostgreSQL 17.4.

\subsection{Разделение ответственности}
REST-ресурсы принимают запросы и передают их сервису. Сервис проверяет данные, разрешает ссылки по ID и выполняет специальные операции. Компонент \texttt{Database} создаёт отдельный \texttt{EntityManager} для каждого запроса, выполняет транзакции типа \texttt{RESOURCE\_LOCAL}, завершает их или откатывает. Сущности находятся в пакете \texttt{domain}. Браузер отвечает только за ввод и отображение; SQL, правила изменения и расчёты наград на клиент не переносятся.

Для данной учебной системы выбраны явные локальные JPA-транзакции внутри CDI-компонента; распределённые JTA-транзакции не нужны. Используются слоистая архитектура, внедрение зависимостей и единица работы. Фабрика EntityManager является общей, сам EntityManager не разделяется между потоками.

\input{packages.tex}
\clearpage
\subsection{UML-диаграмма классов}
\input{classes.tex}

\subsection{Ограничения и хранение связей}
\begin{longtable}{L{3.2cm}L{5.0cm}L{6.3cm}}
\toprule Объект / правило & ORM и сервис & PostgreSQL\\\midrule\endhead
ID & \texttt{@GeneratedValue(IDENTITY)}; ввод ID запрещён & identity, PK, \texttt{CHECK(id>0)}\\
Строки & \texttt{@NotNull}, для имени \texttt{@Size(min=1)} & \texttt{NOT NULL}, \texttt{length(name)>0}\\
Положительные числа & \texttt{@Positive}; проверка диапазона и конечности & \texttt{CHECK(value>0)}, исключение Infinity и NaN\\
Координаты & \texttt{@NotNull}, \texttt{@Max(826)} & \texttt{NOT NULL}, \texttt{CHECK(x<=826)}\\
Паспорт & \texttt{unique=true}; запрос проверки уникальности & \texttt{UNIQUE}, \texttt{NOT NULL}\\
Дата создания & поле недоступно для изменения; обновление после INSERT & \texttt{DEFAULT CURRENT\_DATE}, \texttt{NOT NULL}\\
Дата рождения & \texttt{ZonedDateTime}, JPA converter & текст ISO, проверка формата и календарной даты\\
Ссылки & \texttt{@ManyToOne}, поиск существующего объекта & внешние ключи; направленный \texttt{ON DELETE CASCADE}\\
Перечисления & \texttt{@Enumerated(STRING)} & \texttt{CHECK} допустимых имён\\
\bottomrule
\end{longtable}

Поле \texttt{screenwriter} оставлено необязательным: в исходном описании для него не указан запрет \texttt{null}. Пустые строки \texttt{tagline}, \texttt{passportID} и \texttt{Location.name} разрешены, поскольку для них задан только запрет \texttt{null}; пустой паспорт всё равно должен быть уникальным. Дополнительные ограничения, не указанные в варианте, не вводятся.

\texttt{birthday} сохраняет именованную временную зону, например \texttt{Europe/Moscow}; обычное поле PostgreSQL \texttt{timestamptz} сохраняло бы момент времени, но не исходное имя зоны. Поэтому использован конвертер в ISO-строку. Значения Java \texttt{Long} в JSON сериализуются десятичными строками: это сохраняет точность при отображении и повторном вводе в JavaScript.

\subsection{Семантика удаления}
Зависимость направлена от справочного объекта к использующему его объекту: удаление координат или человека удаляет связанные фильмы; удаление места удаляет связанных людей и затем их фильмы. Сервис явно выполняет этот порядок через JPA. Внешние ключи с \texttt{ON DELETE CASCADE} дублируют правило в БД. Удаление фильма сохраняет независимые координаты и людей, поскольку они могут использоваться другими фильмами. Рекурсивное уничтожение общей справочной записи при удалении одного фильма нарушило бы возможность повторного использования связей.

\subsection{Конкурентный доступ и синхронизация}
Перед изменением транзакция блокирует строку \texttt{AppState(1)} с \texttt{PESSIMISTIC\_WRITE}. Все изменения проходят через этот механизм; поэтому операции над группами фильмов выполняются последовательно и не теряют обновления. Ревизия коллекции увеличивается в той же транзакции. При ошибке откатываются как данные, так и ревизия.

Сущности содержат \texttt{@Version}. Форма передаёт прочитанную версию; устаревшее редактирование или удаление получает HTTP 409. Межзапросный общий кэш EclipseLink отключён. Каждые 2 секунды браузер читает \texttt{/api/revision} и при изменении загружает актуальную таблицу и открытое представление объекта. Несохранённый ввод не затирается: пользователь получает предупреждение, а версия повторно проверяется сервером. Результат специальной операции при внешнем изменении помечается устаревшим.

\section{Пользовательский интерфейс}
После входа пользователь получает доступ к общей коллекции. Меню содержит фильмы, людей, координаты, места и специальные операции. Для создания фильма сначала создаются необходимые справочные записи, затем они выбираются в форме по ID. Создание, просмотр, изменение и подтверждение удаления выполнены в отдельных диалогах.

В таблице фильмов каждой из 16 предметных характеристик соответствует отдельная колонка. Широкая таблица прокручивается горизонтально. Фильтрация названия, слогана и отображаемых имён участников выполняется по полному совпадению; дополнительно доступны жанр и MPAA. Выбор имени колонки проходит серверный разрешённый список, значения передаются параметрами JPQL. Пагинация фильмов выполняется через \texttt{setFirstResult}/\texttt{setMaxResults}; ID служит дополнительным ключом стабильной сортировки.

Используется HTTP-сессия с HttpOnly-cookie. Изменяющие запросы требуют CSRF-токен. Учебная учётная запись по умолчанию \texttt{student / student} заменяется переменными окружения. Все авторизованные сессии имеют одинаковый доступ, поскольку разграничение прав заданием не предусмотрено.

\begin{figure}[H]\centering
\includegraphics[width=\linewidth]{images/ui-table.png}
\caption{Главный экран во время браузерной проверки. Показана часть горизонтально прокручиваемой таблицы.}
\end{figure}
\begin{figure}[H]\centering
\includegraphics[width=\linewidth]{images/ui-details.png}
\caption{Отдельное окно просмотра фильма со связанными координатами и точным значением бюджета типа Long.}
\end{figure}
\begin{figure}[H]\centering
\includegraphics[width=0.83\linewidth]{images/ui-operations.png}
\caption{Отдельный интерфейс пяти специальных операций.}
\end{figure}

\section{Реализация специальных операций}
\subsection{Удаление, среднее и поиск по префиксу}
Для удаления выбираются фильмы с точным совпадением \texttt{usaBoxOffice}, после чего каждый удаляется через EntityManager в одной транзакции. Среднее вычисляется JPQL-запросом \texttt{AVG}; для пустой коллекции возвращается \texttt{null}, интерфейс показывает «нет данных».

Поиск по слогану использует \texttt{LIKE} с явным символом экранирования. Символы \texttt{\%}, \texttt{\_} и \texttt{!} во входной строке считаются буквальными. Пустой префикс соответствует всей коллекции. Специальный поиск по префиксу отделён от точной фильтрации главной таблицы.

\subsection{Перераспределение «Оскаров»}
В исходном тексте есть противоречие: перенос всех наград оставил бы исходные фильмы с нулевым \texttt{oscarsCount}, тогда как поле должно быть строго положительным. \textbf{Принято согласованное уточнение: каждый исходный фильм сохраняет одну награду; перераспределяются остальные.} Это явно отражено в интерфейсе и README.

Для исходного множества $A$ и целевого $B$, $n=|B|>0$:
\[
 S=\sum_{a\in A}(a.\mathrm{oscarsCount}-1),\qquad
 q=\left\lfloor\frac{S}{n}\right\rfloor,\qquad r=S\bmod n.
\]
Исходные фильмы получают значение 1. Целевые фильмы упорядочиваются по ID: первые $r$ получают дополнительно $q+1$, остальные $q$. Сумма наград сохраняется, а добавки различаются не более чем на 1. Равенство итоговых значений не требуется, так как фильмы могли иметь разные награды до операции.

Пример из теста: исходные значения $(5,4)$, целевые $(2,2)$. Переносится $S=7$, результат: $(1,1)$ и $(6,5)$. Общая сумма до и после равна 13. Одинаковые жанры и пустые группы отклоняются; при нулевом фонде допустима операция без изменения наград.

\subsection{Дополнительное награждение}
Выбираются фильмы с продолжительностью \emph{строго больше} заданного порога. Каждому добавляется положительное число наград. Для промежуточных расчётов используется \texttt{long}; перед записью проверяется верхняя граница \texttt{int}. Переполнение в любом фильме отменяет всю транзакцию, в том числе изменения ранее обработанных фильмов. Те же гарантии действуют для перераспределения.

\section{Проверка завершённости и результаты тестирования}
Проверка реализации выполнена \textbf{до написания данного отчёта}, 20 сентября 2026 года. Сначала были запущены интеграционные тесты на настоящем PostgreSQL, затем приложение развёрнуто в Payara и проверено через HTTP и два независимых браузерных контекста Chrome. H2, имитация ORM и ручная подмена ответов не использовались.

\subsection{Интеграционные тесты}
JUnit создаёт уникальную временную схему в отдельной базе \texttt{movie\_lab\_test}, применяет тот же DDL, что и приложение, и удаляет только эту схему после проверки. Используется EclipseLink 4.0.5. Итог: \textbf{32 теста, 0 ошибок, 0 неудач, 0 пропусков}; время набора 14,81 с, Maven \texttt{BUILD SUCCESS}.

\begin{longtable}{L{4.0cm}L{9.8cm}}
\toprule Группа проверок & Проверенное поведение\\\midrule\endhead
CRUD и поля & Генерация ID и даты; создание и изменение; сохранение даты; допустимые null; диапазон Long; несуществующие ссылки; запрет изменения служебных полей.\\
Валидация & Пустое имя, координата 827, положительные значения, паспорт, ISO-дата с зоной, NaN и выход за диапазон.\\
Чтение & Пагинация, сортировка, точный фильтр имени и слогана, сортировка по необязательной связи, защита выбора колонки.\\
Специальные операции & Пустое среднее; среднее 150; массовое удаление; буквальные \% и \_; сохранение суммы, остаток, пустые/одинаковые жанры; строгий порог продолжительности.\\
Транзакции & Полный откат при переполнении в обоих алгоритмах; 12 конкурентных награждений без потерь; ревизия только после commit.\\
Связи & Каскад координаты--фильм и место--человек--фильм; сохранение общих справочников при удалении фильма.\\
Независимая защита БД & Прямые SQL-попытки нарушить NOT NULL, CHECK, UNIQUE, положительность, enum, конечность числа и календарную дату отклоняются PostgreSQL.\\
\bottomrule
\end{longtable}

В первой проверке выявлена ошибка типизации параметра \texttt{null} в запросе проверки паспорта. Исправление: для создания и изменения используются корректные отдельные формы условия, а параметр ID передаётся только для изменения. Также добавлены явные LEFT JOIN для сортировки по необязательным участникам. Оба случая покрыты проверками; приведённый итог относится к исправленной сборке.

\subsection{Браузер и HTTP}
Автоматизированный сценарий \texttt{scripts/browser-test.cjs} выполнил \textbf{16 успешных проверок}. Проверены отказ неавторизованному запросу, неверный пароль, вход, CSRF, создание координат, информативная ошибка фильма, создание через форму и появление во второй сессии, точная передача Long, просмотр связей, обновление через API, конфликт устаревшей формы, синхронизация изменения, экран специальных операций, удаление и его синхронизация, отсутствие ошибок JavaScript.

Сценарий использовал бюджет \texttt{9223372036854775807}; после ввода через браузер API вернул ту же десятичную строку. При конфликте HTTP 409 несохранённая форма оставалась открытой. Тестовые фильм и координаты после успешного сценария удалены. Скриншоты в отчёте сняты с реально работающего приложения.

\subsection{Матрица соответствия заданию}
\begin{longtable}{L{5.0cm}L{8.8cm}}
\toprule Требование & Реализация и подтверждение\\\midrule\endhead
CRUD и отдельные окна & REST и диалоги; JUnit, браузерный сценарий.\\
Связанные объекты и повторное использование & Четыре раздела, выбор по ID, подробный просмотр, тест общих ссылок.\\
Серверная обработка и PostgreSQL & MovieService, JPA-транзакции, проверка реальной БД.\\
Таблица, страницы, точный фильтр, сортировка & 16 колонок, серверная выборка, интеграционные тесты.\\
Автообновление других клиентов & Ревизия после commit; две независимые сессии Chrome.\\
Каскадное удаление & Направленный каскад зависимостей; JPA-сервис и внешние ключи БД.\\
Ошибки ввода & Bean Validation, ограничения формы, структурированные HTTP-ошибки.\\
Пять специальных операций & Отдельный экран, серверные алгоритмы, тесты границ и откатов.\\
Java EE / managed beans / EclipseLink & Jakarta EE 10, CDI-компоненты, явный EclipseLink provider; успешное развёртывание WAR.\\
\bottomrule
\end{longtable}

\subsection{Границы выполненной проверки}
Кафедральный сервер \texttt{pg/studs} не проверялся: кафедральные реквизиты не предоставлялись. Предусмотрена конфигурация через переменные окружения. Docker Engine на машине был выключен; файл Compose приложен как альтернативный способ запуска, но его выполнение не заявляется. Проверен локальный стенд PostgreSQL + Payara. Единая блокировка записи, опрос раз в 2 секунды, общая учебная учётная запись и загрузка справочников целиком подходят для масштаба лабораторной работы; нагрузочная проверка промышленного масштаба не проводилась.

\section{Исходный код и воспроизведение}
Полный проект находится в каталоге \texttt{movie-lab}, архив поставки: \texttt{movie-lab-source.zip}. Приложение, SQL-схема и конфигурация приведены также в приложении к отчёту; тесты и скрипты воспроизведения включены в исходный архив. Удалённый репозиторий не создавался, поэтому фиктивная ссылка не приводится.

\begin{enumerate}
\item Установить JDK 17+, Maven 3.9+ и PostgreSQL 17.
\item В каталоге проекта выполнить \texttt{./scripts/start-local.ps1}. Скрипт создаёт собственную БД, выполняет \texttt{mvn verify} и запускает Payara.
\item Открыть \url{http://localhost:18081/movie-lab/}, войти с учебной учётной записью; сначала создать координаты, затем фильм.
\item Для кафедрального сервера применить схему отдельно и задать \texttt{MOVIE\_DB\_URL}, \texttt{MOVIE\_DB\_USER}, \texttt{MOVIE\_DB\_PASSWORD}. URL: \texttt{jdbc:postgresql://pg:5432/studs?currentSchema=movie\_lab}.
\end{enumerate}

Протоколы проверки: \texttt{verification/tests.log}, XML JUnit, \texttt{verification/browser-results.json}, журнал браузерного сценария и снимки интерфейса. Для повторной компиляции отчёта: два запуска \texttt{xelatex report.tex} либо один запуск \texttt{tectonic report.tex}; относительные пути к исходному проекту должны сохраняться.

\section{Выводы}
Разработана работоспособная информационная система варианта 4101 с управлением фильмами и связанными объектами, PostgreSQL-хранилищем, EclipseLink, управляемыми CDI-компонентами и русским веб-интерфейсом. Реализованы пять специальных операций, защита от потери конкурентных изменений и автоматическое обновление независимых клиентских сессий.

Проверка до оформления отчёта обнаружила и позволила исправить ошибку параметризации запроса. Итоговая сборка прошла 32 интеграционных теста и 16 проверок браузера/API. Практически отработаны отображение объектов на реляционную схему, согласование ограничений ORM и БД, транзакционная обработка групповых операций и воспроизводимая проверка многопользовательского поведения.

Противоречие в операции перераспределения разрешено явным согласованным правилом сохранения одной награды у каждого исходного фильма; оно не скрывается за ослаблением ограничений БД. Для учебного объёма система готова к демонстрации и защите на проверенном локальном стенде.

\begin{thebibliography}{9}
\bibitem{jpa} Eclipse Foundation. Jakarta Persistence 3.1. \url{https://jakarta.ee/specifications/persistence/3.1/}.
\bibitem{eclipselink} Eclipse Foundation. Understanding EclipseLink 4.0. \url{https://eclipse.dev/eclipselink/documentation/4.0/concepts/concepts.html}.
\bibitem{payara} Payara. Customizing Payara Micro with Command-Line Options. \url{https://payara.fish/blog/customizing-payara-micro-with-command-line-options/}.
\end{thebibliography}
''')
(report/'images').mkdir(exist_ok=True)
for name in ['ui-table.png','ui-details.png','ui-operations.png']:shutil.copy2(base/'verification'/name,report/'images'/name)
sources=[('Сущности и типы предметной области',list(sorted((base/'movie-lab/src/main/java/ru/itmo/movie/domain').glob('*.java')))),('Хранение и бизнес-логика',list(sorted((base/'movie-lab/src/main/java/ru/itmo/movie/persistence').glob('*.java')))+list(sorted((base/'movie-lab/src/main/java/ru/itmo/movie/service').glob('*.java')))),('Серверный HTTP-интерфейс',list(sorted((base/'movie-lab/src/main/java/ru/itmo/movie/web').glob('*.java')))),('SQL и конфигурация',[base/'movie-lab/database/schema.sql',base/'movie-lab/pom.xml',base/'movie-lab/src/main/resources/META-INF/persistence.xml',base/'movie-lab/src/main/webapp/WEB-INF/beans.xml',base/'movie-lab/src/main/webapp/WEB-INF/web.xml']),('Клиентский интерфейс',[base/'movie-lab/src/main/webapp/index.html',base/'movie-lab/src/main/webapp/app.js',base/'movie-lab/src/main/webapp/style.css'])]
out=[r'\section{Исходный код приложения}',r'Листинги ниже включены непосредственно из проверенных исходных файлов. Полный проект с тестами и средствами запуска также поставляется отдельным архивом.',r'\begingroup\singlespacing']
for heading,files in sources:
 out.append(r'\subsection{'+heading+'}')
 for file in files:
  rel=file.relative_to(base).as_posix()
  out.extend([r'\Needspace{5\baselineskip}',r'\subsubsection*{'+esc(file.name)+'}',r'\noindent\path{'+rel+'}',r'\VerbatimInput{../'+rel+'}'])
out.append(r'\endgroup')
put('source-code.tex','\n'.join(out))
shutil.copy2(base/'movie-lab/target/surefire-reports/TEST-ru.itmo.movie.MovieServiceTest.xml',base/'verification/junit-results.xml')
shutil.copy2(base/'movie-lab/target/surefire-reports/ru.itmo.movie.MovieServiceTest.txt',base/'verification/junit-summary.txt')
print('Report sources generated AFTER passing 32 integration tests and 16 browser checks.')
