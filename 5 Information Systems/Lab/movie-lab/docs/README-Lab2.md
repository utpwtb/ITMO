# Лабораторная работа № 2 — управление фильмами

Развитие приложения ЛР1: JSON-импорт, история USER/ADMIN и уникальность `(точное название, Person.id режиссёра либо null)` только в бизнес-логике. Прежние CRUD, каскадные удаления, версии, синхронизация и пять специальных операций сохранены. Итоговый интерфейс только на русском; номер варианта из шапки и заголовка браузера убран по указанию пользователя.

## Исходники и документы

- `src/main/java/ru/itmo/movie/{domain,persistence,service,web}` — Jakarta EE 10, CDI, EclipseLink, RESOURCE_LOCAL, Java 17 target.
- `database/schema.sql` — новая БД; `database/migrations/003_lab2_roles_imports.sql` — повторяемое обновление ЛР1 без потери данных.
- `docs/import-format.md`, `src/main/webapp/examples/import-valid.json`, `src/test/resources/import/` — контракт и примеры.
- `jmeter/README.md`, `jmeter/lab2-concurrency.jmx` — серверные конкурентные сценарии.
- `../verification/Lab2/ACCEPTANCE.md`, `isolation-analysis.md` — реальные результаты и ограничения.
- `../report/Lab2/` — русский отчёт, PDF, редактируемые UML DOT и изображения.
- `docs/lab1-readme-historical.md` — сохранённый прежний README; его результаты относятся к ЛР1.

## Helios: построение и запуск

Проверенная среда: FreeBSD 14.5, OpenJDK 21.0.4, Maven 3.8.4, PostgreSQL 18.3, Python 3.11.9, Payara Micro 6.2025.1, JMeter 5.6.3. Проект: `/home/studs/s407960/is-lab2-4101`, HTTP только `127.0.0.1:40797`, база `pg:5432/studs`, schema `s407960`. Продуктивные таблицы: `lab2_4101_`; тестовые: `lab2_4101_test_`. Ресурсы `lab1_4101_` не затрагиваются.

`scripts/helios.py` читает пароль БД из существующего `~/.pgpass` с правами 0600; секреты не передаются аргументами. Java использует ограниченный heap: стандартный запуск java/mvn на Helios пытается выделить недопустимо большой объём памяти.

```sh
cd ~/is-lab2-4101
# test: только при остановленном кандидате и свободных тестовых таблицах
python3.11 scripts/helios.py test
# Новая продуктивная установка; отказывает при существующих таблицах
python3.11 scripts/helios.py init
# Обновление существующей БД с сохранением строк
python3.11 scripts/helios.py migrate
python3.11 scripts/helios.py start
python3.11 scripts/helios.py status
python3.11 scripts/helios.py stop
```

`test` выполняет Maven clean verify на настоящем PostgreSQL и после завершения удаляет только созданные тестовые таблицы. Для Web/JMeter используются `init-test` и `start-test`; интеграционные тесты и кандидат не работают одновременно на этих таблицах. Частный backup/restore описан в `jmeter/README.md`.

WAR: `target/movie-lab.war`; runtime: `.runtime/`; PID: `.runtime/payara.pid`; журнал: `.runtime/payara.log`. Остановка проверяет, что PID соответствует этому Java-процессу. Перед повторным запуском дождаться завершения процесса. Recovery RUNNING рассчитан на один экземпляр: после завершения предыдущего процесса скрипт ждёт AppState lock и помечает прерванные операции FAILED. Recovery при нескольких активных экземплярах не заявляется.

Чтобы назначить ADMIN, сначала зарегистрировать обычный аккаунт, затем выполнить на сервере:

```sh
MOVIE_ADMIN_USER=exact_registered_name python3.11 scripts/helios.py admin
# Для тестового кандидата
MOVIE_TARGET=test MOVIE_ADMIN_USER=exact_registered_name python3.11 scripts/helios.py admin
```

Регистрация отвергает параметр role. Роль читается из доверенной записи БД, а не из запроса. Назначение роли не меняет пароль.

## SSH-туннель

```powershell
ssh -N -L 18083:127.0.0.1:40797 -o ExitOnForwardFailure=yes -p 2222 s407960@helios.cs.ifmo.ru
```

Открыть `http://127.0.0.1:18083/movie-lab/`. Для независимых Cookie-контекстов использовать отдельный профиль либо `localhost:18083`. Эти URL обращаются к Helios, а не к локальному приложению.

`scripts/lab2-remote.py` — локальный Windows-транспорт Paramiko с обязательным существующим known_hosts. Зашифрованный PSCredential читается из `C:/Users/CHL/AppData/Local/MovieLab/credentials/helios-s407960-lab2.clixml` в памяти и передаётся только SSH-аутентификации. Использовать обычный Python, например встроенный Python Codex; Microsoft Store Python может не видеть файл из-за перенаправления AppData. `.runtime`, credential-файл и пароли в архив/отчёт не входят.

```powershell
python scripts/lab2-remote.py exec 'cd ~/is-lab2-4101; python3.11 scripts/helios.py status'
python scripts/lab2-remote.py tunnel 18083 40797
python scripts/pack-lab2.py ../verification/Lab2/source-final.tar.gz
```

После SFTP-распаковки проверить source-manifest.json, построить WAR на сервере и записать `sha256 target/movie-lab.war`. Продуктивное развёртывание использует тот же WAR, который прошёл проверку.

## Импорт и транзакции

`POST api/imports`: multipart file, application/json, Session Cookie и X-CSRF-Token. `GET api/imports?page=0&size=10` и `GET api/imports/{id}` фильтруют владельца на сервере; ADMIN видит всё. До разбора принятого файла сохраняется RUNNING; данные и SUCCESS коммитятся вместе; FAILED сохраняется отдельно после отката. История не увеличивает movie revision.

Long принимается точно из целого JSON или десятичной строки. Person определяется паспортом; несовпадение полных данных запрещено. Название не обрезается и не нормализуется; два одинаковых названия с null-режиссёром конфликтуют. Новый ключ не реализован через ограничения или триггеры PostgreSQL.

`MOVIE_ISOLATION` по умолчанию READ COMMITTED, AppState row lock и клиентская версия защищают записи. `MOVIE_LOCK_TIMEOUT_MS=10000` задаётся через SET LOCAL lock_timeout. Для сравнения доступен SERIALIZABLE с тремя повторами подтверждённого SQLSTATE 40001. Неопределённый commit не повторяется вслепую: требуется проверить operationId в истории.

## Локальная разработка

Она не заменяет серверную приёмку. Windows, Java 17+, Maven, PostgreSQL 17: `./scripts/start-local.ps1`. Собственный кластер `.runtime/pgdata`, базы `movie_lab`/`movie_lab_test`, PostgreSQL loopback 55441, HTTP 18081. Скрипт применяет все миграции; не направлять его на чужой кластер.

Исходная учебная учётная запись student/student сохранена. MOVIE_USER/MOVIE_PASSWORD задают только первоначальный bootstrap и не сбрасывают существующий пароль. Новые пользователи регистрируются в Web. Пароли PBKDF2-HMAC-SHA256, 600000 итераций со случайной солью; Cookie HttpOnly, CSRF для изменений.

## Отчёт

Открыть `../report/Lab2` в редакторе LaTeX или выполнить XeLaTeX/LuaLaTeX над main.tex. Шрифты включены в fonts/. Автономная сборка проверена Tectonic: `tectonic --keep-logs --keep-intermediates main.tex`. UML обновляются командой `python scripts/lab2-uml.py` при установленном Graphviz. Финальный PDF проверяется визуально после компиляции.
