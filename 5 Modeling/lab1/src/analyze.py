"""Воспроизводимый анализ УИР 1, вариант 263. Запуск: python analyze.py."""
from pathlib import Path
import csv
import json
import math
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from scipy import stats
from scipy.linalg import expm
from generator import generate, fit

ROOT = Path(__file__).resolve().parents[1]
REPORT = ROOT / 'report'
NS = [10, 20, 50, 100, 200, 300]
PS = [.9, .95, .99]
plt.rcParams.update({'font.family': 'DejaVu Sans', 'font.size': 10,
                     'axes.spines.top': False, 'axes.spines.right': False})


def characteristics(x):
    m, v = x.mean(), x.var(ddof=1)
    return np.array([m, v, np.sqrt(v), np.sqrt(v)/m,
                     *[stats.norm.ppf((1+p)/2)*np.sqrt(v/len(x)) for p in PS]])


def acf(x, k):
    return np.corrcoef(x[:-k], x[k:])[0, 1]


def pct(a, b):
    return 100 * (a-b)/np.abs(b)


def fmt(x, digits=4):
    return f'{x:.{digits}f}'


def savefig(name):
    plt.tight_layout()
    plt.savefig(REPORT/'figures'/f'{name}.pdf', bbox_inches='tight')
    plt.savefig(REPORT/'figures'/f'{name}.png', dpi=150, bbox_inches='tight')
    plt.close()


def form_table(values, baseline, filename):
    labels = [r'$\bar x$', r'$s^2$', r'$s$', r'$v$',
              r'$\varepsilon_{0.90}$', r'$\varepsilon_{0.95}$', r'$\varepsilon_{0.99}$']
    lines = [r'\begin{tabular}{lrrrrrr}\toprule',
             'Показатель & '+' & '.join(map(str, NS))+r' \\\midrule']
    for j, label in enumerate(labels):
        cells = [(' $\\pm '+fmt(v[j])+'$') if j>=4 else fmt(v[j]) for v in values]
        lines.append(label+' & '+' & '.join(cells)+r' \\')
        lines.append(r'$\Delta,\%$ & '+' & '.join(fmt(pct(values[i,j], baseline[i,j]),2) for i in range(6))+r' \\\addlinespace')
    lines.append(r'\bottomrule\end{tabular}')
    (REPORT/'tables'/filename).write_text('\n'.join(lines), encoding='utf-8')


def main():
    for path in [REPORT/'figures',REPORT/'tables',ROOT/'data']:
        path.mkdir(parents=True,exist_ok=True)
    x = np.loadtxt(ROOT/'data'/'measurements.csv', delimiter=',', skiprows=1)[:,1]
    assert len(x)==300 and np.isfinite(x).all()
    X = np.array([characteristics(x[:n]) for n in NS])
    m, v = X[-1,:2]
    a,b = fit(m,v)
    assert np.isclose(2*a+b,m) and np.isclose(2*a*a+b*b,v)
    y = generate(m,v)
    Y = np.array([characteristics(y[:n]) for n in NS])
    np.savetxt(ROOT/'data'/'simulated.csv', np.c_[np.arange(1,301),y], delimiter=',', header='i,y', comments='',fmt=['%d','%.17g'])
    form_table(X,np.tile(X[-1],(6,1)),'form1.tex')
    form_table(Y,X,'form2.tex')
    with (ROOT/'data'/'statistics.csv').open('w',newline='',encoding='utf-8') as f:
        w=csv.writer(f);w.writerow(['series','n','mean','variance','std','cv','halfwidth90','halfwidth95','halfwidth99'])
        for label,values in [('original',X),('generated',Y)]:
            for n,row in zip(NS,values): w.writerow([label,n,*row])
    rx=np.array([acf(x,k) for k in range(1,61)])
    ry=np.array([acf(y,k) for k in range(1,61)])
    lines=[r'\begin{tabular}{rrrrr}\toprule',r'$k$ & $r_x(k)$ & $r_y(k)$ & $\Delta r$ & $\Delta,\%$ \\\midrule']
    for k in range(10):
        lines.append(' & '.join([str(k+1),fmt(rx[k]),fmt(ry[k]),fmt(ry[k]-rx[k]),fmt(pct(ry[k],rx[k]),2)])+r' \\')
    lines.append(r'\bottomrule\end{tabular}')
    (REPORT/'tables'/'form3.tex').write_text('\n'.join(lines),encoding='utf-8')
    np.savetxt(ROOT/'data'/'autocorrelation.csv',np.c_[np.arange(1,61),rx,ry],delimiter=',',header='lag,original,generated',comments='')
    # Фазовое представление суммы независимых экспоненциальных стадий.
    rates=1/np.array([a,a,b]); T=np.diag(-rates)+np.diag(rates[:-1],1)
    def cdf(t):
        return np.array([0. if z<0 else 1-(expm(T*z)[0]).sum() for z in np.atleast_1d(t)])
    def pdf(t):
        return np.array([0. if z<0 else expm(T*z)[0,-1]*rates[-1] for z in np.atleast_1d(t)])
    edges=np.linspace(0,max(x.max(),y.max()),11)
    cx,_=np.histogram(x,edges);cy,_=np.histogram(y,edges)
    expected=300*np.diff(cdf(edges))
    lines=[r'\begin{tabular}{rrrrr}\toprule',r'Левая граница & Правая граница & $n_x$ & $n_y$ & $300p_j$ \\\midrule']
    for l,r,nx,ny,e in zip(edges[:-1],edges[1:],cx,cy,expected):
        lines.append(f'{l:.2f} & {r:.2f} & {nx} & {ny} & {e:.2f}'+r' \\')
    lines.append(r'\bottomrule\end{tabular}')
    (REPORT/'tables'/'histogram.tex').write_text('\n'.join(lines),encoding='utf-8')
    fig,ax=plt.subplots(figsize=(9,3.5));ax.plot(np.arange(1,301),x,lw=.8);ax.axhline(m,color='black',ls='--',label='Среднее')
    ax.set(xlabel='Номер наблюдения i',ylabel='Значение xᵢ',title='Исходная последовательность, вариант 263');ax.legend();savefig('original')
    fig,ax=plt.subplots(figsize=(9,3.5));ax.hist(x,bins=edges,color='#4178a8',edgecolor='white');ax.set(xlabel='x',ylabel='Частота',title='Гистограмма исходной последовательности');savefig('hist_original')
    fig,axes=plt.subplots(2,1,figsize=(9,5.5),sharex=True)
    for ax,r,title in zip(axes,[rx,ry],['Исходная последовательность','Сгенерированная последовательность']):
        ax.stem(np.arange(1,61),r,basefmt=' ');ax.axhline(1.96/np.sqrt(300),ls='--',color='gray');ax.axhline(-1.96/np.sqrt(300),ls='--',color='gray');ax.set(ylabel='r(k)',title=title,ylim=(-.3,.3));ax.grid(alpha=.2)
    axes[-1].set_xlabel('Сдвиг k');savefig('acf')
    fig,axes=plt.subplots(2,1,figsize=(9,5.5),sharex=True,sharey=True)
    for ax,z,title in zip(axes,[x,y],['Исходная последовательность','Гипоэкспоненциальный генератор']):
        ax.plot(np.arange(1,301),z,lw=.8);ax.set(ylabel='Значение',title=title)
    axes[-1].set_xlabel('Номер наблюдения i');savefig('comparison')
    fig,ax=plt.subplots(figsize=(9,4));ax.hist(x,bins=edges,density=True,alpha=.45,label='Исходная');ax.hist(y,bins=edges,density=True,histtype='step',lw=1.8,label='Сгенерированная');t=np.linspace(0,edges[-1],400);ax.plot(t,pdf(t),'k-',label='Теоретическая плотность');ax.set(xlabel='x',ylabel='Плотность');ax.legend();savefig('density')
    fig,ax=plt.subplots(figsize=(8,3.5))
    for j,p in enumerate(PS):ax.plot(NS,X[:,4+j],'-o',label=f'p = {p}')
    ax.set(xlabel='Объём выборки n',ylabel='Полуширина интервала');ax.legend();savefig('ci')
    # Дополнительные диагностические показатели; не доказательство независимости.
    def ljung(z):
        center=z-z.mean();r=np.array([np.dot(center[:-k],center[k:])/np.dot(center,center) for k in range(1,11)])
        q=len(z)*(len(z)+2)*np.sum(r*r/(len(z)-np.arange(1,11)))
        return [float(q),float(stats.chi2.sf(q,10))]
    trend=stats.linregress(np.arange(1,301),x)
    correlation=stats.pearsonr(x,y)
    D=float(stats.kstest(x,cdf).statistic) # p-value неприменимо без поправки за оценку параметров.
    result=dict(mean=m,variance=v,std=np.sqrt(v),cv=np.sqrt(v)/m,a=a,b=b,rate_a=1/a,rate_b=1/b,
                raw_m2=float(np.mean(x*x)),target_m2=m*m+v,generated=Y[-1].tolist(),
                deviation_pct=pct(Y[-1],X[-1]).tolist(),acf_original=rx[:10].tolist(),acf_generated=ry[:10].tolist(),
                ljung_original=ljung(x),ljung_generated=ljung(y),trend_slope=trend.slope,trend_p=trend.pvalue,
                cross_r=correlation.statistic,cross_p=correlation.pvalue,ecdf_distance=D,
                minimum=x.min(),maximum=x.max(),halfwidths=X[-1,4:].tolist(),
                ks_two_sample=float(stats.ks_2samp(x,y).statistic))
    (ROOT/'data'/'results.json').write_text(json.dumps(result,indent=2),encoding='utf-8')
    print(json.dumps(result,indent=2))
    # Независимая проверка устойчивой реализации дисперсии и нормировки плотности.
    import statistics
    from scipy.integrate import quad
    assert np.isclose(statistics.variance(x),v)
    assert abs(quad(lambda z:pdf([z])[0],0,np.inf)[0]-1)<1e-8
    assert cx.sum()==cy.sum()==300
    assert np.array_equal(y,generate(m,v))
    print('Validation passed: moments, density, counts, deterministic generation.')


if __name__=='__main__':main()
