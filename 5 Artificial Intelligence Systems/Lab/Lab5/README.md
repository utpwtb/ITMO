# Лабораторная работа 5 Деревья решений

Вариант — нечётный номер. Программа строит многоветвевые деревья на категориальных признаках и сравнивает критерии энтропии и Джини. Деревья, предсказание, метрики и площади под кривыми реализованы на Python. Matplotlib используется для графиков.

## Запуск

Из каталога Lab5 с Python 3.11 или новее выполните:

    python -m pip install -r requirements.txt
    python -B src/experiment.py

Программа выводит распределение классов, названия пяти признаков и структуру обоих деревьев. Результаты записываются в results/. Для записи в другой каталог можно передать --output. Фиксированные seed 42 и 43 задают разбиение 80/20 и однократный отбор признаков соответственно.

## Файлы

- [src/experiment.py](src/experiment.py) выполняет эксперимент. [src/tree.py](src/tree.py) и [src/metrics.py](src/metrics.py) содержат реализацию дерева и метрик.
- [data/students.csv](data/students.csv) содержит исходные данные UCI. Для целевого класса используется условие OUTPUT Grade ≥ 3.
- [results/trees.txt](results/trees.txt) содержит полную структуру двух деревьев и суммы выигрышей.
- [results/metrics.csv](results/metrics.csv) содержит метрики при пороге 0,5 и AUC на тесте. В [results/thresholds.csv](results/thresholds.csv) поле pr_precision задаёт ординату PR-кривой. Для пустого набора положительных прогнозов используется начальная точка (0, 1), а precision в таблице метрик полагается равной нулю.
- [results/importance.png](results/importance.png) и [results/curves.png](results/curves.png) содержат итоговые графики.
- [Отчёт в PDF](report/main.pdf), [исходник LaTeX](report/main.tex) и [контрольные вопросы на русском и китайском](control_questions.md).

Данные распространяются по лицензии CC BY 4.0. Файл сохранён без изменений из [CSV UCI](https://archive.ics.uci.edu/static/public/856/data.csv). Yilmaz, N., & Şekeroğlu, B. (2019). Higher Education Students Performance Evaluation. UCI Machine Learning Repository. [DOI 10.24432/C51G82](https://doi.org/10.24432/C51G82).

## Сборка отчёта

Из каталога report выполните `tectonic main.tex` или дважды запустите
`xelatex -halt-on-error main.tex`. Отчёт использует шрифты из report/fonts/,
листинги из src/ и графики из results/.
