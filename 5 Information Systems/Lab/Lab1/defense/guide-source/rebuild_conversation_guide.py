"""Build the revised nine-topic guide. The previous detailed content stays intact."""
from pathlib import Path
import json
import re
import build_guide as base
from conversation_content import SECTIONS

P, pair, heading, inline = base.P, base.pair, base.heading, base.inline
SHARED = 'https://chatgpt.com/share/6adffbf3-efa0-83eb-b196-a875afa5b765'
ORIGINAL_BLOCK = base.block

def lesson_block(b):
    result = ORIGINAL_BLOCK(b)
    if b.get('after'):
        result = result[:-6] + ''.join(pair(x) for x in b['after']) + '</div>'
    return result

def lesson(s):
    result = f'<section class="chapter" id="{s["id"]}" data-search-unit aria-labelledby="heading-{s["id"]}">'
    result += '<header class="chapter-head"><div class="chapter-kicker"><span class="chapter-number">'
    result += inline(P('考题 ' + s['number'] + ' / 09', 'Тема ' + s['number'] + ' / 09'))
    result += '</span><button type="button" class="learn-button" aria-pressed="false">' + inline(P('○ 标记掌握','○ Отметить')) + '</button></div>'
    result += f'<h2 id="heading-{s["id"]}">' + inline(s['title']) + '</h2>' + pair(s['summary'], cls='chapter-summary') + '</header>'
    result += '<div class="chapter-body"><div class="full-only">' + ''.join(lesson_block(b) for b in s['blocks']) + '</div>'
    result += '<div class="oral">' + heading(P('最后，练习这段答辩回答', 'В конце произнесите ответ для защиты'),'h3') + pair(s['oral']) + '</div>'
    result += heading(P('检查是否听懂：先回答，再展开', 'Проверка понимания: сначала ответьте сами'),'h3').replace('<h3>','<h3 class="questions-title">')
    for q in s['questions']:
        result += '<details class="question"><summary>' + pair(q['q'], tag='span', inner='span') + '</summary><div class="question-answer">' + pair(q['a']) + '</div></details>'
    result += '<div class="full-only"><details class="source-details"><summary>' + inline(P('查看官方参考资料','Официальные источники')) + '</summary>' + base.sources(s['sources']) + '</details></div>'
    return result + '</div></section>'

def appendix(id, title, text):
    return f'<section class="appendix" id="{id}" data-search-unit>' + heading(title) + text + '</section>'

def introduction():
    text = pair(P('全书沿用对话中的 Student（学生）例子，再联系你的 Movie 实验。每道题按“先理解 → 看例子 → 做比较 → 答辩表达”展开；术语出现时就解释，不先堆一大串定义。', 'В книге используется пример Student из диалога с последующей связью с вашей лабораторной Movie. Каждая тема идёт по схеме «понять → разобрать пример → сравнить → ответить на защите». Термины объясняются по мере появления.'), cls='section-intro')
    text += '<div class="reading-route">'
    for p in [P('业务需求：查询、保存学生。', 'Бизнес-задача: найти или сохранить студента.'),
              P('对象管理：CDI / Spring 装配服务与依赖。', 'Управление объектами: CDI / Spring собирают сервисы и зависимости.'),
              P('数据访问：Repository 表达操作；JPA 管理关系持久化。', 'Доступ к данным: Repository выражает операции, JPA управляет реляционной персистентностью.'),
              P('具体执行：ORM 提供者与驱动连接数据库。', 'Выполнение: ORM-провайдер и драйвер связываются с БД.')]:
        text += pair(p, cls='route-step')
    text += '</div>'
    text += pair(P('你提出的四类困惑已放回对应章节：第 3 题讲 IoC、DI、CDI 与 EJB；第 4 题讲 ORM、规范与实现；第 5 题讲持久化上下文；第 6、9 题讲 Repository、Data 与字段解析。全部九道原始考题都重新讲解。', 'Ваши вопросы включены в соответствующие темы: тема 3 — IoC, DI, CDI и EJB; 4 — ORM, стандарт и реализация; 5 — persistence context; 6 и 9 — Repository, Data и определение полей. Все девять исходных тем объяснены заново.'), cls='callout')
    text += '<p class="discussion-source"><a href="' + SHARED + '" target="_blank" rel="noopener noreferrer">' + inline(P('本次重构依据：你提供的讲解与追问对话','Основа переработки: предоставленный вами диалог с объяснениями и вопросами')) + '</a></p>'
    return appendix('map', P('先看全书怎样连起来', 'Сначала свяжем темы между собой'), text)

def lab():
    text = pair(P('学生例子帮助理解；下面只把同一思路对应到你的实际代码，不再展开底层配置细节。', 'Пример студентов помогает понять идею; ниже она кратко сопоставлена с вашим кодом без разбора низкоуровневых настроек.'),cls='section-intro')
    text += base.table({'headers':[P('你的代码','Ваш код'),P('在本书中对应什么','Чему соответствует')], 'rows':[
        [P('MovieResource','MovieResource'),P('接收 HTTP 请求，是 REST 入口。','Принимает HTTP-запросы: REST-вход.')],
        [P('MovieService','MovieService'),P('协调业务；是 @ApplicationScoped 的 CDI Bean。','Координирует бизнес-логику; CDI-бин @ApplicationScoped.')],
        [P('Database','Database'),P('创建 EntityManager，并管理 RESOURCE_LOCAL 事务。','Создаёт EntityManager и управляет транзакциями RESOURCE_LOCAL.')],
        [P('Movie + EclipseLink','Movie + EclipseLink'),P('Movie 是 JPA 实体，EclipseLink 是实际 ORM 提供者。','Movie — JPA-сущность, EclipseLink — фактический ORM-провайдер.')]
    ]})
    text += pair(P('因此可以在答辩时说：我的项目使用 Jakarta EE 的 REST、CDI 与 Persistence；由 EclipseLink 实现 ORM。目前没有使用 Spring Data 或 Jakarta Data，数据操作通过 EntityManager 编写。', 'На защите можно сказать: мой проект использует REST, CDI и Persistence из Jakarta EE; ORM реализует EclipseLink. Spring Data и Jakarta Data сейчас не используются, операции написаны через EntityManager.'), cls='callout')
    return appendix('lab', P('最后对应到你的 Movie 实验','Сопоставим с вашей лабораторной Movie'), text)

def glossary():
    values = [('规范 / 实现','Спецификация / реализация'),('容器 / 受管 Bean','Контейнер / управляемый бин'),
              ('依赖注入 / 作用域','Внедрение зависимостей / область видимости'),('实体 / 属性','Сущность / свойство'),
              ('对象关系映射','Объектно-реляционное отображение'),('持久化上下文','Контекст персистентности'),
              ('受管 / 游离','Управляемый / отсоединённый'),('刷新 / 提交事务','Синхронизация / фиксация транзакции'),
              ('仓储 / 查询派生','Репозиторий / выведение запроса'),('自动配置','Автоконфигурация')]
    text = '<div class="glossary-grid">' + ''.join('<div class="term">' + pair(P(*x)) + '</div>' for x in values) + '</div>'
    return appendix('glossary',P('只保留常用术语','Только основные термины'),text)

def review():
    text = '<div class="guide-steps">'
    for p in [P('第一遍：按九题顺序读直观解释和例子，先不背俄语。','Первый проход: прочитайте простые объяснения и примеры девяти тем, пока не заучивая русский ответ.'),
              P('第二遍：先自己回答章末问题，再展开核对；不懂的回到该章例子。','Второй проход: ответьте на вопросы главы, затем раскройте проверку; при затруднении вернитесь к примеру.'),
              P('第三遍：切到俄语与答辩速记，练习每题短回答。重点是说出它是什么、解决什么、与谁不同。','Третий проход: включите русский язык и краткие ответы. Объясните, что это, какую задачу решает и чем отличается от связанных технологий.')]:
        text += '<div class="guide-step">' + pair(p) + '</div>'
    return appendix('study-path',P('怎样使用这本重构版','Как заниматься по переработанному пособию'),text + '</div>')

def main():
    base.section = lesson
    base.make_map = introduction
    base.make_lab = lab
    base.make_glossary = glossary
    base.make_review = review
    base.main(SECTIONS)
    text = base.OUT.read_text(encoding='utf-8')
    replacements = [
        ('理解技术之间的关系，<br>再用俄语讲清楚。','先听懂每道题，<br>再用俄语说清楚。'),
        ('Поймите связи технологий<br>и объясните их по-русски.','Разберитесь в каждой теме<br>и объясните её по-русски.'),
        ('信息系统实验 · 中俄逐段对应','九题重讲 · 中俄逐段对应'),
        ('Лабораторная по ИС · параллельные тексты','Девять тем заново · параллельные тексты'),
        ('技术关系图','全书思路'),('Карта технологий','Связи тем'),
        ('术语与表达','常用术语'),('Термины и связки','Основные термины'),
        ('复习与纠错','复习步骤'),('Повторение</span>','Порядок повторения</span>'),
        ('is-defense-zh-ru-v1','is-defense-zh-ru-conversation-v2'),
        ('2026-10-26','2026-10-27')
    ]
    for before, after in replacements:
        text = text.replace(before,after)
    extra_css = '''.hero{padding-top:28px;padding-bottom:26px}h1{font-size:clamp(1.8rem,2.5vw,2.5rem)}.reading-route{margin:22px 0;border-top:1px solid var(--line)}.route-step{padding:15px 0;border-bottom:1px solid var(--line)}.source-details{margin:24px 0 8px;font-size:.83rem;color:var(--muted)}.source-details>summary{cursor:pointer;min-height:44px;display:flex;gap:10px;align-items:center}.source-details .sources{margin-top:0;border-top:0}.discussion-source{font-size:.78rem;margin-bottom:0}.sources .lang{line-height:1.7}.content-block h3{font-size:1.08rem} @media(max-width:600px){.hero{padding:22px 20px}h1{font-size:1.8rem}.source-details>summary{display:block;padding:8px 0}.route-step{padding:17px 0}}'''
    text = text.replace('</style>', extra_css + '</style>')
    base.OUT.write_text(text,encoding='utf-8')
    (base.HERE / 'conversation-content.json').write_text(json.dumps(SECTIONS, ensure_ascii=False,indent=2) + '\n',encoding='utf-8')
    print(json.dumps({'revision':'conversation-style','bytes':base.OUT.stat().st_size,'sections':len(SECTIONS),'blocks':sum(len(x['blocks']) for x in SECTIONS),'questions':sum(len(x['questions']) for x in SECTIONS)},ensure_ascii=False))

if __name__ == '__main__':
    main()
