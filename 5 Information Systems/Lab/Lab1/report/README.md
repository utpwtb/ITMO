# Отчёт LaTeX

Основной файл: `report.tex`. Язык: русский. Оформление и титульный лист адаптированы из `archive_single_salon/stage1_report.tex` и `titlepage.tex`: Times New Roman, 12 pt, межстрочный интервал 1,5; поля слева 30 мм, справа 15 мм, сверху и снизу 20 мм.

```sh
xelatex -interaction=nonstopmode report.tex
xelatex -interaction=nonstopmode report.tex
```

Альтернатива: `tectonic report.tex`. Нужны пакеты fontspec, polyglossia, TikZ, fvextra, graphicx и стандартные пакеты LaTeX. Если Times New Roman/Arial/Consolas недоступны, используются резервные шрифты, заданные в преамбуле.

Сохраняйте соседний каталог `../movie-lab`: приложение к отчёту подключает проверенные исходники напрямую через `\VerbatimInput`. Изображения находятся в `images/`. Содержимое `assignment.tex` воспроизводит разделы 1–6 исходного задания. `body.tex` содержит реализацию, результаты тестов и выводы, `classes.tex` и `packages.tex` — редактируемые UML-диаграммы TikZ.

Студент, группа и преподаватель взяты из предоставленного шаблона. Их можно изменить в `titlepage.tex`.
