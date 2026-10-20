"""Generate report sources. Compile main.tex with XeLaTeX or LuaLaTeX."""
from __future__ import annotations

import re
from pathlib import Path

from reportlab.lib.enums import TA_CENTER
from reportlab.lib.styles import ParagraphStyle
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen import canvas
from reportlab.platypus import Paragraph

ROOT = Path(__file__).resolve().parents[1]
SOURCE = Path(__file__).with_name("user-scenarios-ru.md")
PROJECT = ROOT / "Task/Task2/report"


def latex(text: str) -> str:
    saved = []
    def save(match):
        saved.append(r"\code{" + match[1] + "}")
        return f"ZZTOKEN{len(saved)-1}ZZ"
    text = re.sub(r"`([^`]+)`", save, text)
    special = {"\\": r"\textbackslash{}", "&": r"\&", "%": r"\%", "$": r"\$",
               "#": r"\#", "_": r"\_", "{": r"\{", "}": r"\}",
               "~": r"\textasciitilde{}", "^": r"\textasciicircum{}"}
    text = "".join(special.get(char, char) for char in text)
    text = re.sub(r"\*\*([^*]+)\*\*", r"\\textbf{\1}", text)
    for i, value in enumerate(saved):
        text = text.replace(f"ZZTOKEN{i}ZZ", value)
    return text


def table(lines: list[str]) -> str:
    rows = [[c.strip() for c in s.strip().strip("|").split("|")] for s in lines]
    rows = [r for r in rows if not all(re.fullmatch(r":?-+:?", c) for c in r)]
    head = " & ".join(r"\textbf{" + latex(c) + "}" for c in rows[0]) + r" \\"
    body = "\n".join(" & ".join(latex(c) for c in row) + r" \\[5pt]" for row in rows[1:])
    if rows[0][0] == "Шаг":
        scenario = "S1" if "RAG" in rows[1][-1] else "S2"
        return "\n".join([
            r"{\small\setlength{\tabcolsep}{5pt}\renewcommand{\arraystretch}{1.15}",
            r"\begin{longtable}{L{9mm}L{26mm}L{\dimexpr\textwidth-6\tabcolsep-35mm\relax}}",
            r"\caption{Обмен информацией в сценарии " + scenario + r"}\\",
            r"\toprule", head, r"\midrule\endfirsthead", r"\toprule", head,
            r"\midrule\endhead", r"\bottomrule\endfoot", body, r"\end{longtable}}"])
    return "\n".join([
        r"\begin{table}[H]\centering\small",
        r"\caption{Сравнение способов обработки задачи}",
        r"\setlength{\tabcolsep}{4pt}\renewcommand{\arraystretch}{1.1}\setlength{\abovecaptionskip}{5pt}",
        r"\begin{tabularx}{\textwidth}{L{0.13\textwidth}YYY}",
        r"\toprule", head, r"\midrule", body.replace(r"\\[5pt]", r"\\[2pt]"),
        r"\bottomrule\end{tabularx}\end{table}"])


def render_content() -> None:
    lines = SOURCE.read_text(encoding="utf-8").splitlines()
    output, i, in_list, branches = [], 0, False, False
    def end_list():
        nonlocal in_list
        if in_list:
            output.append(r"\end{itemize}")
            in_list = False
    while i < len(lines):
        line = lines[i].strip()
        if line.startswith(("# ", "**AI Knowledge Agent", "Практическая работа:", "<!--")):
            i += 1
            continue
        if line.startswith("```mermaid"):
            end_list()
            i += 1
            while i < len(lines) and lines[i].strip() != "```":
                i += 1
            output.extend([r"\begin{figure}[H]\centering",
                           r"\includegraphics[width=\textwidth]{figures/information-flow.pdf}",
                           r"\caption{Обмен информацией между пользователем и системой}",
                           r"\end{figure}"])
        elif line.startswith("|"):
            end_list()
            data = []
            while i < len(lines) and lines[i].strip().startswith("|"):
                data.append(lines[i])
                i += 1
            output.append(table(data))
            continue
        elif line.startswith("## "):
            end_list()
            title = line[3:]
            plain = re.sub(r"^\d+\.\s*", "", title)
            branches = plain.startswith("Альтернативные")
            if plain.startswith(("User Story", "Сценарий", "Альтернативные", "Блок-схема", "Агентная")):
                output.append(r"\clearpage")
            output.append(r"\section{" + latex(plain) + "}")
        elif line.startswith("### "):
            end_list()
            output.append("\\" + ("paragraph" if branches else "subsection") + "{" + latex(line[4:]) + "}")
        elif line.startswith("- "):
            if not in_list:
                output.append(r"\begin{itemize}")
                in_list = True
            output.append(r"\item " + latex(line[2:]))
        elif line:
            end_list()
            output.append(latex(line) + "\n")
            if re.fullmatch(r"\*\*US-.*\*\*", line):
                output.append(r"\nopagebreak[4]")
        else:
            output.append("")
        i += 1
    end_list()
    (PROJECT / "content.tex").write_text("\n".join(output) + "\n", encoding="utf-8")


def render_flowchart() -> None:
    for name, file in (("TimesRU", "times.ttf"), ("TimesRU-Bold", "timesbd.ttf")):
        pdfmetrics.registerFont(TTFont(name, str(Path("C:/Windows/Fonts") / file)))
    pdfmetrics.registerFontFamily("TimesRU", normal="TimesRU", bold="TimesRU-Bold")
    figure = PROJECT / "figures/information-flow.pdf"
    figure.parent.mkdir(exist_ok=True)
    c = canvas.Canvas(str(figure), pagesize=(480, 460), initialFontName="TimesRU", initialFontSize=10)
    c.setTitle("Обмен информацией")
    def paragraph(text, x, y, width, height, size=10):
        style = ParagraphStyle("flow", fontName="TimesRU", fontSize=size, leading=size+2, alignment=TA_CENTER)
        p = Paragraph(text, style)
        _, ph = p.wrap(width-12, height)
        p.drawOn(c, x+6, y+(height-ph)/2)
    def box(text, x, y, width, height):
        c.setLineWidth(0.7)
        c.rect(x, y, width, height)
        paragraph(text, x, y, width, height)
    def diamond(text, cy):
        path = c.beginPath()
        path.moveTo(265, cy+30)
        path.lineTo(375, cy)
        path.lineTo(265, cy-30)
        path.lineTo(155, cy)
        path.close()
        c.drawPath(path)
        paragraph(text, 186, cy-23, 158, 46, 9.4)
    def arrow(x1, y1, x2, y2, label=""):
        import math
        c.setLineWidth(0.7)
        c.line(x1, y1, x2, y2)
        a = math.atan2(y2-y1, x2-x1)
        path = c.beginPath()
        path.moveTo(x2, y2)
        path.lineTo(x2-4*math.cos(a-0.5), y2-4*math.sin(a-0.5))
        path.lineTo(x2-4*math.cos(a+0.5), y2-4*math.sin(a+0.5))
        path.close()
        c.drawPath(path, fill=1, stroke=0)
        if label:
            c.setFont("TimesRU", 9)
            if x1 == x2:
                c.drawString(x1+5, (y1+y2)/2-2, label)
            else:
                c.drawCentredString((x1+x2)/2, y1+7, label)
    box("<b>Пользователь:</b> передает диалог для организации знаний", 155, 412, 220, 43)
    diamond("<b>Система сообщает:</b> есть знания для сохранения?", 360)
    box("<b>Система:</b> сообщает причину пропуска. Сохранения нет.", 0, 329, 134, 62)
    box("<b>Система:</b> сообщает знания, структуру заметок, место сохранения и причины плана", 155, 251, 220, 65)
    diamond("<b>Пользователь:</b> разрешает сохранение по плану?", 195)
    box("<b>Система:</b> подтверждает отказ. Изменения не выполнены.", 396, 154, 84, 82)
    box("<b>Система:</b> сохраняет знания и сообщает фактический результат проверки", 155, 79, 220, 67)
    box("<b>Пользователь:</b> получает заметки и сведения о завершении либо об ошибке", 155, 0, 220, 54)
    for args in [(265,412,265,390), (155,360,134,360,"Нет"), (265,330,265,316,"Да"),
                 (265,251,265,225), (375,195,396,195,"Нет"), (265,165,265,146,"Да"),
                 (265,79,265,54)]:
        arrow(*args)
    c.showPage()
    c.save()


if __name__ == "__main__":
    render_content()
    render_flowchart()
    print(PROJECT / "main.tex")
