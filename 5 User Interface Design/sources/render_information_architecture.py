"""Render the information architecture report sources and standalone scheme."""
from __future__ import annotations

import re
from pathlib import Path

from reportlab.lib.enums import TA_CENTER
from reportlab.lib.styles import ParagraphStyle
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen import canvas
from reportlab.platypus import Paragraph

from render_user_scenarios import latex

ROOT = Path(__file__).resolve().parents[1]
SOURCE = Path(__file__).with_name("information-architecture-ru.md")
PROJECT = ROOT / "Task/Task3/report"


def render_scheme():
    for name, file in (("IATimes", "times.ttf"), ("IATimes-Bold", "timesbd.ttf")):
        pdfmetrics.registerFont(TTFont(name, str(Path("C:/Windows/Fonts") / file)))
    pdfmetrics.registerFontFamily("IATimes", normal="IATimes", bold="IATimes-Bold")
    target = PROJECT / "figures/information-architecture.pdf"
    target.parent.mkdir(exist_ok=True)
    c = canvas.Canvas(str(target), pagesize=(520, 640), initialFontName="IATimes", initialFontSize=11)
    c.setTitle("AI Knowledge Agent: информационная архитектура")

    def paragraph(text, x, y, w, h, size=11, bold=False):
        style = ParagraphStyle("scheme", fontName="IATimes-Bold" if bold else "IATimes",
                               fontSize=size, leading=size+2.5, alignment=TA_CENTER)
        p = Paragraph(text, style)
        _, ph = p.wrap(w-12, h)
        p.drawOn(c, x+6, y+(h-ph)/2)

    def arrow(x1, y1, x2, y2):
        import math
        c.setLineWidth(0.7)
        c.line(x1,y1,x2,y2)
        a = math.atan2(y2-y1,x2-x1)
        p = c.beginPath()
        p.moveTo(x2,y2)
        p.lineTo(x2-4*math.cos(a-.5),y2-4*math.sin(a-.5))
        p.lineTo(x2-4*math.cos(a+.5),y2-4*math.sin(a+.5))
        p.close()
        c.drawPath(p, fill=1, stroke=0)

    def card(title, rows, x, y):
        w,h = 238,200
        c.setLineWidth(0.7)
        c.rect(x,y,w,h)
        c.line(x,y+h-30,x+w,y+h-30)
        paragraph(title,x,y+h-30,w,30,12,True)
        for i,(indent,text) in enumerate(rows):
            c.setFont("IATimes",11)
            c.drawString(x+12+indent*12,y+h-49-i*17,text)

    paragraph("Информационная структура",10,612,500,23,15,True)
    c.rect(125,570,270,35)
    paragraph("AI Knowledge Agent",125,570,270,35,13,True)
    cards = [
        ("Рабочая область", [(0,"Исходный диалог"),(1,"Источник"),(0,"Обработка"),
          (1,"Ход обработки"),(1,"Результаты анализа"),(1,"План сохранения"),
          (1,"Отчет обработки")],10,350),
        ("История",[(0,"Список обработок"),(0,"Сведения обработки"),(0,"Изменения"),
          (0,"Резервные копии"),(1,"Исходный файл"),(1,"Дата и размер"),
          (1,"Результат восстановления")],272,350),
        ("Граф знаний",[(0,"Заметки"),(1,"Название и путь"),(1,"Теги"),
          (0,"Связи заметок"),(1,"Соседние заметки"),(1,"Вид связи"),
          (1,"Неоднозначные связи")],10,110),
        ("Настройки",[(0,"База знаний"),(0,"Хранилище данных"),(0,"Модели ИИ"),
          (0,"Семантический поиск"),(0,"Правила сохранения"),
          (0,"Обработка текста")],272,110),
    ]
    for args in cards:
        card(*args)
    c.line(260,570,260,295)
    for y in (535,295):
        arrow(260,y,248,y)
        arrow(260,y,272,y)
    paragraph("Рабочая область и история ссылаются на одну обработку.",10,83,500,18,10)
    paragraph("Граф показывает реальные связи между заметками.",10,65,500,18,10)
    paragraph("Основная связь данных",10,44,500,18,10,True)
    labels=["Диалог","Обработка","План","Действие","Заметка"]
    for i,label in enumerate(labels):
        x=18+i*100
        c.rect(x,12,84,25)
        paragraph(label,x,12,84,25,10)
        if i<4:
            arrow(x+84,24.5,x+99,24.5)
    c.showPage()
    c.save()
    return target


def render_table(lines, caption):
    rows=[[v.strip() for v in row.strip().strip("|").split("|")] for row in lines]
    rows=[row for row in rows if not all(re.fullmatch(r":?-+:?",v) for v in row)]
    n=len(rows[0])
    if n==2:
        spec=r"L{34mm}L{\dimexpr\textwidth-4\tabcolsep-34mm\relax}"
    elif rows[0][0]=="Объекты":
        spec=r"L{42mm}L{23mm}L{\dimexpr\textwidth-6\tabcolsep-65mm\relax}"
    else:
        spec=r"L{36mm}L{\dimexpr\textwidth-6\tabcolsep-77mm\relax}L{41mm}"
    header=" & ".join(r"\textbf{"+latex(v)+"}" for v in rows[0])+r" \\"
    body="\n".join(" & ".join(latex(v) for v in row)+r" \\[6pt]" for row in rows[1:])
    return "\n".join([
        r"{\small\setlength{\tabcolsep}{5pt}\renewcommand{\arraystretch}{1.12}",
        r"\begin{longtable}{"+spec+"}",r"\caption{"+latex(caption)+r"}\\",
        r"\toprule",header,r"\midrule\endfirsthead",r"\toprule",header,
        r"\midrule\endhead",r"\bottomrule\endfoot",body,r"\end{longtable}}"])


def render_content():
    lines=SOURCE.read_text(encoding="utf-8").splitlines()
    out=[]
    i=0
    in_list=False
    context="Информационная структура"
    def end_list():
        nonlocal in_list
        if in_list:
            out.append(r"\end{itemize}")
            in_list=False
    while i<len(lines):
        line=lines[i].strip()
        if line.startswith(("# ","**AI Knowledge Agent")):
            i+=1
            continue
        if line=="<!-- architecture-diagram -->":
            out.extend([r"\begin{figure}[H]\centering",
                r"\includegraphics[width=\textwidth]{figures/information-architecture.pdf}",
                r"\caption{Разделы и вложенные группы сведений}",r"\end{figure}"])
        elif line.startswith("```text"):
            end_list()
            out.append(r"{\fontsize{9}{10.7}\selectfont\begin{verbatim}")
            i+=1
            while i<len(lines) and lines[i].strip()!="```":
                out.append(lines[i])
                i+=1
            out.append(r"\end{verbatim}}")
        elif line.startswith("|"):
            end_list()
            table_lines=[]
            while i<len(lines) and lines[i].strip().startswith("|"):
                table_lines.append(lines[i])
                i+=1
            out.append(render_table(table_lines,context))
            continue
        elif line.startswith("## "):
            end_list()
            title=re.sub(r"^\d+\.\s*","",line[3:])
            if title in ("Информационные сущности","Связи и вложенность","Схема структуры"):
                out.append(r"\clearpage")
            context=title
            out.append(r"\section{"+latex(title)+"}")
        elif line.startswith("### "):
            end_list()
            title=re.sub(r"^\d+\.\d+\.\s*","",line[4:])
            if title in ("Текстовая структура","План, материалы и результат"):
                out.append(r"\clearpage")
            context=title
            out.append(r"\subsection{"+latex(title)+"}")
        elif line.startswith("- "):
            if not in_list:
                out.append(r"\begin{itemize}")
                in_list=True
            out.append(r"\item "+latex(line[2:]))
        elif line:
            end_list()
            out.append(latex(line)+"\n")
        else:
            out.append("")
        i+=1
    end_list()
    (PROJECT/"content.tex").write_text("\n".join(out)+"\n",encoding="utf-8")


if __name__=="__main__":
    render_scheme()
    render_content()
    print(PROJECT/"main.tex")
