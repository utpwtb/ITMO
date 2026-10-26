"""Build the self-contained, offline Chinese/Russian defense study guide."""
from pathlib import Path
import html
import json
import re

HERE = Path(__file__).resolve().parent
OUT = HERE.parent / '信息系统答辩_中俄双语.html'

def P(zh, ru):
    return {'zh': zh, 'ru': ru}

def esc(s):
    return html.escape(str(s), quote=True)

def rich(s):
    return re.sub(r'`([^`]+)`', lambda m: '<code>' + m.group(1) + '</code>', esc(s)).replace('\n', '<br>')

def pair(p, tag='div', cls='', inner='div'):
    return f'<{tag} class="pair {cls}"><{inner} class="lang lang-zh" lang="zh-CN">{rich(p["zh"])}</{inner}><{inner} class="lang lang-ru" lang="ru">{rich(p["ru"])}</{inner}></{tag}>'

def inline(p):
    return f'<span class="lang lang-zh" lang="zh-CN">{rich(p["zh"])}</span> <span class="lang lang-ru" lang="ru">{rich(p["ru"])}</span>'

def heading(p, tag='h2'):
    return f'<{tag}>{inline(p)}</{tag}>'

def table(t):
    heads = ''.join('<th scope="col">' + pair(p) + '</th>' for p in t['headers'])
    rows = []
    for row in t['rows']:
        cells = ''.join('<td><div class="cell-label">' + inline(t['headers'][i]) + '</div>' + pair(p) + '</td>' for i, p in enumerate(row))
        rows.append('<tr>' + cells + '</tr>')
    return '<div class="table-wrap"><table><thead><tr>' + heads + '</tr></thead><tbody>' + ''.join(rows) + '</tbody></table></div>'

def block(b):
    out = '<div class="content-block">' + pair(b['title'], 'h3', inner='span')
    out += ''.join(pair(p) for p in b.get('paragraphs', []))
    if b.get('bullets'):
        out += '<ul class="paired-list">' + ''.join('<li>' + pair(p) + '</li>' for p in b['bullets']) + '</ul>'
    if b.get('table'):
        out += table(b['table'])
    if b.get('code'):
        c = b['code']
        out += '<div class="code-box"><div class="code-top"><span>' + esc(c.get('language', 'text').upper()) + '</span><button type="button" class="copy-btn">' + inline(P('复制', 'Копировать')) + '</button></div><pre><code>' + esc(c['text']) + '</code></pre>' + pair(c['caption'], cls='code-caption') + '</div>'
    if b.get('callout'):
        out += pair(b['callout'], cls='callout')
    return out + '</div>'

def sources(items):
    return '<div class="sources">' + heading(P('官方资料与规范', 'Официальные материалы и спецификации'), 'h3') + '<ul>' + ''.join('<li><a href="' + esc(x['url']) + '" target="_blank" rel="noopener noreferrer">' + inline(x['label']) + '</a></li>' for x in items) + '</ul></div>'

def section(s):
    out = '<section class="chapter" id="' + s['id'] + '" data-search-unit aria-labelledby="heading-' + s['id'] + '"><header class="chapter-head"><div class="chapter-kicker"><span class="chapter-number">' + s['number'] + ' / 09</span><button type="button" class="learn-button" aria-pressed="false">' + inline(P('○ 标记掌握', '○ Отметить')) + '</button></div>'
    out += '<h2 id="heading-' + s['id'] + '">' + inline(s['title']) + '</h2>' + pair(s['summary'], cls='chapter-summary') + '</header><div class="chapter-body"><div class="full-only">'
    out += ''.join(block(b) for b in s['blocks']) + '</div><div class="oral">' + heading(P('答辩开场：先完整说一遍', 'Начало ответа: произнесите связный текст'), 'h3') + pair(s['oral']) + '</div>'
    out += heading(P('老师可能继续追问', 'Возможные дополнительные вопросы'), 'h3').replace('<h3>', '<h3 class="questions-title">')
    for qa in s['questions']:
        out += '<details class="question"><summary>' + pair(qa['q'],tag='span',inner='span') + '</summary><div class="question-answer">' + pair(qa['a']) + '</div></details>'
    out += '<div class="full-only">' + sources(s['sources']) + '</div></div></section>'
    return out

overview_rows = [
    [P('设计模式', 'Паттерны проектирования'), P('对象协作层', 'Уровень взаимодействия объектов'), P('怎样组织类与对象的职责？', 'Как распределить обязанности классов и объектов?'), P('Strategy、Factory、Adapter、Proxy', 'Strategy, Factory, Adapter, Proxy')],
    [P('架构模式', 'Архитектурные паттерны'), P('系统结构层', 'Уровень структуры системы'), P('系统怎样分层、通信、部署？', 'Как разделить систему, организовать связи и развёртывание?'), P('分层、MVC、六边形架构', 'Слои, MVC, гексагональная архитектура')],
    [P('Jakarta EE', 'Jakarta EE'), P('平台规范集合', 'Набор спецификаций платформы'), P('企业应用有哪些统一契约？', 'Какие общие контракты нужны корпоративному приложению?'), P('CDI、REST、Persistence、Transactions', 'CDI, REST, Persistence, Transactions')],
    [P('CDI / Spring IoC', 'CDI / Spring IoC'), P('对象管理与依赖注入', 'Управление объектами и внедрение зависимостей'), P('谁创建对象、装配依赖、管理生命周期？', 'Кто создаёт объекты, связывает зависимости и управляет жизненным циклом?'), P('容器管理服务与资源', 'Контейнер управляет сервисами и ресурсами')],
    [P('Jakarta Persistence', 'Jakarta Persistence'), P('持久化规范与 API', 'Спецификация и API персистентности'), P('实体怎样映射和同步到关系数据库？', 'Как отображать сущности на реляционную БД и синхронизировать их?'), P('EntityManager、Entity、JPQL', 'EntityManager, Entity, JPQL')],
    [P('Hibernate / EclipseLink', 'Hibernate / EclipseLink'), P('ORM 实现', 'Реализации ORM'), P('谁执行映射、脏检查并生成 SQL？', 'Кто выполняет отображение, dirty checking и генерацию SQL?'), P('Persistence Provider', 'Провайдер Persistence')],
    [P('Jakarta Data / Spring Data', 'Jakarta Data / Spring Data'), P('Repository 抽象', 'Абстракция репозиториев'), P('怎样减少数据访问样板代码？', 'Как сократить шаблонный код доступа к данным?'), P('声明式查询接口；具体存储取决于实现或模块', 'Декларативные интерфейсы запросов; хранилище зависит от реализации или модуля')],
    [P('Spring Framework', 'Spring Framework'), P('应用框架', 'Прикладной фреймворк'), P('怎样整合 DI、Web、事务等编程能力？', 'Как объединить DI, Web, транзакции и другие возможности?'), P('ApplicationContext、MVC、AOP', 'ApplicationContext, MVC, AOP')],
    [P('Spring Boot', 'Spring Boot'), P('配置、启动与运行整合', 'Настройка, запуск и эксплуатационная интеграция'), P('怎样快速组装并运行 Spring 应用？', 'Как быстро собрать и запустить приложение Spring?'), P('自动配置、starter、可执行包、Actuator', 'Автоконфигурация, starter, исполняемый архив, Actuator')],
]

def stack_node(name, p):
    return '<div class="stack-node"><strong>' + esc(name) + '</strong>' + pair(p) + '</div>'

def make_map():
    title = P('先建立全局关系，再逐题学习', 'Сначала общая картина, затем отдельные темы')
    out = '<section class="appendix" id="map" data-search-unit>' + heading(title)
    out += pair(P('这些技术处于不同层级。先问“它解决哪一类问题”，再问“它依赖谁、可以替换谁”。下面两条链展示常见的关系数据库应用组合，不表示所有应用都必须采用这套结构。', 'Эти технологии находятся на разных уровнях. Сначала спросите, какую задачу решает технология, затем — от чего она зависит и чем её можно заменить. Две цепочки показывают типичные сочетания для реляционной БД; такая структура не обязательна для каждого приложения.'), cls='section-intro')
    out += '<div class="map-grid"><div class="stack">' + heading(P('Jakarta 组合', 'Сочетание Jakarta'), 'h3')
    out += stack_node('Jakarta EE runtime + CDI', P('容器创建服务并注入依赖', 'Контейнер создаёт сервисы и внедряет зависимости'))
    out += '<div class="stack-arrow" aria-hidden="true">↓</div>' + stack_node('Jakarta Data [optional]', P('可选：由 Data 提供者实现 Repository；Jakarta EE 11 引入', 'Необязательно: провайдер Data реализует репозитории; введено в Jakarta EE 11'))
    out += '<div class="stack-arrow" aria-hidden="true">↓</div>' + stack_node('Jakarta Persistence → EclipseLink / Hibernate', P('关系存储的一种路径；Data 的其他提供者可采用其他映射方案', 'Один из путей для реляционного хранилища; другие провайдеры Data могут использовать иное отображение'))
    out += '<div class="stack-arrow" aria-hidden="true">↓</div>' + stack_node('JDBC → SQL → PostgreSQL', P('JDBC 驱动传递数据库操作', 'Драйвер JDBC передаёт операции базе данных')) + '</div><div class="stack">' + heading(P('Spring 组合', 'Сочетание Spring'), 'h3')
    out += stack_node('Spring Boot → Spring Framework', P('Boot 整合配置与启动；Framework 提供容器等核心能力', 'Boot объединяет настройку и запуск; Framework предоставляет контейнер и другие базовые возможности'))
    out += '<div class="stack-arrow" aria-hidden="true">↓</div>' + stack_node('Spring Data JPA [optional]', P('可选：Repository 代理委托给 JPA', 'Необязательно: прокси репозитория делегирует работу JPA'))
    out += '<div class="stack-arrow" aria-hidden="true">↓</div>' + stack_node('Jakarta Persistence → Hibernate / EclipseLink', P('JPA 模块仍需要 ORM 提供者', 'Модулю JPA по-прежнему нужен ORM-провайдер'))
    out += '<div class="stack-arrow" aria-hidden="true">↓</div>' + stack_node('JDBC → SQL → PostgreSQL', P('最终仍使用数据库能力与约束', 'В конечном счёте используются возможности и ограничения БД')) + '</div></div>'
    out += pair(P('关系图中的箭头表示典型的组合或委托，不表示两个技术属于同一层，也不保证 Jakarta Data 与 JPA 共享同一个持久化上下文。Spring Data JDBC、MongoDB、R2DBC 等模块也不沿用上面的 JPA 路径。', 'Стрелки означают типичную композицию или делегирование, а не одинаковый уровень технологий и не гарантию общего persistence context у Jakarta Data и JPA. Модули Spring Data JDBC, MongoDB и R2DBC также не следуют показанному пути JPA.'), cls='callout')
    out += table({'headers':[P('技术', 'Технология'),P('所属层级', 'Уровень'),P('核心问题', 'Главный вопрос'),P('识别关键词', 'Ключевые слова')], 'rows':overview_rows})
    out += block({'title':P('版本坐标：以实验为基准', 'Версии: ориентир — ваша лабораторная'), 'paragraphs':[
        P('实验的 pom.xml 声明 Java 17、Jakarta EE API 10.0.0（provided）和 EclipseLink 4.0.5。EE 10 的 Persistence 规范版本为 3.1；实验 persistence.xml 使用 3.0 的 XML 描述格式。这些是不同维度：XML 的 version 不能单独证明运行时 API 或提供者版本。', 'В pom.xml лабораторной указаны Java 17, Jakarta EE API 10.0.0 (provided) и EclipseLink 4.0.5. EE 10 включает Persistence 3.1; persistence.xml использует формат XML-дескриптора 3.0. Это разные измерения: атрибут version в XML сам по себе не определяет версию API или провайдера во время выполнения.'),
        P('Jakarta Data 1.0 属于 Jakarta EE 11，不能因为项目引用 EE 10 API 就认为已经支持 Data。Spring 章节以 Framework 6 / Boot 3 的 Jakarta 编程模型作为教学基线，不把它们称作最新版本。本文核对日期：2026-10-26；升级时应重新核对 Java、容器、API 和实现的兼容矩阵。', 'Jakarta Data 1.0 входит в Jakarta EE 11: зависимость от EE 10 API ещё не означает поддержку Data. В разделах Spring учебной основой служит модель Jakarta из Framework 6 / Boot 3; эти версии не называются последними. Дата проверки: 26.10.2026. При обновлении нужно заново проверить совместимость Java, контейнера, API и реализации.')
    ]})
    out += sources([{'label':P('Jakarta EE 10 平台与版本', 'Jakarta EE 10: платформа и версии'),'url':'https://jakarta.ee/specifications/platform/10/'},{'label':P('Jakarta Data 1.0 规范', 'Спецификация Jakarta Data 1.0'),'url':'https://jakarta.ee/specifications/data/1.0/'}])
    return out + '</section>'

lab_blocks = [
    {'title':P('用代码证明：实验采用什么技术栈？', 'Подтверждение кодом: какой стек использует лабораторная?'), 'table':{'headers':[P('证据位置', 'Где смотреть'),P('实际内容', 'Что в коде'),P('答辩应怎样解释', 'Как объяснить на защите')], 'rows':[
        [P('movie-lab/pom.xml', 'movie-lab/pom.xml'),P('jakarta.jakartaee-api:10.0.0；scope=provided；EclipseLink 4.0.5；PostgreSQL 驱动', 'jakarta.jakartaee-api:10.0.0; scope=provided; EclipseLink 4.0.5; драйвер PostgreSQL'),P('API 依赖提供编译契约；provided 表示部署环境预期提供该 API/平台运行支持，单独的 API jar 不会启动容器。', 'Зависимость API задаёт контракт компиляции; provided означает ожидание поддержки API/платформы от среды развёртывания. Сам JAR с API не запускает контейнер.')],
        [P('MovieResource.java', 'MovieResource.java'),P('@Path、@GET/@POST、@RequestScoped、@Inject', '@Path, @GET/@POST, @RequestScoped, @Inject'),P('REST 资源接收 HTTP 请求；CDI 注入 MovieService；资源使用请求作用域。', 'REST-ресурс принимает HTTP-запросы; CDI внедряет MovieService; ресурс имеет область запроса.')],
        [P('MovieService.java / Database.java', 'MovieService.java / Database.java'),P('@ApplicationScoped；@Inject Database；Persistence.createEntityManagerFactory', '@ApplicationScoped; @Inject Database; Persistence.createEntityManagerFactory'),P('业务和持久化协调对象由 CDI 管理；EntityManagerFactory 通过程序式 API 创建。', 'Объектами бизнес-логики и координации хранения управляет CDI; EntityManagerFactory создаётся программно.')],
        [P('persistence.xml', 'persistence.xml'),P('org.eclipse.persistence.jpa.PersistenceProvider；RESOURCE_LOCAL', 'org.eclipse.persistence.jpa.PersistenceProvider; RESOURCE_LOCAL'),P('选择 EclipseLink 提供者；应用通过 EntityTransaction 控制资源本地事务。', 'Выбран провайдер EclipseLink; приложение управляет локальной транзакцией через EntityTransaction.')],
        [P('Movie.java', 'Movie.java'),P('@Entity、@Id、@GeneratedValue、@ManyToOne、@Version', '@Entity, @Id, @GeneratedValue, @ManyToOne, @Version'),P('实体映射、主键生成、关联和版本冲突检测属于 Persistence 的职责。', 'Отображение сущности, генерация ключа, связи и контроль версий относятся к Persistence.')],
        [P('WEB-INF/beans.xml', 'WEB-INF/beans.xml'),P('version=4.0；bean-discovery-mode=annotated', 'version=4.0; bean-discovery-mode=annotated'),P('CDI 采用 annotated 发现模式；不能把包里的每一个普通类都自动视为 CDI Bean。', 'CDI использует режим обнаружения annotated; нельзя автоматически считать каждый обычный класс в пакете CDI-бином.')],
    ]}},
    {'title':P('跟踪一次修改电影的请求', 'Проследим запрос изменения фильма'), 'bullets':[
        P('HTTP PUT 进入 MovieResource.update，读取路径、ID 和 JSON 输入，调用 service.save。入口负责协议适配，业务规则在 Service 中处理。', 'HTTP PUT попадает в MovieResource.update, где читаются путь, ID и JSON, затем вызывается service.save. Входной слой адаптирует протокол, а Service обрабатывает бизнес-правила.'),
        P('MovieService 调用 db.write。Database 创建本次操作专用的 EntityManager，并调用 EntityTransaction.begin。ApplicationScoped 的 Database 不把同一个 EntityManager 共享给所有请求。', 'MovieService вызывает db.write. Database создаёт отдельный EntityManager для операции и вызывает EntityTransaction.begin. Database с областью ApplicationScoped не раздаёт один EntityManager всем запросам.'),
        P('事务首先以 PESSIMISTIC_WRITE 锁定 ID=1 的 AppState 行。按这条写入路径执行的操作被同一行锁串行化：实现简单、便于维护全局修订号，但它限制并发写吞吐量。', 'Транзакция сначала блокирует строку AppState с ID=1 через PESSIMISTIC_WRITE. Операции этого пути записи сериализуются одной блокировкой: это упрощает общий номер ревизии, но ограничивает пропускную способность параллельной записи.'),
        P('Service 读取 Movie，校验浏览器提交的旧版本与数据库当前版本，再验证输入并修改受管实体。这一显式检查识别用户长时间编辑造成的旧表单；@Version 则补充检测持久化读写之间的并发冲突。', 'Service читает Movie, сравнивает версию старой формы с текущей версией БД, проверяет входные данные и изменяет managed-сущность. Явная проверка выявляет устаревшую форму после долгого редактирования; @Version дополнительно обнаруживает конкурентные изменения между чтением и записью при персистентности.'),
        P('EclipseLink 根据实体状态生成 SQL。Database 更新 AppState.revision，执行 flush，再 commit；发生 RuntimeException 时回滚活动事务。flush 可能提前暴露约束错误，但此时事务还没有提交。', 'EclipseLink формирует SQL по состоянию сущностей. Database обновляет AppState.revision, выполняет flush, затем commit; при RuntimeException активная транзакция откатывается. flush может раньше выявить нарушение ограничений, но ещё не фиксирует транзакцию.'),
        P('try-with-resources 关闭 EntityManager。返回的实体不应再被假定处于可用的原持久化上下文中；若需要未加载的关联，宜在上下文内明确加载或转换成 DTO。', 'try-with-resources закрывает EntityManager. Возвращённую сущность уже нельзя считать находящейся в доступном исходном persistence context; нужные незагруженные связи следует явно загрузить или преобразовать в DTO до закрытия контекста.')
    ]},
    {'title':P('配置的后果：缓存、关联与事务', 'Следствия настроек: кэш, связи и транзакции'), 'paragraphs':[
        P('eclipselink.cache.shared.default=false 关闭默认共享实体缓存（二级缓存），不等于取消当前 EntityManager 的一级缓存或持久化上下文。eclipselink.weaving=false 禁用织入；某些延迟加载与变更追踪优化会受影响，应查看实际 SQL 与提供者行为。', 'eclipselink.cache.shared.default=false выключает общий кэш сущностей по умолчанию (второй уровень), но не отменяет кэш первого уровня или persistence context текущего EntityManager. eclipselink.weaving=false отключает weaving; это влияет на некоторые способы ленивой загрузки и оптимизации отслеживания изменений. Нужно смотреть реальный SQL и поведение провайдера.'),
        P('Movie 的 @ManyToOne 没有显式 fetch 参数，按 JPA 默认是 EAGER。这不保证一条 JOIN SQL 完成，也不能据此说实验实现了 LAZY。page 方法的 LEFT JOIN 主要用于筛选和排序；普通 JOIN 与 JOIN FETCH 的语义不同。', 'У @ManyToOne в Movie не указан fetch, поэтому по умолчанию JPA это EAGER. Это не гарантирует один SQL с JOIN и не позволяет утверждать, что в лабораторной используется LAZY. LEFT JOIN в методе page в основном нужен для фильтрации и сортировки; обычный JOIN и JOIN FETCH имеют разную семантику.'),
        P('不要说“部署到 Jakarta EE 容器，所以事务一定由 JTA 管理”。本项目实际是 RESOURCE_LOCAL + EntityTransaction。换成容器管理的 JTA，需要配套调整持久化单元、数据源、EntityManager 获取方式与事务边界。', 'Не говорите: «развёрнуто в контейнере Jakarta EE, значит транзакциями обязательно управляет JTA». Здесь реально используются RESOURCE_LOCAL и EntityTransaction. Переход к JTA контейнера требует согласованно изменить persistence unit, источник данных, получение EntityManager и границы транзакций.')
    ], 'callout':P('准确表述：我的实验使用 Jakarta EE 的 REST、CDI 和 Persistence API，ORM 提供者为 EclipseLink；当前数据访问通过 EntityManager 手写，没有使用 Spring、Spring Boot、Spring Data 或 Jakarta Data。', 'Точная формулировка: в моей лабораторной используются REST, CDI и Persistence API из Jakarta EE, ORM-провайдер — EclipseLink. Доступ к данным написан через EntityManager; Spring, Spring Boot, Spring Data и Jakarta Data не используются.')},
    {'title':P('怎样把实验迁移到 Spring，而不混淆概念？', 'Как перенести лабораторную на Spring и сохранить точность понятий?'), 'paragraphs':[
        P('Movie 的标准 JPA 映射通常可以继续使用。REST 入口可改为 Spring MVC 控制器；CDI 的服务装配改由 Spring 容器管理；数据源、EntityManagerFactory 和事务管理交给相应 Spring 配置或 Boot 自动配置。', 'Стандартное JPA-отображение Movie обычно можно сохранить. REST-вход можно заменить контроллером Spring MVC; сборкой сервисов вместо CDI займётся контейнер Spring; DataSource, EntityManagerFactory и управление транзакциями настраиваются через Spring или автоконфигурацию Boot.'),
        P('若再引入 Spring Data JPA，可把常规 CRUD 和查询提取到 Repository，但多步骤业务事务仍应在 Service 边界统一设计。更换框架不会自动保留旧的锁策略、异常到 HTTP 状态的映射、校验流程和缓存设置，迁移需要逐项核对这些行为。', 'При добавлении Spring Data JPA обычные CRUD и запросы можно вынести в Repository, но границы многошаговых бизнес-транзакций по-прежнему следует проектировать в Service. Смена фреймворка автоматически не сохраняет стратегию блокировок, отображение ошибок в HTTP-статусы, проверки и настройки кэша; эти свойства нужно сверять отдельно.')
    ]}
]

def make_lab():
    out = '<section class="appendix" id="lab" data-search-unit>' + heading(P('把理论落到你的 Movie 实验', 'Связь теории с вашей лабораторной Movie'))
    out += pair(P('以下结论来自当前工作区源码核对，描述的是本地代码与配置，不把它当作远程运行环境的实时检测。证据路径均相对于 Lab1/movie-lab。', 'Выводы ниже основаны на исходниках текущего рабочего каталога и описывают локальный код и настройки. Это не проверка удалённой среды в реальном времени. Пути указаны относительно Lab1/movie-lab.'),cls='section-intro')
    out += ''.join(block(b) for b in lab_blocks)
    out += '<div class="sources">' + pair(P('本地核对文件：pom.xml；src/main/resources/META-INF/persistence.xml；src/main/webapp/WEB-INF/beans.xml；src/main/java/ru/itmo/movie 下的 MovieResource、MovieService、Database、Movie。核对日期：2026-10-26。', 'Проверенные локальные файлы: pom.xml; src/main/resources/META-INF/persistence.xml; src/main/webapp/WEB-INF/beans.xml; классы MovieResource, MovieService, Database и Movie в src/main/java/ru/itmo/movie. Дата проверки: 26.10.2026.')) + '</div></section>'
    return out

terms = [
    ('specification',P('规范：规定可依赖的契约与行为', 'Спецификация: определяет контракт и поведение')),
    ('implementation / provider',P('实现 / 提供者：实际履行规范的代码', 'Реализация / провайдер: код, выполняющий спецификацию')),
    ('container',P('容器：管理组件及其运行服务', 'Контейнер: управляет компонентами и сервисами выполнения')),
    ('managed bean',P('受管 Bean：由相应容器管理的对象', 'Управляемый бин: объект под управлением соответствующего контейнера')),
    ('IoC / DI',P('控制反转 / 依赖注入', 'Инверсия управления / внедрение зависимостей')),
    ('scope / lifecycle',P('作用域 / 生命周期', 'Область видимости / жизненный цикл')),
    ('qualifier / proxy',P('限定符 / 代理', 'Квалификатор / прокси')),
    ('ORM',P('对象关系映射', 'Объектно-реляционное отображение')),
    ('entity',P('实体：具有持久化标识的领域对象', 'Сущность: объект предметной области с персистентной идентичностью')),
    ('persistence context',P('持久化上下文：管理实体身份与状态的环境', 'Контекст персистентности: среда управления идентичностью и состоянием сущностей')),
    ('managed / detached',P('受管 / 游离：是否关联当前持久化上下文', 'Управляемая / отсоединённая: связана ли сущность с текущим контекстом')),
    ('dirty checking',P('脏检查：识别受管实体的状态修改', 'Отслеживание изменений: обнаружение изменений managed-сущности')),
    ('flush / commit',P('刷新到数据库 / 提交事务', 'Синхронизация с БД / фиксация транзакции')),
    ('lazy / eager loading',P('延迟加载 / 立即加载', 'Ленивая / немедленная загрузка')),
    ('owning side / mappedBy',P('关联拥有方 / 反向方通过 mappedBy 指定拥有方的关联属性', 'Владеющая сторона связи / на обратной стороне mappedBy указывает свойство владеющей стороны')),
    ('cascade',P('级联：将实体操作传播给关联实体', 'Каскадирование: распространение операций на связанные сущности')),
    ('optimistic / pessimistic locking',P('乐观锁 / 悲观锁', 'Оптимистическая / пессимистическая блокировка')),
    ('repository / DAO',P('仓储 / 数据访问对象', 'Репозиторий / объект доступа к данным')),
    ('transaction boundary',P('事务边界', 'Граница транзакции')),
    ('auto-configuration',P('自动配置', 'Автоконфигурация')),
    ('starter / BOM',P('依赖入口集合 / 依赖版本清单', 'Набор зависимостей / перечень согласованных версий зависимостей')),
    ('query derivation',P('查询派生：从方法声明生成查询', 'Выведение запроса: построение запроса по объявлению метода')),
    ('pagination / projection',P('分页 / 投影', 'Пагинация / проекция')),
    ('portability / coupling',P('可移植性 / 耦合', 'Переносимость / связанность')),
]

def make_glossary():
    out = '<section class="appendix" id="glossary" data-search-unit>' + heading(P('中俄术语与答辩连接句', 'Термины и связки для устного ответа')) + '<div class="glossary-grid">'
    for key, value in terms:
        out += '<div class="term"><code>' + esc(key) + '</code>' + pair(value) + '</div>'
    out += '</div>'
    out += block({'title':P('把答案组织成四句话', 'Постройте ответ из четырёх частей'), 'bullets':[
        P('定义：“X 是……，它的主要职责是……”', 'Определение: «X — это … Его основная задача — …»'),
        P('机制：“它通过……实现这一点；关键接口或注解是……”', 'Механизм: «Это достигается с помощью … Основные интерфейсы или аннотации — …»'),
        P('比较：“与 Y 相比，X 的区别在于……；代价是……”', 'Сравнение: «По сравнению с Y, X отличается тем, что … Цена такого подхода — …»'),
        P('实验：“在我的 Movie 项目中，这对应……；可以在……看到证据。”', 'Лабораторная: «В моём проекте Movie этому соответствует … Подтверждение находится в …»')
    ]})
    out += block({'title':P('当老师要求比较时', 'Когда преподаватель просит сравнить'), 'bullets':[
        P('“两者解决相关问题，但抽象层次不同。”', '«Обе технологии решают связанные задачи, но находятся на разных уровнях абстракции.»'),
        P('“这是规范规定的行为；具体 SQL 和优化取决于提供者。”', '«Это поведение определено спецификацией; конкретный SQL и оптимизации зависят от провайдера.»'),
        P('“这个选择减少了样板代码，但没有消除事务与性能设计的责任。”', '«Такой выбор сокращает шаблонный код, но не отменяет проектирование транзакций и производительности.»'),
        P('“我先说明本项目的配置，再区分另一种常见配置。”', '«Сначала я поясню конфигурацию своего проекта, затем выделю другой распространённый вариант.»')
    ]})
    return out + '</section>'

def make_review():
    out = '<section class="appendix" id="study-path" data-search-unit>' + heading(P('复习顺序与现场检查', 'Порядок повторения и проверка перед защитой'))
    out += '<div class="guide-steps">'
    for value in [
        P('第一遍：读全局关系图，按“平台 → 容器 → 持久化 → Repository → 自动配置”解释每个技术的位置。先能够说清谁是规范、谁是实现、谁是框架。', 'Первый проход: изучите общую схему и объясните место технологий в цепочке «платформа → контейнер → персистентность → репозитории → автоконфигурация». Сначала научитесь отличать спецификацию, реализацию и фреймворк.'),
        P('第二遍：逐题阅读正文和比较表。每题至少用 Movie 实验举一个例子，并主动说明一个优点、一个代价、一个适用条件。', 'Второй проход: прочитайте объяснения и таблицы. Для каждой темы приведите пример из Movie и назовите преимущество, цену решения и условие применимости.'),
        P('第三遍：切换为“俄语”与“答辩速记”，先不打开追问答案，用俄语说出定义、机制、对比和实验例子。不会的题回到全文复习。', 'Третий проход: включите русский язык и режим кратких ответов. Не открывая ответы на дополнительные вопросы, произнесите определение, механизм, сравнение и пример из лабораторной. Непонятные темы повторите в полном режиме.'),
        P('最后：使用随机抽题，不按目录顺序复述。能解释为什么项目使用 RESOURCE_LOCAL、为什么 EclipseLink 不是 JPA、为什么 Spring Data JPA 还需要 ORM，才算打通关联。', 'В конце: используйте случайные вопросы, отвечая не по порядку оглавления. Связи усвоены, когда вы можете объяснить, почему проект использует RESOURCE_LOCAL, почему EclipseLink не равен JPA и почему Spring Data JPA всё ещё нуждается в ORM.')
    ]:
        out += '<div class="guide-step">' + pair(value) + '</div>'
    out += '</div>'
    out += block({'title':P('答辩前，修正这八种说法', 'Перед защитой исправьте восемь формулировок'), 'table':{'headers':[P('容易说错', 'Неточная формулировка'),P('准确表述', 'Точная формулировка')], 'rows':[
        [P('“JPA 就是 Hibernate。”', '«JPA — это Hibernate.»'),P('JPA / Jakarta Persistence 是规范；Hibernate 和 EclipseLink 是不同实现。', 'JPA / Jakarta Persistence — спецификация; Hibernate и EclipseLink — разные реализации.')],
        [P('“Bean 的单例作用域保证线程安全。”', '«Singleton-область бина гарантирует потокобезопасность.»'),P('作用域规定实例与上下文的关系；可变共享状态仍需并发设计。', 'Область задаёт отношение экземпляра к контексту; изменяемое общее состояние требует отдельного проектирования конкурентного доступа.')],
        [P('“flush 后不能回滚。”', '«После flush откат невозможен.»'),P('flush 是同步 SQL；事务是否提交由 commit 决定，活动事务仍可回滚。', 'flush синхронизирует SQL; фиксация определяется commit, активную транзакцию ещё можно откатить.')],
        [P('“EAGER 表示一定用一条 JOIN。”', '«EAGER обязательно означает один JOIN.»'),P('EAGER 规定加载要求，不规定唯一 SQL 形态；仍可能出现额外查询。', 'EAGER задаёт требование загрузки, но не единственную форму SQL; дополнительные запросы возможны.')],
        [P('“有 @Entity 就自动成为 CDI Bean。”', '«@Entity автоматически делает класс CDI-бином.»'),P('实体状态由持久化上下文管理；CDI 发现和生命周期有独立规则。', 'Состоянием сущности управляет persistence context; у CDI отдельные правила обнаружения и жизненного цикла.')],
        [P('“Spring Boot 是应用服务器或 ORM。”', '«Spring Boot — сервер приложений или ORM.»'),P('Boot 整合配置、依赖与运行方式；Web 服务器和 ORM 由具体依赖提供。', 'Boot объединяет настройку, зависимости и запуск; веб-сервер и ORM предоставляются конкретными зависимостями.')],
        [P('“Spring Data 的 save 就是数据库 UPSERT。”', '«save в Spring Data — это UPSERT базы данных.»'),P('具体模块定义 save；Spring Data JPA 通常依据新实体检测选择 persist 或 merge。', 'Семантику save задаёт модуль; Spring Data JPA обычно выбирает persist или merge по определению новой сущности.')],
        [P('“Jakarta Data 替代 JPA，并强制共享上下文。”', '«Jakarta Data заменяет JPA и требует общий контекст.»'),P('Data 规定 Repository 抽象；映射与存储取决于提供者，1.0 不统一规定与 JPA 持久化上下文的集成。', 'Data задаёт абстракцию репозиториев; отображение и хранение зависят от провайдера. Версия 1.0 не унифицирует интеграцию с persistence context JPA.')],
    ]}})
    return out + '</section>'

def main(sections=None):
    if sections is None:
        sections = []
        for name in ['part1.json','part2.json','part3.json']:
            sections.extend(json.loads((HERE / name).read_text(encoding='utf-8-sig')))
    assert len(sections) == 9
    assert len({s['id'] for s in sections}) == 9
    def verify(value):
        if isinstance(value,dict):
            if 'zh' in value or 'ru' in value:
                assert set(value) == {'zh','ru'} and all(isinstance(x,str) and x.strip() for x in value.values()), value
            for child in value.values(): verify(child)
        elif isinstance(value,list):
            for child in value: verify(child)
    verify(sections)
    for s in sections:
        for b in s['blocks']:
            if 'table' in b:
                assert all(len(row) == len(b['table']['headers']) for row in b['table']['rows'])
        assert len(s['questions']) >= 4
        assert s['sources'] and all(x['url'].startswith('https://') for x in s['sources'])
    nav = [('map','↳',P('技术关系图', 'Карта технологий'))] + [(s['id'],s['number'],s['title']) for s in sections] + [('lab','↳',P('联系我的实验', 'Моя лабораторная')),('glossary','↳',P('术语与表达', 'Термины и связки')),('study-path','↳',P('复习与纠错', 'Повторение')),('drill','↳',P('随机抽题', 'Случайный вопрос'))]
    css = (HERE / 'guide.css').read_text(encoding='utf-8')
    js = (HERE / 'guide.js').read_text(encoding='utf-8')
    doc = '<!DOCTYPE html><html lang="zh-CN"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1"><meta name="color-scheme" content="light"><meta name="description" content="信息系统实验答辩中俄双语学习手册：Jakarta EE、CDI、ORM、Persistence、Data、Spring、Boot 与 Spring Data。"><title>信息系统答辩 · Информационные системы</title><style>' + css + '</style></head><body data-language="both" data-study="full"><a class="skip" href="#content">' + inline(P('跳到正文', 'К основному тексту')) + '</a>'
    doc += '<header class="topbar"><a href="#hero" class="brand"><span class="brand-mark" aria-hidden="true">IS</span><span>信息系统 · ИС<small>答辩学习手册 · Подготовка к защите</small></span></a><div class="toolbar"><div class="segmented" role="group" aria-label="语言 / Язык"><button type="button" data-lang-choice="both" aria-pressed="true">中 / РУ</button><button type="button" data-lang-choice="zh" aria-pressed="false">中文</button><button type="button" data-lang-choice="ru" aria-pressed="false">Русский</button></div><button id="review-toggle" class="tool-btn review-toggle" type="button" aria-pressed="false">' + inline(P('答辩速记', 'Краткие ответы')) + '</button><div class="search-box"><label class="sr-only" for="search">搜索 / Поиск</label><input id="search" type="search" placeholder="搜索 / Поиск" autocomplete="off" enterkeyhint="search"><button type="button" id="clear-search" class="clear-search" aria-label="清除 / Очистить" hidden>×</button></div><button type="button" id="print-guide" class="tool-btn print-button">' + inline(P('打印', 'Печать')) + '</button></div></header>'
    doc += '<div class="mobile-nav"><label for="chapter-select">' + inline(P('跳转章节', 'Перейти к разделу')) + '</label><select id="chapter-select"><option value="">目录 / Оглавление</option>' + ''.join('<option value="' + i + '">' + esc(n + ' ' + p['zh'] + ' · ' + p['ru']) + '</option>' for i,n,p in nav) + '</select></div><div class="layout"><aside class="sidebar" aria-label="目录 / Оглавление"><p class="nav-label">' + inline(P('九个问题，一套完整技术关系', 'Девять тем и связи между ними')) + '</p><nav class="toc">'
    doc += ''.join('<a href="#' + i + '"><span class="nav-num">' + n + '</span><span>' + inline(p) + '</span></a>' for i,n,p in nav)
    doc += '</nav><div class="nav-foot"><div id="progress-label">已掌握 0 / 9 · Освоено 0 / 9</div><div id="progress-track" class="progress-track" role="progressbar" aria-label="掌握进度 / Прогресс" aria-valuemin="0" aria-valuemax="9" aria-valuenow="0"><span id="progress-bar"></span></div>' + inline(P('掌握标记保存在当前浏览器。', 'Отметки сохраняются в этом браузере.')) + '</div></aside><main class="main" id="content"><div id="search-status" class="search-status" role="status" hidden></div><div id="empty" class="empty-state" hidden>' + pair(P('没有匹配章节。试试 JPA、事务、CDI 或 Repository。', 'Разделов не найдено. Попробуйте JPA, транзакция, CDI или Repository.')) + '</div>'
    doc += '<section class="hero" id="hero"><div class="eyebrow">' + inline(P('信息系统实验 · 中俄逐段对应', 'Лабораторная по ИС · параллельные тексты')) + '</div><h1>' + inline(P('理解技术之间的关系，\n再用俄语讲清楚。', 'Поймите связи технологий\nи объясните их по-русски.')) + '</h1>'
    doc += pair(P('围绕九道答辩题，学习定义、工作机制、API、差异、优缺点与适用场景。每题包含可直接练习的俄语开场和老师可能提出的追问，并联系你的 Movie 实验。', 'По девяти темам защиты разберите определения, механизмы, API, различия, преимущества, ограничения и условия применения. В каждой теме есть текст для начала устного ответа и возможные дополнительные вопросы, а также связь с вашей лабораторной Movie.'),cls='lead')
    doc += '<div class="meta"><span>Java 17 · Jakarta EE 10</span><span>中文 ⇄ Русский</span><span>' + inline(P('离线单文件', 'Один файл, без сети')) + '</span><span>2026-10-26</span></div></section>'
    doc += make_map() + ''.join(section(s) for s in sections) + make_lab() + make_glossary() + make_review()
    doc += '<section class="study-panel" id="drill" data-search-unit>' + heading(P('随机抽题：先说，再核对', 'Случайный вопрос: сначала ответьте сами'))
    doc += pair(P('每轮覆盖所有追问，不重复抽取。先用俄语组织答案，再展开参考要点；也可以切换到双语检查理解。', 'Каждый раунд охватывает все дополнительные вопросы без повторов. Сначала сформулируйте ответ по-русски, затем откройте опорные пункты; для проверки понимания можно включить два языка.'),cls='section-intro')
    doc += '<div id="drill-meta" class="drill-meta"></div><div id="drill-question" class="drill-question" aria-live="polite"></div><div id="drill-answer" class="drill-answer" hidden></div><div class="drill-actions"><button id="reveal-answer" type="button" class="primary-btn" aria-expanded="false" aria-controls="drill-answer">' + inline(P('展开 / 收起答案', 'Показать / скрыть ответ')) + '</button><button type="button" id="next-question" class="secondary-btn">' + inline(P('下一题', 'Следующий вопрос')) + '</button></div><p id="drill-position" class="drill-meta"></p><noscript>' + pair(P('随机抽题需要 JavaScript；上方各章节的追问和正文可以直接阅读。', 'Для случайных вопросов нужен JavaScript; текст и вопросы в разделах выше доступны без него.')) + '</noscript></section>'
    doc += '<footer class="footer">' + pair(P('本手册用于理解与口头练习。代码为带上下文说明的教学片段，未声明为可直接运行的完整项目。正文与引用可离线阅读，打开官方链接需要网络；语言切换、抽题和掌握记录需要 JavaScript。', 'Пособие предназначено для понимания и устной тренировки. Код — учебные фрагменты с пояснениями контекста, а не заявленный полностью запускаемый проект. Текст и ссылки доступны офлайн, переход на официальные сайты требует сети; переключение языков, случайные вопросы и отметки требуют JavaScript.')) + '</footer></main></div><button type="button" id="back-top" class="back-top" aria-label="返回顶部 / Наверх">↑</button><div id="toast" class="toast" role="status" hidden></div>'
    deck = [{'topic':P(s['number']+' · '+s['title']['zh'],s['number']+' · '+s['title']['ru']), **qa} for s in sections for qa in s['questions']]
    doc += '<script type="application/json" id="drill-data">' + json.dumps(deck,ensure_ascii=False).replace('<','\\u003c') + '</script><script>' + js + '</script></body></html>'
    OUT.write_text(doc, encoding='utf-8')
    all_text = json.dumps(sections, ensure_ascii=False)
    print(json.dumps({'file':str(OUT), 'bytes':OUT.stat().st_size,'topics':len(sections),'blocks':sum(len(s['blocks']) for s in sections),'followups':len(deck),'source_links':sum(len(s['sources']) for s in sections),'matched_language_pairs':len(re.findall(r'"zh":',all_text))},ensure_ascii=False))

if __name__ == '__main__':
    main()
