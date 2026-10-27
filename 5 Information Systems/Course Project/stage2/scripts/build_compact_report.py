"""Build a concise Russian report with two complete vector diagrams and SQL listings."""
from pathlib import Path
from io import BytesIO
import json
import re
import sys

from pypdf import PdfReader, PdfWriter, Transformation
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A3, A2, landscape
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

import draw_integrated_models as diagrams

sys.stdout.reconfigure(encoding="utf-8")
S=Path(__file__).resolve().parents[1]


def tex(value):
    return str(value).replace("&",r"\&").replace("%",r"\%").replace("#",r"\#").replace("_",r"\_\allowbreak{}")


def code(value):
    return r"\texttt{"+tex(value).replace(".",r".\allowbreak{}")+"}"


def table(headers,rows,widths):
    return "\n".join([r"\begin{longtable}{"+"".join("L{"+str(w)+"cm}" for w in widths)+"}",
                      r"\toprule "+" & ".join(headers)+r"\\\midrule\endhead"]+
                     [" & ".join(row)+r"\\" for row in rows]+[r"\bottomrule\end{longtable}"])


def sql_block(source):
    return "\n".join([r"\begin{lstlisting}[style=sql]",source.strip(),r"\end{lstlisting}"])


def readable_sql(source):
    parts=re.split(r"('(?:''|[^'])*')",source)
    return "".join(re.sub(r",(?=\S|$)",", ",part) if i%2==0 else part for i,part in enumerate(parts))


def sheet(source,destination,pagesize,caption,legend,section_title):
    """Place a whole vector diagram on a standard foldout sheet, without rasterizing."""
    width,height=pagesize
    page=PdfReader(str(source)).pages[0]
    sw,sh=float(page.mediabox.width),float(page.mediabox.height)-105
    page.cropbox.upper_right=(sw,sh)
    scale=min((width-72)/sw,(height-155)/sh)
    x=(width-sw*scale)/2
    y=height-78-sh*scale
    writer=PdfWriter()
    output=writer.add_blank_page(width,height)
    output.merge_transformed_page(page,Transformation().scale(scale).translate(x,y))
    if "ReportArial" not in pdfmetrics.getRegisteredFontNames():
        pdfmetrics.registerFont(TTFont("ReportArial","C:/Windows/Fonts/arial.ttf"))
        pdfmetrics.registerFont(TTFont("ReportArialBold","C:/Windows/Fonts/arialbd.ttf"))
    overlay=BytesIO()
    c=canvas.Canvas(overlay,pagesize=pagesize)
    c.setFont("ReportArialBold",18)
    c.drawString(36,height-45,section_title)
    c.setFont("ReportArial",11)
    c.drawString(36,45,caption)
    c.setFont("ReportArial",9)
    c.drawString(36,28,legend)
    c.save();overlay.seek(0)
    output.merge_page(PdfReader(overlay).pages[0])
    with destination.open("wb") as stream:
        writer.write(stream)


def operations_markdown(fragment):
    """Move the former sections 7 and 8 intact, with Markdown tables and code."""
    def inline(value):
        value=value.replace(r"\allowbreak{}","").replace(r"\_","_")
        value=re.sub(r"\\texttt\{([^{}]*)\}",lambda m:"`"+m[1]+"`",value)
        value=re.sub(r"\\textbf\{([^{}]*)\}",lambda m:"**"+m[1]+"**",value)
        return value.replace(r"\par ","<br>").replace(r"\&","&").replace(r"\%","%")
    def convert_table(match):
        headers=[inline(c.strip()) for c in match[1].split(" & ")]
        rows=[row.strip() for row in match[2].split(r"\\") if row.strip()]
        return "\n\n"+"\n".join(["| "+" | ".join(headers)+" |","| "+" | ".join("---" for _ in headers)+" |"]+
                                    ["| "+" | ".join(inline(c.strip()) for c in row.split(" & "))+" |" for row in rows])+"\n\n"
    fragment=re.sub(r"\\begin\{longtable\}.*?\\toprule (.*?)\\\\\\midrule\\endhead\s*(.*?)\\bottomrule\\end\{longtable\}",convert_table,fragment,flags=re.S)
    fragment=re.sub(r"\\begin\{lstlisting\}\[style=commands\]\s*(.*?)\\end\{lstlisting\}",lambda m:"\n```bash\n"+m[1].strip()+"\n```\n",fragment,flags=re.S)
    fragment=fragment.replace(r"\section{Скрипты и воспроизведение}","## 7. Скрипты и воспроизведение")
    fragment=fragment.replace(r"\section{Результаты проверки}","## 8. Результаты проверки")
    result="# Скрипты, воспроизведение и проверка\n\nМатериалы бывших разделов 7 и 8, вынесенные из PDF-отчёта.\n\n"+inline(fragment).strip()+"\n"
    assert r"\begin{" not in result and r"\end{" not in result
    return re.sub(r"\n{3,}","\n\n",result)


def revise_report(full):
    start=full.index(r"\section{Скрипты и воспроизведение}")
    end=full.index(r"\section{Заключение}")
    (S/"OPERATIONS_AND_VERIFICATION.md").write_text(operations_markdown(full[start:end]),encoding="utf-8")
    full=full[:start]+full[end:]
    start=full.index(r"\section{ER-модель}")
    end=full.index(r"\section{Целостность и доступ}")
    figures=r'''\clearpage
\includepdf[pages=1,fitpaper=true,pagecommand={\thispagestyle{empty}\refstepcounter{section}\addcontentsline{toc}{section}{\protect\numberline{\thesection}ER-модель}}]{figures/er_model_a3.pdf}
\includepdf[pages=1,fitpaper=true,pagecommand={\thispagestyle{empty}\refstepcounter{section}\addcontentsline{toc}{section}{\protect\numberline{\thesection}Даталогическая модель}}]{figures/logical_model_a2.pdf}
'''
    full=full[:start]+figures+full[end:]
    # The full statements below replace the former isolated master_service example.
    start=full.index("Основные фрагменты DDL:")
    end=full.index("Триггеры защищают условия",start)
    full=full[:start]+full[end:]
    ddl=(S/"sql/01_tables.sql").read_text("utf-8")
    tables=re.findall(r"CREATE TABLE beauty\.([a-z_]+) \(.*?\n\);",ddl,re.S)
    statements=re.findall(r"CREATE TABLE beauty\.[a-z_]+ \(.*?\n\);",ddl,re.S)
    assert len(statements)==14 and set(tables)==set(diagrams.TABLES)
    setup=ddl[:ddl.index("CREATE TABLE")].strip()
    chunks=[r"\subsection{Создание таблиц}",sql_block(setup)]
    for name,statement in zip(tables,statements):
        chunks += [r"\par\medskip\noindent\begin{minipage}{\linewidth}",
                   r"\subsubsection*{"+tex(diagrams.NAMES[name])+" ("+code(name)+")}",
                   sql_block(readable_sql(statement)),r"\end{minipage}\par\medskip"]
    chunks.append(r"\subsection{Контроль бизнес-правил}")
    marker=r"\section{Целостность и доступ}"
    full=full.replace(marker,marker+"\n"+"\n".join(chunks),1)
    full=full.replace("UQ","UNIQUE")
    full=full.replace("Все 79 проверок пройдены; полезность индексов подтверждена планами запросов. ","")
    full=full.replace(r"\section{Заключение}",r"\par\begin{samepage}\section{Заключение}")
    full=full.replace(r"\end{document}",r"\par\end{samepage}\end{document}")
    return full


PREAMBLE=r'''\documentclass[11pt,a4paper]{article}
\usepackage{fontspec}
\IfFontExistsTF{Times New Roman}{\setmainfont{Times New Roman}\newfontfamily\cyrillicfont{Times New Roman}}{\setmainfont{CMU Serif}\newfontfamily\cyrillicfont{CMU Serif}}
\IfFontExistsTF{Arial}{\setsansfont{Arial}\newfontfamily\cyrillicfontsf{Arial}}{\setsansfont{CMU Sans Serif}\newfontfamily\cyrillicfontsf{CMU Sans Serif}}
\IfFontExistsTF{Courier New}{\setmonofont{Courier New}\newfontfamily\cyrillicfonttt{Courier New}}{\setmonofont{CMU Typewriter Text}\newfontfamily\cyrillicfonttt{CMU Typewriter Text}}
\usepackage{polyglossia}\setdefaultlanguage{russian}\setotherlanguage{english}
\usepackage[left=20mm,right=20mm,top=20mm,bottom=25mm]{geometry}
\usepackage{amsmath,array,longtable,booktabs,enumitem,setspace,xcolor,listings,pdfpages,etoolbox,hyperref}
\hypersetup{unicode=true,colorlinks=true,linkcolor=black,urlcolor=blue,pdftitle={Курсовая работа. Этап 2. База данных салонов красоты},pdfauthor={Чэнь Хаолинь, Павлов Эдгар}}
\setstretch{1.12}\setlength{\parindent}{1.25cm}\setlength{\parskip}{2pt}
\widowpenalty=10000\clubpenalty=10000
\setlength{\emergencystretch}{3em}\setlist{nosep,leftmargin=*,before=\raggedright}
\newcolumntype{L}[1]{>{\raggedright\arraybackslash}p{#1}}
\renewcommand{\arraystretch}{1.12}
\AtBeginEnvironment{longtable}{\small\setstretch{1.02}}
\definecolor{SQLKeyword}{HTML}{173F78}
\definecolor{SQLType}{HTML}{6A2B8A}
\definecolor{SQLString}{HTML}{25613B}
\definecolor{SQLComment}{HTML}{66716E}
\definecolor{CodeBackground}{HTML}{F5F7FA}
\lstdefinestyle{sql}{language=SQL,basicstyle=\ttfamily\footnotesize,
  keywordstyle=\bfseries\color{SQLKeyword},
  keywordstyle=[2]\bfseries\color{SQLType},
  stringstyle=\color{SQLString},commentstyle=\itshape\color{SQLComment},
  morekeywords={GENERATED,ALWAYS,IDENTITY,STORED,INCLUDE,EXCLUDE,USING,WITH,
    PERFORM,RAISE,EXCEPTION,DECLARE,RETURN,QUERY,LANGUAGE,PLPGSQL,SQL,
    SECURITY,DEFINER,RETURNS,ELSIF,END,IF,THEN,IS,DISTINCT,FROM,ERRCODE},
  morekeywords=[2]{bigint,integer,smallint,text,numeric,boolean,timestamp,time,date,tsrange,void},
  sensitive=false,backgroundcolor=\color{CodeBackground},frame=single,
  rulecolor=\color{black!15},framerule=0.3pt,xleftmargin=6pt,xrightmargin=6pt,
  framexleftmargin=4pt,framexrightmargin=4pt,aboveskip=6pt,belowskip=7pt,
  columns=fullflexible,keepspaces=true,showstringspaces=false,
  breaklines=true,breakatwhitespace=true,tabsize=2}
\lstdefinestyle{commands}{style=sql,language=bash,keywordstyle=\color{SQLKeyword},morekeywords={psql},basicstyle=\ttfamily\footnotesize}
\setcounter{tocdepth}{1}
\begin{document}
\begin{titlepage}\centering
Федеральное государственное автономное\\образовательное учреждение высшего образования\\
\textbf{«Национальный исследовательский университет ИТМО»}\vfill
Информационные системы\\[0.5\baselineskip]\textbf{Курсовая работа. Этап 2}\\[0.5\baselineskip]
Информационная система поиска салонов красоты\\и онлайн-записи на услуги\\[0.5\baselineskip]
\textbf{Проектирование и реализация базы данных PostgreSQL}\vfill
\begin{flushright}Выполнили:\\Чэнь Хаолинь P3216 407960\\Павлов Эдгар P3316 409297\\Преподаватель:\\Коновалов Арсений Антонович\end{flushright}
\vspace{4\baselineskip}г. Санкт-Петербург, 2026\end{titlepage}
\setcounter{page}{2}\tableofcontents\clearpage
'''


def main():
    diagrams.main()
    metadata=json.loads((S/"verification/schema_metadata.json").read_text("utf-8"))
    tests=json.loads((S/"verification/test_results.json").read_text("utf-8"))
    counts=json.loads((S/"verification/seed_counts.json").read_text("utf-8"))
    plans=json.loads((S/"verification/explain_plans.json").read_text("utf-8"))
    assert tests["all_passed"] and len(metadata["tables"])==14
    figs=S/"report/figures"
    sheet(figs/"er_model.pdf",figs/"er_model_a3.pdf",landscape(A3),
          "Рисунок 1. Полная ER-модель: 10 сущностей и прямая связь M:N.",
          "","2. ER-модель")
    native=PdfReader(str(figs/"logical_model.pdf")).pages[0]
    logical_size=landscape(A2) if float(native.mediabox.width)>float(native.mediabox.height) else A2
    sheet(figs/"logical_model.pdf",figs/"logical_model_a2.pdf",logical_size,
          "Рисунок 2. Полная даталогическая модель PostgreSQL: 14 таблиц и 25 внешних ключей.",
          "","3. Даталогическая модель")
    model={"entity_count":10,"entities":[{"name":n,"russian_name":diagrams.NAMES[n],"attributes":diagrams.CONCEPT_ATTRS[n]} for n in diagrams.CORE],
           "many_to_many":{"left":"master","right":"salon_service","association_table":"master_service","attributes":["is_active"]},
           "physical_table_count":14,"attribute_relations":["salon_photo","master_photo"],"technical_relations":["master_invitation"]}
    (S/"report/conceptual_model.json").write_text(json.dumps(model,ensure_ascii=False,indent=2),encoding="utf-8")
    parts=[PREAMBLE,r'''\section{Задание и границы системы}
Цель этапа --- спроектировать и реализовать базу данных платформы салонов красоты. Требуется:
\begin{enumerate}
\item Построить ER-модель не менее чем из десяти сущностей со связью M:N.
\item Согласовать модель с преподавателем и получить даталогическую модель.
\item Реализовать её в PostgreSQL, обеспечить целостность DDL и триггерами.
\item Подготовить скрипты жизненного цикла базы, демоданные и бизнес-операции PL/pgSQL.
\item Обосновать индексы по прецедентам и представить результаты проверки.
\end{enumerate}
Платформа обслуживает несколько салонов одного города. У пользователя одна роль: клиент, мастер, владелец или администратор. Владелец управляет одним салоном, мастер работает в одном салоне. Запись содержит одну услугу и одного мастера. Денежные значения заданы в рублях, локальное время --- Europe/Moscow. Горизонт записи составляет 30 календарных дней, включая текущий; начала выбираются с шагом 15 минут, длительность услуги может быть произвольным положительным числом минут.

\section{ER-модель}
Концептуальная модель содержит \textbf{10 сущностей}: пользователь, район, салон, вид услуги, услуга салона, мастер, рабочий интервал, запись, отзыв и решение модерации. Полная схема приведена на рисунке~1; каждый объект показан один раз.

Связь «мастер выполняет услугу салона» имеет кратность \textbf{M:N} и атрибут активности назначения. Например, два мастера выполняют маникюр, а один из них также выполняет педикюр: это три разрешённые пары. Сама пара не вводится в ER-граф как отдельный бизнес-объект; её таблица появляется при переходе к отношениям.

Фотографии интерьера и работ мастера --- составные многозначные атрибуты: путь, подпись, порядок и видимость. Автор отзыва и его конкретные цели выводятся через выполненную запись. Решение модерации имеет обязательного администратора и ровно одну цель: пользователя, салон, мастера или отзыв. Путь фотографии уточняет элемент атрибута выбранного салона или мастера.

\textbf{Согласование:} модель подготовлена к обсуждению; фактическое подтверждение преподавателя пока не зафиксировано. Даталогическая модель далее представляет вариант для согласования.
\clearpage
\includepdf[pages=1,fitpaper=true,pagecommand={\thispagestyle{empty}}]{figures/er_model_a3.pdf}
\section{Даталогическая модель и нормализация}
Полная схема на рисунке~2 содержит \textbf{14 таблиц}: десять основных отношений, таблицу связи M:N, две таблицы элементов фотоатрибутов и техническую таблицу приглашений.
''',table(["Преобразование","Результат и ключ"],[
        ["Бизнес-сущности",r"По одной таблице с идентификатором; исключение для многозначных атрибутов указано ниже."],
        ["Связь M:N",code("master_service")+r": PK (master\_id, salon\_service\_id), активность пары."],
        ["Фотографии",code("salon_photo")+", "+code("master_photo")+r": составные PK (родитель, file\_path)."],
        ["Одноразовое приглашение",code("master_invitation")+r": invitation\_id; уникальный хеш, срок, использование и отзыв токена."],
    ],[4.1,12.0]),r'''
Запись ссылается составным FK на разрешённую пару «мастер--услуга». Триггер дополнительно проверяет принадлежность обоих объектов одному салону. Отзыв имеет FK на запись и уникальную пару (appointment\_id, target\_type): не более одного отзыва о салоне и одного о мастере. Имя мастера хранится в пользователе и не дублируется в профиле.

Для модерации используются четыре целевых FK с XOR. Два дополнительных составных FK (target\_salon\_id, photo\_path) и (target\_master\_id, photo\_path) проверяют существование конкретного фотоэлемента. Все внешние ключи используют ON DELETE RESTRICT: исторически значимые объекты архивируются.

Разделение фотоэлементов устраняет повторяющиеся группы и обеспечивает 1НФ. Атрибуты основных отношений зависят от их ключей; связи и сведения о пользователе не дублируются, что соответствует 3НФ. Снимки названия, цены и длительности относятся к факту подтверждения записи и сохраняют историю. Окончание и диапазон времени --- контролируемые generated-столбцы. Рейтинги и свободные времена вычисляются запросами.

На рисунке~2 ключи вынесены в отдельную левую колонку; типы справа выделены полужирным. PK --- первичный ключ, FK --- внешний, UQ --- уникальность, NN --- NOT NULL, G --- вычисляемый столбец. Повтор F13 у двух полей означает один составной FK, а не две независимые ссылки.
\clearpage
\includepdf[pages=1,fitpaper=true,pagecommand={\thispagestyle{empty}}]{figures/logical_model_a2.pdf}
\section{Целостность и доступ}
''',table(["Инвариант","Реализация"],[
        ["Идентичность и принадлежность","PK, FK, UQ; неизменность роли и владельческих связей; проверка ролей и одного салона триггерами."],
        ["Нет пересечения времени","GiST EXCLUDE по мастеру и диапазону для рабочих интервалов и неотменённых записей. Полуоткрытые интервалы допускают соседние посещения."],
        ["Запись допустима","Триггер проверяет публикацию, активность, разрешённую пару, горизонт, шаг начала и вхождение всей услуги в один рабочий интервал."],
        ["История и статусы","Снимки неизменны; отмена до начала, результат после окончания. Сокращение графика и деактивация не нарушают ещё не завершённые подтверждённые записи."],
        ["Отзывы и модерация","Только COMPLETED, рейтинг 1--5, UQ по типу цели; неизменяемый текст и аудит. CHECK XOR и составные FK для фото."],
        ["Фото и приглашения","До 20 неархивных фото; JPEG/PNG до 5 МБ; скрытые фото учитываются в квоте. Уникальный одноразовый токен, срок и взаимное исключение использования и отзыва."],
    ],[4.1,12.0]),r"Основные фрагменты DDL:",sql_block('''CREATE TABLE beauty.master_service (
  master_id bigint NOT NULL
    REFERENCES beauty.master ON DELETE RESTRICT,
  salon_service_id bigint NOT NULL
    REFERENCES beauty.salon_service ON DELETE RESTRICT,
  is_active boolean NOT NULL DEFAULT true,
  PRIMARY KEY (master_id, salon_service_id)
);

-- Constraint inside beauty.appointment:
CONSTRAINT ex_appointment_overlap
  EXCLUDE USING gist (master_id WITH =, slot WITH &&)
  WHERE (status <> 'CANCELLED')'''),r'''
Триггеры защищают условия, зависящие от других строк и времени. Например, контроль права на отзыв включает следующую проверку:
''',sql_block('''IF NOT EXISTS (
  SELECT FROM beauty.appointment
  WHERE appointment_id = NEW.appointment_id
    AND status = 'COMPLETED'
) THEN
  RAISE EXCEPTION 'Review requires a completed visit'
    USING ERRCODE = '23514';
END IF;'''),r'''
Все бизнес-записи получают единый транзакционный advisory lock до чтения изменяемых условий и блокировки строк. Допускается READ COMMITTED; иной уровень явно отклоняется. Это устраняет проверяемые гонки между записью, графиком, каталогом и токенами, но последовательно выполняет изменения всей платформы. Производительность при 20 параллельных клиентах не подтверждена; для масштабирования требуется более мелкая схема блокировок.

Backend получает только EXECUTE на API; актор берётся из аутентифицированной сессии. Проверку файлов выполняет файловый сервис.

\section{Критические функции и процедуры}
Реализованы 22 бизнес-операции. Пишущие операции используют PL/pgSQL; выбор свободного времени выражен SQL-запросом. Два view рассчитывают независимые рейтинги салона и мастера только по опубликованным отзывам.
''',table(["Прецеденты","API и назначение"],[
        ["П1",code("register_user")+", "+code("authenticate")+": регистрация и пароль; "+code("accept_invitation")+": активация мастера."],
        ["П2--П4, П12",code("search_salons")+", "+code("available_slots")+", "+code("book_appointment")+": фильтры, допустимые начала и подтверждение условий."],
        ["П5, П9, П10",code("appointment_journal")+", "+code("cancel_appointment")+", "+code("mark_visit")+": личная история, отмена и результат посещения."],
        ["П6, П7, П11",code("add_review")+", "+code("moderate")+", "+code("create_salon")+", "+code("resubmit_salon")+": отзывы, решения и публикация."],
        ["П8, П9",code("invite_master")+", "+code("reissue_invitation")+", "+code("set_master_service")+", "+code("save_work_interval")+", "+code("delete_work_interval")+", "+code("save_service")+", "+code("save_master_profile")+", "+code("put_photo")+", "+code("archive_photo")+": управление своим салоном и профилем."],
    ],[2.8,13.3]),r'''
При подтверждении записи сервер повторно проверяет цену и длительность: изменение каталога требует нового подтверждения клиента. После INSERT триггер проверяет доступность и сохраняет актуальные снимки. Полный пример критической функции:
''',sql_block('''CREATE FUNCTION beauty.book_appointment(
  p_client bigint, p_master bigint, p_service bigint,
  p_start timestamp, p_expected_price numeric,
  p_expected_duration integer
) RETURNS bigint
LANGUAGE plpgsql SECURITY DEFINER
SET search_path = pg_catalog, beauty, pg_temp AS $$
DECLARE s beauty.salon_service; id bigint;
BEGIN
  PERFORM beauty.lock_writes();
  PERFORM beauty.require_actor(p_client, ARRAY['CLIENT']);
  SELECT * INTO s FROM beauty.salon_service
    WHERE salon_service_id = p_service;
  IF NOT FOUND THEN RAISE EXCEPTION 'Service does not exist'
    USING ERRCODE = '23503'; END IF;
  IF s.price IS DISTINCT FROM p_expected_price OR
     s.duration_minutes IS DISTINCT FROM p_expected_duration THEN
    RAISE EXCEPTION 'Service terms changed; confirm again'
      USING ERRCODE = '22023'; END IF;
  INSERT INTO beauty.appointment (
    client_user_id, master_id, salon_service_id, start_at,
    service_name_snapshot, price_snapshot, duration_snapshot
  ) VALUES (
    p_client, p_master, p_service, p_start,
    s.name, s.price, s.duration_minutes
  ) RETURNING appointment_id INTO id;
  RETURN id;
END $$;'''),r'''
{\raggedright mark\_\allowbreak{}visit фиксирует COMPLETED или NO\_SHOW после окончания посещения. cancel\_\allowbreak{}appointment идемпотентна и сохраняет автора отмены. add\_\allowbreak{}review допускает отзыв клиента о выполненной записи. При активации приглашения проверяются срок и однократность токена.\par}

\section{Индексы по прецедентам}
В схеме 43 индекса: 23 обеспечивают PK/UQ/EXCLUDE, 19 созданы для запросов и один частичный уникальный индекс защищает открытые приглашения. Индексы ограничений не дублируются.
''']
    index_rows=[
        ("idx_salon_public_district","П2","Район и идентификатор в опубликованном каталоге."),
        ("idx_salon_public_coordinates","П2","Отбор прямоугольника карты; радиус вычисляется для кандидатов."),
        ("idx_service_salon_type_price","П2, П3","Тип и цена услуги внутри выбранного салона."),
        ("idx_service_type_price","П2","Поиск салонов по типу и диапазону цены одной услуги."),
        ("idx_master_salon","П3, П8","Активные мастера салона."),
        ("idx_assignment_service","П3, П4","Мастера услуги; обратный порядок к PK связи M:N."),
        ("idx_work_master_date","П4, П9, П12","График мастера в нужную дату; INCLUDE окончания."),
        ("idx_appointment_client_time","П5","Последние записи клиента без полной сортировки."),
        ("idx_appointment_master_time","П9, П10","Журнал мастера за дату и история посещений."),
        ("idx_appointment_service_future","П8","Проверка защиты услуги с будущими подтверждёнными записями."),
        ("idx_appointment_busy","П4, П12","GiST-поиск пересекающихся подтверждённых интервалов."),
        ("idx_review_published_target","П3, П6, П11","Опубликованные оценки нужного типа цели."),
        ("idx_salon_photo_visible / idx_master_photo_visible","П3","Видимые фото родителя в порядке показа."),
        ("idx_moderation_user / idx_moderation_salon / idx_moderation_master / idx_moderation_review","П7, П11","История решений по конкретному объекту; частичные индексы без NULL."),
        ("idx_invitation_master_history","П1, П8","История и повторная выдача приглашений мастера."),
        ("uq_invitation_open","П1","Не более одного неиспользованного, неотозванного токена."),
    ]
    parts.append(table(["Индекс","Прецедент","Польза"],[[r"\par ".join(code(x.strip()) for x in name.split(" / ")),use,why] for name,use,why in index_rows],[6.4,2.0,7.3]))
    parts += [r"Примеры индексов для истории клиента и поиска занятых слотов:",sql_block('''CREATE INDEX idx_appointment_client_time
  ON beauty.appointment (client_user_id, start_at DESC)
  INCLUDE (status, master_id, salon_service_id);

CREATE INDEX idx_appointment_busy
  ON beauty.appointment USING gist (master_id, slot)
  WHERE status = 'CONFIRMED';'''),r'''
\section{Скрипты и воспроизведение}
Нужны PostgreSQL, psql, права владельца схемы и расширения btree\_gist, pgcrypto. Проверенная версия --- PostgreSQL 17.4. При работе в выданной преподавателем пустой базе шаг CREATE DATABASE пропускается.
''',table(["Файлы","Назначение"],[
        [code("sql/00_create_database.sql")+", "+code("sql/99_drop_database.sql"),"Создание явно указанной UTF-8 базы и удаление без FORCE."],
        [code("sql/01_tables.sql")+", "+code("sql/02_seed.sql"),"Таблицы, декларативные ограничения и синтетические данные."],
        [code("sql/03_integrity.sql")+", "+code("sql/04_routines.sql"),"Триггеры, помощники, бизнес-функции, процедуры и view."],
        [code("sql/05_indexes.sql")+", "+code("sql/06_grant_backend.sql"),"Индексы запросов и EXECUTE для существующей серверной роли."],
        [code("sql/install.sql"),"Атомарная установка, необязательные демоданные и ANALYZE."],
        [code("scripts/CreateDatabase.ps1")+", "+code("scripts/DropDatabase.ps1")+", "+code("scripts/TestDatabase.ps1"),"Локальные команды создания, удаления и изолированной проверки."],
    ],[8.1,8.0]),r"Запуск из каталога второго этапа:",r'''\begin{lstlisting}[style=commands]
psql -h HOST -U USER -d postgres \
  -v db_name=beauty_course -f sql/00_create_database.sql
psql -h HOST -U USER -d beauty_course \
  -v with_demo_data=true -f sql/install.sql
psql -h HOST -U OWNER -d beauty_course \
  -v backend_role=SERVER_ROLE -f sql/06_grant_backend.sql
psql -h HOST -U USER -d postgres \
  -v db_name=beauty_course -f sql/99_drop_database.sql
\end{lstlisting}
Исторические демоданные загружаются после DDL, до установки бизнес-триггеров, в одной транзакции install. Декларативные ограничения действуют при загрузке; дополнительные проверки подтверждают согласованность истории. Этот путь предназначен для новой демонстрационной базы. Без флага демоданных создаётся пустая рабочая схема. Удаление не завершает чужие сеансы.

\section{Результаты проверки}
''',f"Выполнено \\textbf{{{tests['passed']} из {tests['total']} проверок}}; все завершились успешно. Создано {len(metadata['tables'])} таблиц, {len(metadata['triggers'])} пользовательских триггера, {len(metadata['indexes'])} индекса. Проверены установка с демоданными и без них, создание и удаление отдельной базы, допустимые и запрещённые сценарии и права backend.",
    table(["Данные / проверка","Результат"],[
        ["Нагрузка тестовых данных",f"{counts['salon']} салонов, {counts['master']} профиль мастера, {counts['salon_service']} услуг; {counts['work_interval']} рабочих интервалов, {counts['appointment']} записей, {counts['review']} отзывов."],
        ["Время и каталог","Отклонены пересечение, перерыв, прошедшая дата, неверный шаг, чужая услуга и изменение занятых условий; соседние записи разрешены."],
        ["Права и история","Отклонены чужая отмена, ранний результат, изменение конечного статуса, удаление истории, повтор отзыва, прямой доступ к таблицам."],
        ["Модерация и приглашения","Проверены XOR, ссылки на фото, квота, скрытие и рейтинги, сроки, отзыв и одноразовое использование токена."],
        ["Четыре конкурентных сценария","Повтор одной записи; запись против сокращения графика; одинаковый отзыв; двойная активация приглашения."],
    ],[4.2,11.9]),r'''
В конкурентных проверках использованы пары реальных сеансов: первая транзакция удерживалась две секунды, вторая ожидала блокировку более секунды. Вторая запись в тот же слот отклонялась с 23P01, сокращение занятого графика --- с 23514, повтор отзыва --- с 23505, повтор токена --- с 22023. Проверка нагрузки всей платформы не проводилась.

EXPLAIN (ANALYZE, BUFFERS, FORMAT JSON) выполнен без отключения последовательного сканирования:
''']
    labels={"client_history":"История клиента","master_day":"Журнал мастера","working_date":"График на дату","busy_overlap":"Пересечение слота","service_and_price":"Тип услуги и цена"}
    def indexes(plan):
        return ([plan["Index Name"]] if "Index Name" in plan else [])+sum([indexes(x) for x in plan.get("Plans",[])],[])
    parts += [table(["Запрос","Выбранные индексы","мс"],[[labels[k],r"\par ".join(code(x) for x in indexes(v["explain"][0]["Plan"])),str(v["explain"][0]["Execution Time"])] for k,v in plans.items()],[4.0,9.8,1.8]),r'''
Планы подтверждают использование индексов в пяти характерных запросах. Время относится к локальным SQL-вызовам и не включает сеть, HTTP или параллельную нагрузку. Геометрическая проверка двух полных схем подтвердила отсутствие повторных сущностей, перекрытий и проходов через рамки; три и два пересечения соответственно обозначены дугами.

\section{Заключение}
Построены ER-модель из десяти сущностей с M:N и даталогическая модель из четырнадцати отношений. Реализованы PostgreSQL DDL, триггеры, бизнес-операции PL/pgSQL, индексы и скрипты жизненного цикла. Все 79 проверок пройдены; полезность индексов подтверждена планами запросов. Материалы готовы к обсуждению с преподавателем; фактическое согласование ER-модели остаётся обязательным внешним шагом.
\end{document}
''']
    full=revise_report("\n\n".join(parts))
    (S/"report/stage2_report.tex").write_text(full,encoding="utf-8")
    print("Report ready: sections 2/3 are diagrams only; 14 complete CREATE TABLE statements; former sections 7/8 moved to Markdown.")


if __name__=="__main__":
    main()
