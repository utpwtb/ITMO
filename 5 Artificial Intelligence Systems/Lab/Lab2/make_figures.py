"""Графики и таблицы отчёта из сохранённых результатов; модели здесь не обучаются."""
from pathlib import Path
import json
import sys
import numpy as np
import pandas as pd
ROOT = Path(__file__).resolve().parent
sys.path.append(str(ROOT / '.deps'))
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from model import FEATURES, Preprocessor

RESULTS = ROOT / 'results'
FIGURES = ROOT / 'report/figures'
TABLES = ROOT / 'report/tables'
FIGURES.mkdir(parents=True, exist_ok=True)
TABLES.mkdir(parents=True, exist_ok=True)
plt.rcParams.update({'font.family': 'DejaVu Sans', 'font.size': 10,
                     'axes.spines.top': False, 'axes.spines.right': False,
                     'savefig.dpi': 180, 'axes.titleweight': 'bold'})
LABELS = ['Беременности', 'Глюкоза', 'Давление', 'Кожная складка',
          'Инсулин', 'ИМТ', 'Наследственность', 'Возраст']


def save(name):
    plt.savefig(FIGURES / (name + '.pdf'), bbox_inches='tight')
    plt.savefig(FIGURES / (name + '.png'), bbox_inches='tight')
    plt.close()


data = pd.read_csv(ROOT / 'data/pima-indians-diabetes.csv', header=None,
                   names=FEATURES + ['Outcome'])
clean = Preprocessor.clean(data)
stats = clean.describe().T
fig, axes = plt.subplots(2, 4, figsize=(11.6, 5.5))
for ax, column, label in zip(axes.flat, FEATURES, LABELS):
    ax.hist(clean[column].dropna(), bins=18, color='#31688e', edgecolor='white', linewidth=.4)
    ax.axvline(stats.loc[column, 'mean'], color='#c55a11', linewidth=1.4, label='Среднее')
    ax.axvline(stats.loc[column, '50%'], color='#252525', linestyle='--', linewidth=1.2, label='Медиана')
    ax.set_title(label, fontsize=10)
    ax.set_ylabel('Количество')
axes[0,0].legend(fontsize=7)
fig.tight_layout()
save('distributions')

fig, axes = plt.subplots(2, 4, figsize=(11.6, 5.5))
for ax, column, label in zip(axes.flat, FEATURES, LABELS):
    s = stats.loc[column]
    ax.plot([0,0], [s['min'],s['max']], color='#999999', linewidth=1.2)
    ax.plot([0,0], [s['25%'],s['75%']], color='#31688e', linewidth=12, solid_capstyle='butt')
    ax.plot(0,s['50%'],'_', color='white', markersize=13, markeredgewidth=2)
    ax.errorbar(.45,s['mean'], yerr=s['std'], fmt='o', color='#c55a11', capsize=4)
    ax.set_xticks([0,.45], ['Квантили','Среднее ± s'], fontsize=8)
    ax.set_xlim(-.3,.85)
    ax.set_title(f"{label}\nn={int(s['count'])}", fontsize=10)
fig.tight_layout()
save('statistics')

fig, axes = plt.subplots(1,2,figsize=(11.3,3.5), gridspec_kw={'width_ratios':[1,2]})
axes[0].bar(['Класс 0','Класс 1'],[500,268],color=['#31688e','#c55a11'])
for i,v in enumerate([500,268]): axes[0].text(i,v+8,str(v),ha='center')
axes[0].set_ylim(0,560)
axes[0].set_ylabel('Количество')
axes[0].set_title('Распределение классов')
axes[1].barh(LABELS,clean.isna().sum().to_numpy(),color='#31688e')
axes[1].invert_yaxis()
axes[1].set_xlabel('Количество нулей, заменяемых на пропуск')
axes[1].set_title('Пропуски до заполнения')
fig.tight_layout()
save('missing_classes')

table = pd.read_csv(RESULTS / 'test_metrics.csv')
validation = pd.read_csv(RESULTS / 'validation_metrics.csv')
histories = json.loads((RESULTS / 'loss_histories.json').read_text())
fig, axes = plt.subplots(1,2,figsize=(11.3,3.8))
for index in [2,5,8,11]:
    r = table.loc[index]
    axes[0].plot(histories[str(index)],label=f"α={r.learning_rate:g}")
axes[0].set_xscale('symlog',linthresh=1)
axes[0].set_title('Градиентный спуск')
axes[0].set_xlabel('Итерация (логарифмическая шкала)')
for index in [14,17,20]:
    r = table.loc[index]
    axes[1].plot(histories[str(index)],label=f"α={r.learning_rate:g}")
axes[1].set_title('Метод Ньютона')
axes[1].set_xlabel('Итерация')
for ax in axes:
    ax.set_ylabel('Log loss на train')
    ax.legend()
    ax.grid(alpha=.2)
fig.tight_layout()
save('convergence')

fig, axes = plt.subplots(1,2,figsize=(10.8,3.6))
for ax, method, title in zip(axes,['gd','newton'],['Градиентный спуск','Метод Ньютона']):
    matrix = validation[validation.method==method].pivot(index='learning_rate',columns='iterations',values='val_log_loss')
    im=ax.imshow(matrix,aspect='auto',cmap='YlGnBu',vmin=.46,vmax=.68)
    ax.set_xticks(range(len(matrix.columns)),matrix.columns)
    ax.set_yticks(range(len(matrix.index)),[f'{x:g}' for x in matrix.index])
    ax.set_xlabel('Число итераций')
    ax.set_ylabel('Шаг α')
    ax.set_title(title)
    for i in range(len(matrix)):
        for j in range(len(matrix.columns)):
            value=matrix.iloc[i,j]
            ax.text(j,i,f'{value:.4f}',ha='center',va='center',color='white' if value>.59 else 'black')
fig.colorbar(im,ax=axes.tolist(),label='Validation log loss',fraction=.025,pad=.03)
save('validation_grid')

summary=json.loads((RESULTS/'summary.json').read_text())
r=summary['selected_result']
cm=np.array([[r['tn'],r['fp']],[r['fn'],r['tp']]])
fig,axes=plt.subplots(1,2,figsize=(10.8,3.8))
axes[0].imshow(cm,cmap='Blues',vmin=0,vmax=100)
for i in range(2):
    for j in range(2): axes[0].text(j,i,str(cm[i,j]),ha='center',va='center',fontsize=18,color='white' if cm[i,j]>50 else 'black')
axes[0].set_xticks([0,1],['0','1']); axes[0].set_yticks([0,1],['0','1'])
axes[0].set_xlabel('Предсказанный класс'); axes[0].set_ylabel('Истинный класс')
axes[0].set_title('Матрица ошибок (test, n=154)')
coef=pd.read_csv(RESULTS/'coefficients.csv').iloc[1:]
axes[1].barh(LABELS,coef.weight,color='#31688e')
axes[1].invert_yaxis(); axes[1].set_xlabel('Коэффициент стандартизованного признака')
axes[1].set_title('Выбранная модель')
fig.tight_layout()
save('selected_model')


def write_table(filename, header, rows, spec):
    text = '\\begin{tabular}{' + spec + '}\n\\toprule\n' + header + r' \\' + '\n\\midrule\n'
    text += '\n'.join(' & '.join(row) + r' \\' for row in rows)
    text += '\n\\bottomrule\n\\end{tabular}\n'
    (TABLES/filename).write_text(text,encoding='utf8')

rows=[]
for label,(_,s) in zip(LABELS,stats.iterrows()):
    rows.append([label,str(int(s['count']))]+[f'{s[c]:.2f}' for c in ['mean','std','min','25%','50%','75%','max']])
write_table('statistics.tex','Признак & n & Среднее & s & min & Q1 & Q2 & Q3 & max',rows,'lrrrrrrrr')
for method in ['gd','newton']:
    rows=[]
    for _,s in table[table.method==method].iterrows():
        val=validation.loc[validation.config_id==s.config_id,'val_log_loss'].iloc[0]
        row=[f'{s.learning_rate:g}',str(int(s.iterations)),f'{val:.4f}']+[f'{s[c]:.4f}' for c in ['accuracy','precision','recall','f1','test_log_loss']]
        if s.selected: row=[r'\textbf{'+v+'}' for v in row]
        rows.append(row)
    write_table(method+'.tex',r'$\alpha$ & T & $L_{val}$ & Accuracy & Precision & Recall & F1 & $L_{test}$',rows,'rrrrrrrr')
rows=[[s.feature.replace('DiabetesPedigreeFunction','Наследственность'),f'{s.weight:.4f}',f'{s.odds_ratio:.4f}'] for _,s in pd.read_csv(RESULTS/'coefficients.csv').iterrows()]
write_table('coefficients.tex',r'Признак & $w_j$ & $\exp(w_j)$',rows,'lrr')
prediction=pd.read_csv(RESULTS/'test_predictions.csv').sort_values('row_id').head(6)
rows=[[str(int(s.row_id)),str(int(s.actual)),f'{s.probability:.4f}',str(int(s.predicted))] for _,s in prediction.iterrows()]
write_table('examples.tex','Индекс строки & Истина & Вероятность & Прогноз',rows,'rrrr')
print('Created 6 figures and 5 tables from actual results.')
