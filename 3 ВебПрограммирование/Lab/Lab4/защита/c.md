# Java EE 平台。规范及其实现。

Java EE（Java Platform, Enterprise Edition）是一个用于开发企业级应用的平台规范。它定义了一系列标准API和服务，如Servlet、JPA、EJB、JMS等，用于构建分布式、可扩展、安全的应用程序。规范由Java Community Process（JCP）制定，并通过JSRs（Java Specification Requests）文档化。实现包括Oracle的WebLogic、IBM的WebSphere、Red Hat的WildFly/JBoss以及开源项目如Apache TomEE。Java EE 8是最后一个版本，之后被移交至Eclipse基金会并更名为Jakarta EE。

Java EE (Java Platform, Enterprise Edition) — это платформа-спецификация для разработки корпоративных приложений. Она определяет набор стандартных API и сервисов, таких как Servlet, JPA, EJB, JMS, для создания распределённых, масштабируемых и безопасных приложений. Спецификация разрабатывается Java Community Process (JCP) и документируется в виде JSR (Java Specification Requests). Реализации включают Oracle WebLogic, IBM WebSphere, Red Hat WildFly/JBoss, а также open-source проекты, такие как Apache TomEE. Java EE 8 была последней версией, после чего платформа была передана Eclipse Foundation и переименована в Jakarta EE.

---

# IoC、CDI 与位置透明性原则。组件与容器。

IoC（控制反转）是一种设计原则，将对象的创建和依赖管理从组件转移到容器。在Java EE中，CDI（Contexts and Dependency Injection）是实现IoC的标准，允许通过注解（如 `@Inject`）进行依赖注入。位置透明性指组件无需知道依赖的具体位置（如本地或远程），由容器处理通信细节。组件（如EJB、Servlet）是业务逻辑单元，容器（如Web容器、EJB容器）提供运行时环境，管理生命周期、事务和安全。

IoC (инверсия управления) — это принцип проектирования, при котором создание объектов и управление зависимостями передаются от компонентов контейнеру. В Java EE CDI (Contexts and Dependency Injection) является стандартной реализацией IoC, позволяющей внедрять зависимости через аннотации (например, `@Inject`). Прозрачность расположения означает, что компонентам не нужно знать точное местоположение зависимостей (локальное или удалённое), так как контейнер обрабатывает детали коммуникации. Компоненты (например, EJB, Servlet) — это единицы бизнес-логики, а контейнер (например, веб-контейнер, EJB-контейнер) предоставляет среду выполнения, управляя жизненным циклом, транзакциями и безопасностью.

---

# 组件的生命周期管理。部署描述符。

Java EE组件的生命周期由容器管理。例如，Servlet的生命周期包括 `init()`、`service()`和 `destroy()`方法；EJB有 `@PostConstruct`、`@PreDestroy`等回调。部署描述符是XML文件（如 `web.xml`、`ejb-jar.xml`），用于配置组件行为、依赖和资源，替代或补充注解。现代Java EE更倾向于使用注解，但部署描述符仍用于覆盖注解或集中配置。

Жизненный цикл компонентов Java EE управляется контейнером. Например, жизненный цикл Servlet включает методы `init()`, `service()` и `destroy()`; у EJB есть обратные вызовы `@PostConstruct`, `@PreDestroy`. Дескрипторы развёртывания — это XML-файлы (например, `web.xml`, `ejb-jar.xml`), используемые для настройки поведения компонентов, зависимостей и ресурсов, что может заменять или дополнять аннотации. Современный Java EE предпочитает использование аннотаций, но дескрипторы развёртывания всё ещё применяются для переопределения аннотаций или централизованной конфигурации.

---

# Java EE API。组件类型。Java EE平台配置文件。

Java EE API包括Servlet、JSP、EJB、JPA、JMS、JAX-RS、JAX-WS等。组件类型分为Web组件（Servlet、JSP）、业务组件（EJB）和客户端组件（Application Client）。Java EE平台配置文件（如Full Platform、Web Profile）定义了API子集，以简化部署。Web Profile包含Web相关API（Servlet、JPA），适合轻量级应用；Full Platform包含所有API（包括EJB、JMS），适用于复杂企业应用。

Java EE API включает Servlet, JSP, EJB, JPA, JMS, JAX-RS, JAX-WS и другие. Типы компонентов делятся на веб-компоненты (Servlet, JSP), бизнес-компоненты (EJB) и клиентские компоненты (Application Client). Профили платформы Java EE (например, Full Platform, Web Profile) определяют подмножества API для упрощения развёртывания. Web Profile включает веб-ориентированные API (Servlet, JPA) и подходит для легковесных приложений; Full Platform содержит все API (включая EJB, JMS) для сложных корпоративных приложений.

---

# EJB组件。无状态与有状态会话Bean。EJB Lite与EJB Full。

EJB（Enterprise JavaBeans）是Java EE的业务组件，用于封装业务逻辑。无状态会话Bean（SLSB）不保存客户端状态，适用于可重用的操作；有状态会话Bean（SFSB）维护客户端会话状态，适用于多步骤交互。EJB Lite是EJB的子集（仅包含会话Bean、拦截器、事务），轻量级；EJB Full包含所有特性（如消息驱动Bean、远程调用），功能完整。

EJB (Enterprise JavaBeans) — это бизнес-компоненты Java EE для инкапсуляции бизнес-логики. Stateless Session Bean (SLSB) не сохраняет состояние клиента и подходит для повторно используемых операций; Stateful Session Bean (SFSB) поддерживает состояние сессии клиента для многошаговых взаимодействий. EJB Lite — это подмножество EJB (только сессионные бины, перехватчики, транзакции), легковесное; EJB Full включает все функции (например, Message-Driven Bean, удалённый вызов) и является полным.

---

# 在Java EE中处理电子邮件。JavaMail API。

Java EE通过JavaMail API处理电子邮件。它提供 `javax.mail`包，支持SMTP、POP3、IMAP协议。核心类包括 `Session`（配置邮件会话）、`Message`（创建邮件）、`Transport`（发送邮件）。通常与JNDI查找邮件资源（如 `mail/Session`）结合使用。示例：通过 `@Resource`注入 `Session`，使用 `MimeMessage`构建邮件内容，调用 `Transport.send()`发送。

Java EE обрабатывает электронную почту через JavaMail API. Он предоставляет пакет `javax.mail`, поддерживающий протоколы SMTP, POP3, IMAP. Ключевые классы включают `Session` (настройка почтовой сессии), `Message` (создание письма), `Transport` (отправка письма). Обычно используется с JNDI для поиска почтовых ресурсов (например, `mail/Session`). Пример: внедрение `Session` через `@Resource`, создание `MimeMessage` для содержимого, вызов `Transport.send()` для отправки.

---

# JMS。消息队列的实现。消息传递到客户端的方式。消息驱动Bean。

JMS（Java Message Service）是Java EE的消息传递API，支持点对点（Queue）和发布-订阅（Topic）模型。实现包括ActiveMQ、IBM MQ、HornetQ（WildFly）。消息传递到客户端可通过消费者同步接收（`receive()`）或监听器异步处理（`MessageListener`）。消息驱动Bean（MDB）是一种特殊EJB，异步消费JMS消息，由容器管理并发和事务。

JMS (Java Message Service) — это API обмена сообщениями в Java EE, поддерживающее модели точка-точка (очередь) и издатель-подписчик (топик). Реализации включают ActiveMQ, IBM MQ, HornetQ (WildFly). Доставка сообщений клиенту может быть синхронной через потребителя (`receive()`) или асинхронной через слушателя (`MessageListener`). Message-Driven Bean (MDB) — это специальный EJB, который асинхронно потребляет JMS-сообщения, а контейнер управляет параллелизмом и транзакциями.

---

# 事务的概念。Java EE中的事务管理。JTA。

事务是确保数据一致性的操作单元，具有ACID属性。Java EE支持声明式事务（通过 `@Transactional`或部署描述符）和编程式事务（使用 `UserTransaction`）。JTA（Java Transaction API）是分布式事务标准，允许跨多个资源（如数据库、JMS）管理事务。容器管理事务（CMT）由EJB容器处理；Bean管理事务（BMT）由开发者编码控制。

Транзакция — это единица операций, обеспечивающая целостность данных, с свойствами ACID. Java EE поддерживает декларативные транзакции (через `@Transactional` или дескрипторы развёртывания) и программные транзакции (с использованием `UserTransaction`). JTA (Java Transaction API) — стандарт для распределённых транзакций, позволяющий управлять транзакциями across multiple resources (например, базы данных, JMS). Контейнер управляет транзакциями (CMT) через EJB-контейнер; бины управляют транзакциями (BMT) через код разработчика.

---

# Web服务。JAX-RS与JAX-WS技术。

Web服务允许跨网络交互。JAX-WS（基于SOAP）使用XML消息，支持WS-*标准（如安全性），适用于复杂企业集成；JAX-RS（基于REST）使用HTTP方法（GET/POST），轻量级，适合Web和移动应用。JAX-WS通过 `@WebService`注解实现；JAX-RS通过 `@Path`、`@GET`等注解定义资源。Java EE同时支持两者，但REST更流行。

Веб-сервисы позволяют взаимодействовать по сети. JAX-WS (на основе SOAP) использует XML-сообщения, поддерживает стандарты WS-* (например, безопасность) и подходит для сложной корпоративной интеграции; JAX-RS (на основе REST) использует HTTP-методы (GET/POST), легковесный и подходит для веб- и мобильных приложений. JAX-WS реализуется через аннотацию `@WebService`; JAX-RS определяет ресурсы через аннотации `@Path`, `@GET` и другие. Java EE поддерживает оба, но REST более популярен.

---

# Spring平台。与Java EE的异同。

Spring是开源框架，提供全面的编程和配置模型。与Java EE相同点：都支持IoC、事务、Web服务。不同点：Spring更灵活，可独立使用，模块可选；Java EE是标准规范，需容器实现。Spring Boot简化了配置和部署，而Java EE更依赖容器。Spring生态丰富（如Cloud、Security），Java EE更标准化。现代Jakarta EE与Spring竞争，但常共同使用。

Spring — это open-source фреймворк, предоставляющий комплексную модель программирования и конфигурации. Сходства с Java EE: поддержка IoC, транзакций, веб-сервисов. Различия: Spring более гибкий, может использоваться независимо, модули опциональны; Java EE — стандартная спецификация, требует реализации контейнера. Spring Boot упрощает конфигурацию и развёртывание, а Java EE больше зависит от контейнера. Экосистема Spring богаче (например, Cloud, Security), Java EE более стандартизирована. Современный Jakarta EE конкурирует со Spring, но они часто используются вместе.

---

# Spring模块。Spring运行时架构。Spring Security与Spring Data。

Spring模块包括Core（IoC）、AOP、Data Access（JDBC、ORM）、Web（MVC）、Security、Boot等。运行时架构基于ApplicationContext容器，管理Bean生命周期和依赖。Spring Security提供认证和授权，支持OAuth、JWT；Spring Data简化数据访问（JPA、MongoDB），通过Repository抽象查询。Spring Boot通过自动配置和嵌入式服务器简化开发。

Модули Spring включают Core (IoC), AOP, Data Access (JDBC, ORM), Web (MVC), Security, Boot и другие. Архитектура времени выполнения основана на контейнере ApplicationContext, управляющем жизненным циклом бинов и зависимостями. Spring Security предоставляет аутентификацию и авторизацию, поддерживает OAuth, JWT; Spring Data упрощает доступ к данным (JPA, MongoDB) через абстракцию Repository. Spring Boot упрощает разработку через авто-конфигурацию и встроенные серверы.

---

# Spring中IoC与CDI的实现。与Java EE的异同。

Spring通过ApplicationContext和BeanFactory实现IoC，依赖注入通过 `@Autowired`、XML配置或Java Config。CDI在Spring中类似，但Spring的IoC更早且功能更广（如 `@Qualifier`）。与Java EE CDI比较：两者都支持类型安全注入，但Spring不严格遵循CDI规范，提供更多扩展（如 `@Primary`）。Spring可与CDI集成（如使用 `@Inject`），但通常独立使用。

Spring реализует IoC через ApplicationContext и BeanFactory, внедрение зависимостей — через `@Autowired`, XML-конфигурацию или Java Config. CDI в Spring аналогичен, но IoC Spring старше и функциональнее (например, `@Qualifier`). По сравнению с Java EE CDI: оба поддерживают типобезопасное внедрение, но Spring не строго следует спецификации CDI, предлагая больше расширений (например, `@Primary`). Spring может интегрироваться с CDI (например, с `@Inject`), но обычно используется независимо.

---

# Java EE与Spring中REST API的实现。

Java EE使用JAX-RS实现REST API（如Jersey、RESTEasy），通过 `@Path`、`@GET`等注解定义端点，集成容器服务（如CDI、事务）。Spring使用Spring MVC（`@RestController`、`@RequestMapping`）或Spring WebFlux（响应式），依赖Spring IoC。比较：JAX-RS更标准化，Spring MVC更灵活（如拦截器、全局异常处理）。两者都支持JSON/XML，但Spring生态工具更丰富（如Swagger集成）。

Java EE использует JAX-RS для реализации REST API (например, Jersey, RESTEasy), определяя endpoints через аннотации `@Path`, `@GET` и другие, интегрируя сервисы контейнера (например, CDI, транзакции). Spring использует Spring MVC (`@RestController`, `@RequestMapping`) или Spring WebFlux (реактивный), зависит от Spring IoC. Сравнение: JAX-RS более стандартизирован, Spring MVC более гибок (например, перехватчики, глобальная обработка исключений). Оба поддерживают JSON/XML, но экосистема Spring богаче инструментами (например, интеграция Swagger).

---

# React JS。应用程序的架构与主要开发原则。

React是用于构建UI的JavaScript库。架构基于组件树，数据单向流动（自上而下）。开发原则包括：声明式编程（描述UI状态）、组件化（可复用）、虚拟DOM（高效更新）、单向数据流（易于调试）。通常与状态管理库（如Redux）和路由库（React Router）结合使用。React Hooks（如 `useState`）允许函数组件使用状态和副作用。

React — это JavaScript-библиотека для построения UI. Архитектура основана на дереве компонентов с односторонним потоком данных (сверху вниз). Принципы разработки включают: декларативное программирование (описание состояния UI), компонентность (переиспользуемость), виртуальный DOM (эффективное обновление), односторонний поток данных (легкая отладка). Обычно используется с библиотеками управления состоянием (например, Redux) и маршрутизации (React Router). React Hooks (например, `useState`) позволяют функциональным компонентам использовать состояние и побочные эффекты.

---

# React组件。State与props。"智能"组件与"木偶"组件。

React组件可以是函数或类。props是从父组件传递的数据，不可变；state是组件内部状态，可变（通过 `setState`更新）。“智能”组件（容器组件）管理状态和逻辑，通常使用state；“木偶”组件（展示组件）只接收props并渲染UI，无状态。这种分离提高了可测试性和复用性。

Компоненты React могут быть функциями или классами. props — это данные, передаваемые от родительского компонента, неизменяемые; state — внутреннее состояние компонента, изменяемое (обновляется через `setState`). "Умные" компоненты (контейнеры) управляют состоянием и логикой, обычно используют state; "глупые" компоненты (презентационные) только получают props и отображают UI, не имеют состояния. Это разделение повышает тестируемость и переиспользуемость.

---

# React应用程序中的页面标记。JSX。

JSX是JavaScript语法扩展，允许在JavaScript中编写类似HTML的标记。它被Babel转译为 `React.createElement()`调用。示例：`<div className="app">{variable}</div>`。JSX支持嵌入表达式、条件渲染和循环。它提高了代码可读性，并允许类型检查（如TypeScript）。注意：JSX中属性使用驼峰命名（如 `onClick`），`class`变为 `className`。

JSX — это расширение синтаксиса JavaScript, позволяющее писать HTML-подобную разметку в JavaScript. Оно транспилируется Babel в вызовы `React.createElement()`. Пример: `<div className="app">{variable}</div>`. JSX поддерживает встраивание выражений, условный рендеринг и циклы. Это повышает читаемость кода и позволяет проверку типов (например, TypeScript). Внимание: в JSX атрибуты используют camelCase (например, `onClick`), `class` становится `className`.

---

# React应用程序中的导航。React Router。

React Router是React的标准路由库，管理SPA中的导航。核心组件包括 `<BrowserRouter>`（HTML5 history）、`<Route>`（定义路径）、`<Link>`（导航链接）、`<Switch>`（独占路由）。示例：`<Route path="/home" component={Home} />`。React Router v6引入 `<Routes>`和 `useNavigate`钩子。它支持嵌套路由、动态参数和懒加载。

React Router — стандартная библиотека маршрутизации для React, управляющая навигацией в SPA. Ключевые компоненты: `<BrowserRouter>` (HTML5 history), `<Route>` (определение пути), `<Link>` (навигационные ссылки), `<Switch>` (эксклюзивные маршруты). Пример: `<Route path="/home" component={Home} />`. React Router v6 представил `<Routes>` и хук `useNavigate`. Он поддерживает вложенные маршруты, динамические параметры и ленивую загрузку.

---

# 界面状态管理。Redux。

Redux是状态管理库，用于管理React应用中的全局状态。原则包括：单一数据源（store）、state只读（通过reducers更新）、纯函数更改。核心概念：Action（描述事件）、Reducer（处理逻辑）、Store（保存状态）。React-Redux提供 `<Provider>`和 `useSelector`/`useDispatch`钩子连接组件。适用于复杂状态交互，但可能带来样板代码；现代替代品有Context API或MobX。

Redux — это библиотека управления состоянием для управления глобальным состоянием в React-приложениях. Принципы включают: единственный источник данных (store), state только для чтения (обновляется через reducers), изменения чистыми функциями. Ключевые концепции: Action (описание события), Reducer (логика обработки), Store (хранение состояния). React-Redux предоставляет `<Provider>` и хуки `useSelector`/`useDispatch` для подключения компонентов. Подходит для сложных взаимодействий с состоянием, но может создавать шаблонный код; современные альтернативы — Context API или MobX.

---

# Angular：架构与主要开发原则。

Angular是用于构建Web应用的TypeScript框架。架构基于模块化、组件化和依赖注入。核心概念包括模块（`@NgModule`）、组件（`@Component`）、服务（`@Injectable`）。开发原则：单向数据流（与双向绑定结合）、声明式模板、TypeScript强类型、RxJS响应式编程。Angular CLI简化开发流程。它提供完整解决方案（路由、表单、HTTP客户端），适用于大型应用。

Angular — это TypeScript-фреймворк для построения веб-приложений. Архитектура основана на модульности, компонентности и внедрении зависимостей. Ключевые концепции включают модули (`@NgModule`), компоненты (`@Component`), сервисы (`@Injectable`). Принципы разработки: односторонний поток данных (в сочетании с двусторонней привязкой), декларативные шаблоны, строгая типизация TypeScript, реактивное программирование с RxJS. Angular CLI упрощает процесс разработки. Он предоставляет полное решение (маршрутизация, формы, HTTP-клиент) и подходит для крупных приложений.

---

# Angular：模块、组件、服务与依赖注入（DI）。

模块（`@NgModule`）组织相关组件、指令、服务，通过 `imports`、`declarations`、`providers`配置。组件（`@Component`）是UI构建块，包含模板、样式和逻辑。服务（`@Injectable`）封装业务逻辑和数据访问。依赖注入（DI）是Angular核心，通过构造函数注入服务，提高可测试性和模块化。示例：`constructor(private service: DataService) {}`。Angular的DI是层次化的，与组件树对齐。

Модули (`@NgModule`) организуют связанные компоненты, директивы, сервисы через конфигурацию `imports`, `declarations`, `providers`. Компоненты (`@Component`) — строительные блоки UI, включают шаблон, стили и логику. Сервисы (`@Injectable`) инкапсулируют бизнес-логику и доступ к данным. Внедрение зависимостей (DI) — ядро Angular, сервисы внедряются через конструктор, что повышает тестируемость и модульность. Пример: `constructor(private service: DataService) {}`. DI в Angular иерархична и соответствует дереву компонентов.

---

# Angular：页面模板、组件生命周期、CSS引入。

Angular模板是HTML增强，支持插值（`{{value}}`）、属性绑定（`[property]`）、事件绑定（`(event)`）和结构指令（`*ngIf`、`*ngFor`）。组件生命周期钩子包括 `ngOnInit`（初始化）、`ngOnChanges`（输入变化）、`ngOnDestroy`（清理）。CSS可通过组件元数据 `styles`内联、`styleUrls`引用外部文件，或全局样式引入。Angular支持CSS预处理器（Sass、Less），并封装样式（模拟Shadow DOM）。

Шаблоны Angular — это расширенный HTML, поддерживающий интерполяцию (`{{value}}`), привязку свойств (`[property]`), привязку событий (`(event)`) и структурные директивы (`*ngIf`, `*ngFor`). Хуки жизненного цикла компонента включают `ngOnInit` (инициализация), `ngOnChanges` (изменения входных данных), `ngOnDestroy` (очистка). CSS можно встраивать через метаданные компонента `styles`, ссылаться через `styleUrls` на внешние файлы или добавлять глобально. Angular поддерживает препроцессоры CSS (Sass, Less) и инкапсуляцию стилей (эмуляция Shadow DOM).

---

# Angular：客户端-服务器交互、表单数据的创建、发送与验证。

Angular通过 `HttpClient`模块（`@angular/common/http`）进行客户端-服务器交互，支持GET、POST等HTTP方法，返回Observable（RxJS）。表单有两种：模板驱动表单（`ngModel`）和响应式表单（`FormGroup`、`FormControl`）。验证通过内置验证器（如 `Validators.required`）或自定义函数实现。数据发送使用 `HttpClient.post(url, data)`，可添加头信息和错误处理。示例：订阅Observable并更新UI。

Angular взаимодействует с сервером через модуль `HttpClient` (`@angular/common/http`), поддерживает методы HTTP (GET, POST и другие), возвращает Observable (RxJS). Формы бывают двух типов: шаблонные ( `ngModel`) и реактивные (`FormGroup`, `FormControl`). Валидация осуществляется через встроенные валидаторы (например, `Validators.required`) или пользовательские функции. Данные отправляются с помощью `HttpClient.post(url, data)`, можно добавлять заголовки и обрабатывать ошибки. Пример: подписка на Observable и обновление UI.
