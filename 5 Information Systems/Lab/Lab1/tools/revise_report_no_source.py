"""Apply the user's report-only scope: no code listings, a GitHub placeholder."""
from pathlib import Path
import re

base = Path(__file__).resolve().parents[1]
report = base / 'report'

p = report / 'report.tex'
text = p.read_text(encoding='utf-8')
text = text.replace(',fvextra,xurl', ',xurl')
text = re.sub(r'^\\fvset\{.*\}\n', '', text, flags=re.M)
text = text.replace('\\clearpage\n\\appendix\n\\input{source-code.tex}\n', '')
if '\\newcommand{\\githubrepo}' not in text:
    text = text.replace('\\begin{document}',
        '% Укажите ссылку на GitHub внутри фигурных скобок ниже.\n'
        '\\newcommand{\\githubrepo}{}\n\\begin{document}')
p.write_text(text, encoding='utf-8')

p = report / 'assignment.tex'
text = p.read_text(encoding='utf-8')
text = re.sub(r'\\begin\{Verbatim\}.*?\\end\{Verbatim\}',
              lambda _: '\\input{domain-requirements.tex}', text, flags=re.S)
p.write_text(text, encoding='utf-8')

p = report / 'body.tex'
text = p.read_text(encoding='utf-8')
text = text.replace('Ниже приведён текст задания из файла \\texttt{Lab1.md}; далее отдельно описаны решения, принятые при реализации.',
                    'Ниже изложены требования из файла \\texttt{Lab1.md}; описание полей представлено таблицей без листингов исходного кода. Далее отдельно описаны решения, принятые при реализации.')
text = text.replace('\\section{Исходный код и воспроизведение}', '\\section{Репозиторий проекта и воспроизведение}')
start = text.index('Полный проект находится в каталоге')
end = text.index('\\begin{enumerate}', start)
text = text[:start] + r'''Исходный код, SQL-схема, автоматизированные тесты и инструкции по запуску размещаются в репозитории проекта. Листинги исходного кода в отчёт не включены.

\noindent\textbf{Ссылка на репозиторий GitHub:}\par
\ifx\githubrepo\empty
\noindent\fbox{\parbox{\dimexpr\linewidth-2\fboxsep-2\fboxrule\relax}{\vspace{0.3em}\textit{Место для ссылки на репозиторий GitHub.}\vspace{0.3em}}}
\else
\noindent\expandafter\url\expandafter{\githubrepo}
\fi

''' + text[end:]
text = text.replace('; относительные пути к исходному проекту должны сохраняться.',
                    '; все материалы отчёта находятся в каталоге \\texttt{report}.')
p.write_text(text, encoding='utf-8')

# Retain the superseded appendix only as an internal backup, outside the report.
p = report / 'source-code.tex'
if p.exists():
    backup = base / 'tools' / 'encoding-backup'
    backup.mkdir(exist_ok=True)
    (backup / 'source-code.removed.tex.bak').write_bytes(p.read_bytes())
    p.unlink()

readme = report / 'README.md'
text = readme.read_text(encoding='utf-8')
start = text.index('Сохраняйте соседний каталог')
end = text.index('\n\nСтудент', start)
text = text[:start] + '''Отчёт не содержит листингов исходного кода и не зависит от соседнего каталога приложения. В `report.tex` предусмотрена команда `\\newcommand{\\githubrepo}{}`: впишите ссылку на GitHub между последними фигурными скобками. Пока ссылка не указана, PDF показывает обозначенное место для неё.

Изображения находятся в `images/`. `assignment.tex` содержит требования задания; поля классов перечислены в `domain-requirements.tex` без Java-кода. `body.tex` содержит описание реализации, тестирование и выводы; `classes.tex` и `packages.tex` — UML-диаграммы TikZ. Все текстовые файлы сохранены в UTF-8.''' + text[end:]
readme.write_text(text, encoding='utf-8')
print('Code listings removed. GitHub placeholder added. Report is self-contained.')
