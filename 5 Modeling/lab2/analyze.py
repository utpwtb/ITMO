"""Exact CTMC calculation for two queueing systems; no simulation or MARK calls."""
from pathlib import Path
import csv
import json
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

ROOT = Path(__file__).resolve().parent
DATA = ROOT / 'data'
DATA.mkdir(exist_ok=True)
FIG = ROOT / 'latex' / 'figures'
FIG.mkdir(parents=True, exist_ok=True)
B, V, A1, A2 = 40., 2.6, .7, .3
MU = 1 / B
H1 = (1 + np.sqrt((V * V - 1) / (V * V + 1))) / 2
H2 = 1 - H1
MU11, MU12 = 2 * H1 / B, 2 * H2 / B


def stationary(g):
    matrix = g.T.copy()
    matrix[-1, :] = 1
    rhs = np.zeros(len(g))
    rhs[-1] = 1
    p = np.linalg.solve(matrix, rhs)
    assert np.min(p) > -1e-12
    assert abs(p.sum() - 1) < 1e-12
    assert np.max(np.abs(p @ g)) < 1e-12
    return p


def generator(n, edges):
    g = np.zeros((n, n))
    for i, j, rate in edges:
        g[i, j] += rate
    np.fill_diagonal(g, -g.sum(axis=1))
    return g


def system1(lam):
    # E0=(0,0;0), E1=(1,0;0), E2=(0,1;0), E3..7=(1,1;0..4).
    edges = [(0,1,A1*lam),(0,2,A2*lam),(1,0,MU),(2,0,MU),
             (1,3,lam),(2,3,lam),(3,1,MU),(3,2,MU)]
    for j in range(3,7):
        edges += [(j,j+1,lam),(j+1,j,2*MU)]
    g = generator(8, edges)
    p = stationary(g)
    rho = np.array([p[1]+p[3:].sum(), p[2]+p[3:].sum()])
    ell = sum(q*p[q+3] for q in range(5))
    m = p[1]+p[2]+sum((q+2)*p[q+3] for q in range(5))
    out = MU * rho
    loss = lam*p[7]
    # Poisson arrivals see p; only q<=3 accepted; q+1 departures at rate 2 mu.
    wait_numerator = sum(p[q+3]*(q+1)/(2*MU) for q in range(4))
    w = wait_numerator/(1-p[7])
    # Tag a customer by its eventual serving device (equal rates => probability 1/2).
    wi = lam*.5*wait_numerator/out
    li = np.array([ell/2,ell/2])
    mi = rho+li
    result = dict(y=lam*B,rho=rho.tolist(),rho_mean=rho.mean(),
                  eta=1-rho.mean(),kprime=rho.sum(),l=ell,m=m,pi=p[7],
                  throughput=out.sum(),throughput_i=out.tolist(),loss=loss,
                  w=w,u=w+B,w_i=wi.tolist(),u_i=(wi+B).tolist(),
                  l_attributed=li.tolist(),m_attributed=mi.tolist())
    assert abs(lam-loss-out.sum())<1e-12
    assert abs(ell-out.sum()*w)<1e-11
    assert abs(m-out.sum()*(w+B))<1e-11
    assert np.max(np.abs(li-out*wi))<1e-11
    return g,p,result


def system2(lam):
    l1,l2 = A1*lam,A2*lam
    ga = generator(3,[(0,1,l1*H1),(0,2,l1*H2),(1,0,MU11),(2,0,MU12)])
    gb = generator(4,[(i,i+1,l2) for i in range(3)]+[(i,i-1,MU) for i in range(1,4)])
    # E_(4a+k), a=0,1,2 and k=0,1,2,3.
    g = np.kron(ga,np.eye(4))+np.kron(np.eye(3),gb)
    p = stationary(g)
    pa,pb = p.reshape(3,4).sum(axis=1),p.reshape(3,4).sum(axis=0)
    assert np.max(np.abs(p-np.kron(stationary(ga),stationary(gb))))<1e-12
    rho = np.array([1-pa[0],1-pb[0]])
    ell = pb[2]+2*pb[3]
    m = rho.sum()+ell
    out = np.array([MU11*pa[1]+MU12*pa[2],MU*(1-pb[0])])
    pi_i = np.array([rho[0],pb[3]])
    pi = A1*pi_i[0]+A2*pi_i[1]
    # Conditional on acceptance: k previous services of mean b, k=0,1,2.
    wi = np.array([0., B*(pb[1]+2*pb[2])/(1-pb[3])])
    w = np.dot(out,wi)/out.sum()
    result = dict(y=lam*B,y_i=[l1*B,l2*B],rho=rho.tolist(),rho_mean=rho.mean(),
                  eta=1-rho.mean(),kprime=rho.sum(),l=ell,l_i=[0.,ell],
                  m=m,m_i=[rho[0],rho[1]+ell],pi=pi,pi_i=pi_i.tolist(),
                  throughput=out.sum(),throughput_i=out.tolist(),loss=lam*pi,
                  loss_i=(np.array([l1,l2])*pi_i).tolist(),w=w,u=w+B,
                  w_i=wi.tolist(),u_i=(wi+B).tolist(),pa=pa.tolist(),pb=pb.tolist())
    assert abs(lam*(1-pi)-out.sum())<1e-12
    assert abs(ell-out.sum()*w)<1e-11
    assert abs(m-out.sum()*(w+B))<1e-11
    return g,p,result


def save_baseline():
    all_results={ 'parameters':dict(lam=.1,b=B,v=V,a1=A1,a2=A2,h1=H1,h2=H2,mu=MU,mu11=MU11,mu12=MU12)}
    for i,fn in enumerate([system1,system2],1):
        g,p,r=fn(.1)
        np.savetxt(DATA/f'G{i}.csv',g,delimiter=',',fmt='%.12g')
        with (DATA/f'states{i}.csv').open('w',newline='',encoding='utf-8-sig') as f:
            writer=csv.writer(f);writer.writerow(['state','code','probability'])
            for j,pj in enumerate(p):
                code=([(0,0,0),(1,0,0),(0,1,0)]+[(1,1,q) for q in range(5)])[j] if i==1 else (j//4,j%4)
                writer.writerow([f'E{j}',str(code),f'{pj:.12g}'])
        r['p']=p.tolist();r['max_balance_residual']=float(np.max(np.abs(p@g)))
        all_results[f'system{i}']=r
    assert abs(H1/MU11+H2/MU12-B)<1e-10
    assert abs((2*(H1/MU11**2+H2/MU12**2)-B**2)/B**2-V**2)<1e-10
    (DATA/'results.json').write_text(json.dumps(all_results,ensure_ascii=False,indent=2),encoding='utf-8')
    return all_results


def plots():
    plt.rcParams.update({'font.family':'DejaVu Serif','font.size':10,'axes.spines.top':False,'axes.spines.right':False})
    xs=np.linspace(.005,.2,160)
    r1=[system1(x)[2] for x in xs];r2=[system2(x)[2] for x in xs]
    fig,axs=plt.subplots(2,2,figsize=(9,5.1),layout='constrained')
    for ax,key,label in zip(axs.flat,['l','pi','throughput','u'],
                            [r'$l$, заявок',r'$\pi$',r"$\lambda'$, с$^{-1}$",r'$u$, с']):
        for rs,lab,color,ls in [(r1,'СИСТЕМА 1','#1f4e79','-'),(r2,'СИСТЕМА 2','#aa4b27','--')]:
            ax.plot(xs,[r[key] for r in rs],label=lab,color=color,ls=ls,lw=1.8)
        ax.axvline(.1,color='0.5',ls=':',lw=1)
        ax.set(xlabel=r'$\lambda$, с$^{-1}$',ylabel=label,xlim=(0,.2))
        ax.grid(alpha=.2)
    axs[0,0].legend(frameon=False)
    fig.savefig(FIG/'comparison.pdf');fig.savefig(FIG/'comparison.png',dpi=180);plt.close(fig)
    with (DATA/'sweep.csv').open('w',newline='',encoding='utf-8-sig') as f:
        w=csv.writer(f);w.writerow(['lambda','l_1','l_2','pi_1','pi_2','throughput_1','throughput_2','u_1','u_2'])
        for x in [.01,.025,.05,.075,.1,.125,.15,.2]:
            a=system1(x)[2];b=system2(x)[2]
            w.writerow([x,a['l'],b['l'],a['pi'],b['pi'],a['throughput'],b['throughput'],a['u'],b['u']])


def latex_tables(results):
    directory=ROOT/'latex'/'tables'
    directory.mkdir(exist_ok=True)
    r1,r2=results['system1'],results['system2']
    lines=[]
    codes=[(0,0,0),(1,0,0),(0,1,0)]+[(1,1,q) for q in range(5)]
    for j in range(12):
        if j<8:
            d1,d2,q=codes[j]
            left=rf'$E_{{{j}}}$ & $({d1},{d2};{q})$ & {r1["p"][j]:.9f}'
        else:
            left='--- & --- & ---'
        lines.append(left+rf' & $E_{{{j}}}$ & $({j//4},{j%4})$ & {r2["p"][j]:.9f} \\')
    (directory/'probabilities.tex').write_text('\n'.join(lines)+'\n'+r'\bottomrule'+'\n',encoding='utf-8')
    metrics=[('Нагрузка',r'$y$','y'),('Средняя загрузка приборов',r'$\rho$','rho_mean'),
             ('Среднее число работающих приборов',r"$k'$",'kprime'),('Коэффициент простоя',r'$\eta$','eta'),
             ('Средняя длина очереди',r'$l$','l'),('Среднее число заявок',r'$m$','m'),
             ('Вероятность потери',r'$\pi$','pi'),('Производительность, с$^{-1}$',r"$\lambda'$",'throughput'),
             ('Поток отказов, с$^{-1}$',r"$\lambda''$",'loss'),
             ('Среднее время ожидания, с',r'$w$','w'),('Среднее время пребывания, с',r'$u$','u')]
    lines=[rf'{name} & {symbol} & {r1[key]:.9f} & {r2[key]:.9f} \\' for name,symbol,key in metrics]
    (directory/'totals.tex').write_text('\n'.join(lines)+'\n'+r'\bottomrule'+'\n',encoding='utf-8')
    metrics=[('Нагрузка',r'$y_i=\lambda_i b$',[None,None],r2['y_i']),
             ('Загрузка',r'$\rho_i=\sum p$',r1['rho'],r2['rho']),
             ('Простой',r'$\eta_i=1-\rho_i$',[1-x for x in r1['rho']],[1-x for x in r2['rho']]),
             ('Длина очереди',r'$l_i\ (l_i^*)$',r1['l_attributed'],r2['l_i']),
             ('Число заявок',r'$m_i\ (m_i^*)$',r1['m_attributed'],r2['m_i']),
             ('Ожидание, с',r'$w_i$',r1['w_i'],r2['w_i']),
             ('Пребывание, с',r'$u_i=w_i+b$',r1['u_i'],r2['u_i']),
             ('Вероятность потери',r'$\pi_i$',[None,None],r2['pi_i']),
             ('Производит., с$^{-1}$',r"$\lambda_i'$",r1['throughput_i'],r2['throughput_i']),
             ('Поток отказов, с$^{-1}$',r"$\lambda_i''=\lambda_i\pi_i$",[None,None],r2['loss_i'])]
    lines=[name+' & '+formula+' & '+' & '.join('---' if x is None else f'{x:.6f}' for x in a+b)+r' \\' for name,formula,a,b in metrics]
    (directory/'devices.tex').write_text('\n'.join(lines)+'\n'+r'\bottomrule'+'\n',encoding='utf-8')


if __name__=='__main__':
    r=save_baseline();plots();latex_tables(r);print(json.dumps(r,ensure_ascii=False,indent=2))
