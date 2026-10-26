"""Build the report from the confirmed business model and live PostgreSQL metadata."""
from pathlib import Path
from itertools import combinations
from collections import Counter
import json, re, sys, html
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
import pypdfium2 as pdfium

sys.stdout.reconfigure(encoding='utf-8')
S=Path(__file__).resolve().parents[1]
M=json.loads((S/'verification/schema_metadata.json').read_text(encoding='utf-8'))
T=json.loads((S/'verification/test_results.json').read_text(encoding='utf-8'))
COUNTS=json.loads((S/'verification/seed_counts.json').read_text(encoding='utf-8'))
PLANS=json.loads((S/'verification/explain_plans.json').read_text(encoding='utf-8'))
assert T['all_passed']
NAMES={'user_account':'Пользователь','district':'Район','salon':'Салон','service_type':'Вид услуги','salon_service':'Услуга салона',
       'master':'Мастер','master_service':'Мастер--услуга','work_interval':'Рабочий интервал','appointment':'Запись','review':'Отзыв',
       'moderation_decision':'Решение модерации','salon_photo':'Фото интерьера: элементы атрибута','master_photo':'Фото работ: элементы атрибута','master_invitation':'Приглашение: техническая таблица'}
CORE=list(NAMES)[:11]
TABLES={t['name']:t for t in M['tables']}
PK={}
for c in M['constraints']:
    if c['kind']=='p': PK[c['table']]=re.search(r'\(([^)]+)\)',c['definition'])[1].split(', ')
MODEL={'entity_count':11,'entities':[{'name':x,'russian_name':NAMES[x],
  'attributes':[c for c in TABLES[x]['columns'] if c['name']!='slot'],
  'multivalued_attributes':([{'name':'Фотографии интерьера','components':['file_path','caption','sort_order','visibility']}] if x=='salon' else
                          [{'name':'Фотографии работ','components':['file_path','caption','sort_order','visibility']}] if x=='master' else [])} for x in CORE],
  'many_to_many':{'left':'master','right':'salon_service','association':'master_service','key':['master_id','salon_service_id']},
  'physical_table_count':14,'attribute_relations':['salon_photo','master_photo'],'technical_relations':['master_invitation']}
(S/'report/conceptual_model.json').write_text(json.dumps(MODEL,ensure_ascii=False,indent=2),encoding='utf-8')

def tex(v):
    return str(v).replace('&',r'\&').replace('%',r'\%').replace('#',r'\#').replace('_',r'\_\allowbreak{}')
def code(v): return r'\texttt{'+tex(v).replace('.',r'.\allowbreak{}').replace('/',r'/\allowbreak{}')+'}'
def table(headers,rows,widths):
    return '\n'.join([r'\begin{longtable}{'+''.join('L{'+str(w)+'cm}' for w in widths)+'}',r'\toprule '+' & '.join(headers)+r'\\\midrule\endhead']+
                     [' & '.join(row)+r'\\' for row in rows]+[r'\bottomrule\end{longtable}'])

W,H=3.6,2.2
def node(alias,entity,x,y): return {'id':alias,'entity':entity,'x':x,'y':y,'w':W,'h':H}
def anchor(n,a):
    return (n['x']+({'W':-1,'E':1,'SW':-1,'SE':1,'NW':-1,'NE':1}.get(a,0))*n['w']/2,
            n['y']+({'N':1,'S':-1,'NW':1,'NE':1,'SW':-1,'SE':-1}.get(a,0))*n['h']/2)
def view(name,title,nodes): return {'name':name,'title':title,'nodes':nodes,'edges':[]}
def edge(v,a,b,pa,pb,start,end,bends=(),label=''):
    by={n['id']:n for n in v['nodes']}
    v['edges'].append({'a':a,'b':b,'pa':pa,'pb':pb,'start':start,'end':end,'points':[anchor(by[a],start),*bends,anchor(by[b],end)],'label':label})

V=[]
v=view('er_01_catalog','Каталог и принадлежность данных',[node('district','district',2,8),node('salon','salon',7,8),node('service','salon_service',12,8),node('type','service_type',17,8),node('master','master',2,3),node('owner','user_account',7,3)])
edge(v,'district','salon','1','0..N','E','W')
edge(v,'salon','service','1','0..N','E','W')
edge(v,'type','service','1','0..N','W','E')
edge(v,'salon','master','1','0..N','SW','N',[(5.2,5.7),(2,5.7)])
edge(v,'owner','salon','1','0..1','N','S')
edge(v,'owner','master','1','0..1','W','E')
V.append(v)
v=view('er_02_booking','Многие ко многим, рабочее время и посещение',[node('master','master',2,6),node('assignment','master_service',7,6),node('appointment','appointment',12,6),node('review','review',17,6),node('service','salon_service',7,10),node('work','work_interval',2,2),node('client','user_account',12,2)])
for a,b in [('master','assignment'),('assignment','appointment')]: edge(v,a,b,'1','0..N','E','W')
edge(v,'appointment','review','1','0..2','E','W')
edge(v,'service','assignment','1','0..N','S','N')
edge(v,'master','work','1','0..N','S','N')
edge(v,'client','appointment','1','0..N','N','S')
V.append(v)
v=view('er_03_moderation','Администратор и четыре взаимоисключающих цели',[node('admin','user_account',2,6),node('decision','moderation_decision',7,6),node('salon','salon',12,10),node('master','master',12,6),node('review','review',12,2),node('target_user','user_account',2,2)])
edge(v,'admin','decision','1','0..N','E','W')
edge(v,'salon','decision','0..1','0..N','W','N',[(7,10)])
edge(v,'master','decision','0..1','0..N','W','E')
edge(v,'review','decision','0..1','0..N','W','SE',[(8.8,2)])
edge(v,'target_user','decision','0..1','0..N','E','SW',[(5.2,2)])
V.append(v)
v=view('er_04_evidence','Необязательные ссылки на инициаторов действий',[node('cancel_actor','user_account',3,7),node('cancel_appointment','appointment',11,7),node('result_actor','user_account',3,2),node('result_appointment','appointment',11,2)])
edge(v,'cancel_actor','cancel_appointment','0..1','0..N','E','W',label='cancelled_by_user_id')
edge(v,'result_actor','result_appointment','0..1','0..N','E','W',label='result_marked_by_user_id')
V.append(v)
v=view('logical_01_photos','Отношения для многозначных атрибутов и их модерация',[node('salon','salon',2,9),node('interior','salon_photo',8,9),node('master','master',2,3),node('work','master_photo',8,3),node('decision','moderation_decision',14,6)])
edge(v,'salon','interior','1','0..N','E','W')
edge(v,'master','work','1','0..N','E','W')
edge(v,'interior','decision','0..1','0..N','E','NW',[(12.2,9)],label='салон + путь')
edge(v,'work','decision','0..1','0..N','E','SW',[(12.2,3)],label='мастер + путь')
V.append(v)
v=view('logical_02_invitation','Техническое отношение одноразового приглашения',[node('owner','user_account',2,5),node('invitation','master_invitation',8,5),node('master','master',14,5)])
edge(v,'owner','invitation','1','0..N','E','W')
edge(v,'master','invitation','1','0..N','W','E')
V.append(v)

def intersects(s,t):
    (x1,y1),(x2,y2)=s; (x3,y3),(x4,y4)=t
    if y1==y2 and y3==y4: return y1==y3 and max(min(x1,x2),min(x3,x4))<=min(max(x1,x2),max(x3,x4))+1e-8
    if x1==x2 and x3==x4: return x1==x3 and max(min(y1,y2),min(y3,y4))<=min(max(y1,y2),max(y3,y4))+1e-8
    if x1==x2: return min(x3,x4)-1e-8<=x1<=max(x3,x4)+1e-8 and min(y1,y2)-1e-8<=y3<=max(y1,y2)+1e-8
    return min(x1,x2)-1e-8<=x3<=max(x1,x2)+1e-8 and min(y3,y4)-1e-8<=y1<=max(y3,y4)+1e-8
def hits_interior(seg,n):
    (x1,y1),(x2,y2)=seg; l,r=n['x']-n['w']/2,n['x']+n['w']/2; b,t=n['y']-n['h']/2,n['y']+n['h']/2
    if x1==x2: return l+1e-8<x1<r-1e-8 and max(min(y1,y2),b)<min(max(y1,y2),t)-1e-8
    return b+1e-8<y1<t-1e-8 and max(min(x1,x2),l)<min(max(x1,x2),r)-1e-8
geometry=[]
for v in V:
    segments=[]
    for i,e in enumerate(v['edges']):
        for a,b in zip(e['points'],e['points'][1:]):
            assert a[0]==b[0] or a[1]==b[1],(v['name'],'diagonal',a,b)
            for n in v['nodes']: assert not hits_interior((a,b),n),(v['name'],'line through node',n['id'])
            segments.append((i,(a,b)))
    for (i,s),(j,t) in combinations(segments,2):
        if i!=j: assert not intersects(s,t),(v['name'],'crossing or overlap',i,j,s,t)
    geometry.append({'view':v['name'],'relationships':len(v['edges']),'orthogonal':True,'crossings':0,'lines_through_entities':0})
(S/'verification/diagram_geometry.json').write_text(json.dumps(geometry,ensure_ascii=False,indent=2),encoding='utf-8')
(S/'diagrams/diagram_layouts.json').write_text(json.dumps(V,ensure_ascii=False,indent=2),encoding='utf-8')

def lines(n):
    e=n['entity']; result=[NAMES[e].replace('--','-'),','.join(PK[e])]
    if e=='salon': result+=['{Фото интерьера: путь,','подпись, порядок, видимость}']
    if e=='master': result+=['{Фото работ: путь,','подпись, порядок, видимость}']
    if e=='master_service': result+=['M:N: master ↔ salon_service']
    if e=='moderation_decision': result+=['4 целевых FK: XOR','photo_path необязателен']
    return result
def cardinal_position(e,side):
    x,y=e['points'][0 if side==0 else -1]; a=e['start'] if side==0 else e['end']
    dx={'E':.36,'W':-.36,'N':.3,'S':.3,'NW':-.2,'NE':.2,'SW':-.2,'SE':.2}[a]
    dy={'E':.25,'W':.25,'N':.3,'S':-.3,'NW':.3,'NE':.3,'SW':-.3,'SE':-.3}[a]
    return x+dx,y+dy

for font,path in [('Dia','arial.ttf'),('DiaBold','arialbd.ttf')]: pdfmetrics.registerFont(TTFont(font,'C:/Windows/Fonts/'+path))
TMP=S/'tmp'; TMP.mkdir(exist_ok=True)
DIAGRAMS={}
for v in V:
    xmin=min(n['x']-n['w']/2 for n in v['nodes'])-.65
    xmax=max(n['x']+n['w']/2 for n in v['nodes'])+.65
    ymin=min(n['y']-n['h']/2 for n in v['nodes'])-.7
    ymax=max(n['y']+n['h']/2 for n in v['nodes'])+.7
    scale=48; width=(xmax-xmin)*scale; height=(ymax-ymin)*scale
    convert=lambda p:((p[0]-xmin)*scale,(ymax-p[1])*scale)
    svg=[f'<svg xmlns="http://www.w3.org/2000/svg" width="{width:.0f}" height="{height:.0f}" viewBox="0 0 {width:.2f} {height:.2f}">','<rect width="100%" height="100%" fill="white"/>']
    tikz=[r'\begingroup\setstretch{1}\begin{tikzpicture}[x=1cm,y=1cm, entity/.style={draw,rounded corners=1pt,fill=gray!3,align=center,text width=3.4cm,minimum width=3.6cm,minimum height=2.2cm,font=\small,inner sep=2pt,outer sep=0pt}]']
    c=canvas.Canvas(str(TMP/(v['name']+'.pdf')),pagesize=(width,height))
    for e in v['edges']:
        pts=[convert(p) for p in e['points']]
        svg.append('<polyline points="'+' '.join(f'{x:.2f},{y:.2f}' for x,y in pts)+'" fill="none" stroke="#35404b" stroke-width="1.3"/>')
        path=c.beginPath(); path.moveTo(pts[0][0],height-pts[0][1])
        for x,y in pts[1:]: path.lineTo(x,height-y)
        c.drawPath(path)
        tikz.append(r'\draw '+' -- '.join(f'({x},{y})' for x,y in e['points'])+';')
        for side,value in [(0,e['pa']),(1,e['pb'])]:
            x,y=cardinal_position(e,side); px,py=convert((x,y))
            svg.append(f'<text x="{px:.2f}" y="{py:.2f}" text-anchor="middle" dominant-baseline="middle" font-family="Arial" font-size="11">{html.escape(value)}</text>')
            c.setFont('Dia',8); c.drawCentredString(px,height-py-2,value)
            tikz.append(fr'\node[fill=white,inner sep=1pt,font=\scriptsize] at ({x},{y}) {{{value}}};')
        if e['label']:
            # Label horizontal portion only, so no label overlaps the vertical FK branch.
            horizontal=[(a,b) for a,b in zip(e['points'],e['points'][1:]) if a[1]==b[1]]
            a,b=max(horizontal,key=lambda z:abs(z[0][0]-z[1][0]))
            x,y=(a[0]+b[0])/2,a[1]+.45
            px,py=convert((x,y)); svg.append(f'<text x="{px:.2f}" y="{py:.2f}" text-anchor="middle" font-family="Arial" font-size="10">{html.escape(e["label"])}</text>')
            c.setFont('Dia',7); c.drawCentredString(px,height-py,e['label'])
            tikz.append(fr'\node[font=\scriptsize,fill=white,inner sep=1pt] at ({x},{y}) {{{code(e["label"])}}};')
    for n in v['nodes']:
        px,py=convert((n['x']-n['w']/2,n['y']+n['h']/2)); nw,nh=n['w']*scale,n['h']*scale
        svg.append(f'<rect x="{px}" y="{py}" width="{nw}" height="{nh}" rx="3" fill="#f6f7f8" stroke="#35404b" stroke-width="1.3"/>')
        c.setFillColorRGB(.97,.975,.98); c.rect(px,height-py-nh,nw,nh,fill=1,stroke=1); c.setFillColorRGB(0,0,0)
        text=lines(n)
        if pdfmetrics.stringWidth(text[0],'DiaBold',11)>nw-12:
            words=text[0].split(); wrapped=[]; current=''
            for word in words:
                candidate=(current+' '+word).strip()
                if current and pdfmetrics.stringWidth(candidate,'DiaBold',11)>nw-12:
                    wrapped.append(current); current=word
                else: current=candidate
            wrapped.append(current); text=wrapped+text[1:]
        for i,line in enumerate(text):
            # Split composite keys at a comma, keeping each identifier complete.
            if i==1 and len(line)>24:
                parts=line.split(','); text=text[:i]+parts+text[i+1:]; break
        top=py+nh/2-(len(text)-1)*9
        for i,line in enumerate(text):
            yy=top+i*18
            svg.append(f'<text x="{px+nw/2}" y="{yy}" text-anchor="middle" dominant-baseline="middle" font-family="Arial" font-size="{11 if i==0 else 9}" font-weight="{"bold" if i==0 else "normal"}">{html.escape(line)}</text>')
            c.setFont('DiaBold' if i==0 else 'Dia',11 if i==0 else 9); c.drawCentredString(px+nw/2,height-yy-3,line)
        title={'moderation_decision':r'Решение\\модерации','salon_photo':r'Фото интерьера\\(атрибут)',
               'master_photo':r'Фото работ\\(атрибут)','master_invitation':r'Приглашение\\(техническое)'}.get(n['entity'],tex(NAMES[n['entity']]))
        latextext=r'\textbf{'+title+'}'+r'\\{\scriptsize '+r'\\'.join(code(k) for k in PK[n['entity']])+'}'
        if n['entity'] in ('salon','master'):
            photo_label='Фото интерьера' if n['entity']=='salon' else 'Фото работ'
            latextext+=r'\\{\scriptsize \{'+photo_label+r':\\путь, подпись,\\порядок, видимость\}}'
        if n['entity']=='master_service': latextext+=r'\\{\scriptsize M:N: мастер и услуга}'
        if n['entity']=='moderation_decision': latextext+=r'\\{\scriptsize XOR: одна цель}\\{\scriptsize '+code('photo_path')+'}'
        tikz.append(fr'\node[entity] ({n["id"]}) at ({n["x"]},{n["y"]}) '+'{'+latextext+'};')
    svg.append('</svg>'); (S/'diagrams'/(v['name']+'.svg')).write_text('\n'.join(svg),encoding='utf-8')
    tikz.append(r'\end{tikzpicture}\endgroup'); DIAGRAMS[v['name']]='\n'.join(tikz)
    (S/'diagrams'/(v['name']+'.tikz')).write_text(DIAGRAMS[v['name']],encoding='utf-8')
    c.save(); d=pdfium.PdfDocument(str(TMP/(v['name']+'.pdf'))); d[0].render(scale=1.8).to_pil().save(S/'diagrams'/(v['name']+'.png'))

PREAMBLE=r'''\documentclass[12pt,a4paper]{article}
\usepackage{fontspec}
\IfFontExistsTF{Times New Roman}{\setmainfont{Times New Roman}\newfontfamily\cyrillicfont{Times New Roman}}{\setmainfont{CMU Serif}\newfontfamily\cyrillicfont{CMU Serif}}
\IfFontExistsTF{Arial}{\setsansfont{Arial}\newfontfamily\cyrillicfontsf{Arial}}{\setsansfont{CMU Sans Serif}\newfontfamily\cyrillicfontsf{CMU Sans Serif}}
\IfFontExistsTF{Courier New}{\setmonofont{Courier New}\newfontfamily\cyrillicfonttt{Courier New}}{\setmonofont{CMU Typewriter Text}\newfontfamily\cyrillicfonttt{CMU Typewriter Text}}
\usepackage{polyglossia}\setdefaultlanguage{russian}\setotherlanguage{english}
\usepackage[left=30mm,right=15mm,top=20mm,bottom=20mm]{geometry}
\usepackage{amsmath,array,longtable,booktabs,enumitem,setspace,pdflscape,tikz,hyperref}
\hypersetup{unicode=true,colorlinks=true,linkcolor=black,urlcolor=blue,pdftitle={База данных платформы салонов красоты. Этап 2},pdfauthor={Чэнь Хаолинь, Павлов Эдгар}}
\onehalfspacing\setlength{\parindent}{1.25cm}\setlength{\emergencystretch}{3em}\setlist{nosep,leftmargin=*}
\newcolumntype{L}[1]{>{\raggedright\arraybackslash}p{#1}}\renewcommand{\arraystretch}{1.08}
\AtBeginEnvironment{longtable}{\small\setstretch{1.05}}
\newcommand{\reserve}{\par\ifdim\pagegoal<\dimexpr\pagetotal+7\baselineskip\relax\newpage\fi}
\begin{document}
\begin{titlepage}\centering
Федеральное государственное автономное\\образовательное учреждение высшего образования\\
\textbf{«Национальный исследовательский университет ИТМО»}\vfill
Информационные системы\\[0.5\baselineskip]\textbf{Курсовая работа. Этап 2}\\[0.5\baselineskip]
Информационная система поиска салонов красоты\\и онлайн-записи на услуги\\[0.5\baselineskip]
\textbf{Проектирование и реализация базы данных PostgreSQL}\vfill
\begin{flushright}Выполнили:\\Чэнь Хаолинь P3216 407960\\Павлов Эдгар P3316 409297\\Преподаватель:\\Коновалов Арсений Антонович\end{flushright}
\vspace{4\baselineskip}г. Санкт-Петербург, 2026\end{titlepage}
\setcounter{page}{2}{\small\setstretch{1.05}\tableofcontents}\clearpage
'''
INTRO=r'''\section{Постановка задачи и границы работы}
Второй этап включает следующие задания:
\begin{enumerate}
\item Сформировать ER-модель на основе предметной области и прецедентов предыдущего этапа: не менее десяти сущностей и хотя бы одна связь «многие ко многим».
\item Согласовать ER-модель с преподавателем и построить даталогическую модель.
\item Реализовать даталогическую модель в PostgreSQL.
\item Обеспечить целостность средствами DDL и триггеров.
\item Подготовить создание и удаление базы, заполнение тестовыми данными.
\item Предложить и реализовать функции и процедуры PL/pgSQL для критических запросов.
\item Создать и обосновать индексы в контексте прецедентов первого этапа.
\item Составить отчёт о проектировании, реализации и проверке.
\end{enumerate}

Платформа объединяет несколько салонов одного города. Учётная запись имеет ровно одну роль: клиент, мастер, владелец или администратор. Владелец управляет одним салоном; мастер работает в одном салоне. Запись включает одного клиента, одного мастера и одну услугу. Цена и длительность принадлежат услуге салона, общие виды услуг используются для сравнения.

Время определяется в едином часовом поясе Europe/Moscow; цены задаются в рублях. Рабочие интервалы относятся к конкретной дате без перехода через полночь. Новая запись возможна на 30 календарных дней, включая текущий день. Начала идут с шагом 15 минут, длительность услуги не обязана делиться на 15. Оплата, чаты, филиалы и учёт оборудования в модель не входят.

\section{Концептуальная ER-модель}
В модели \textbf{11 сущностей}. Фотографии интерьера являются составным многозначным атрибутом салона, фотографии работ --- аналогичным атрибутом мастера. Элемент содержит путь, подпись, порядок и видимость; файл хранится вне базы. Отдельной концептуальной сущности «Фотография» нет. Имя мастера берётся из его пользователя.

Сущность «Мастер--услуга» представляет связь M:N внутри одного салона. Один мастер выполняет несколько услуг, одну услугу выполняют несколько мастеров. Составной ключ пары исключает повторные назначения. Например, Анна и Мария выполняют маникюр, а Анна дополнительно выполняет педикюр: имеются три пары, что демонстрирует множественность с обеих сторон.
'''
PURPOSE={'user_account':'Учётная запись, уникальная почта, хеш пароля, роль и состояние доступа.','district':'Район единственного города.','salon':'Владелец, адрес, координаты, контакты, публикация и фотографии интерьера.','service_type':'Общий вид сопоставимых услуг.','salon_service':'Услуга конкретного салона, текущие цена и длительность.','master':'Профессиональный профиль пользователя, салон и фотографии работ.','master_service':'Уникальная пара мастера и услуги; активность назначения.','work_interval':'Непересекающийся рабочий интервал мастера на конкретную дату.','appointment':'Участники, время, снимки условий и состояние посещения.','review':'Тип цели и оценка выполненной записи; автор и цель определяются через запись.','moderation_decision':'Администратор, одна цель, действие, причина, время и необязательный путь фотографии.'}
parts=[PREAMBLE,INTRO,table(['Сущность','Назначение'],[[NAMES[x],PURPOSE[x]] for x in CORE],[4,10.8]),
 r'''PK --- первичный ключ; FK --- внешний ключ; UQ --- уникальность. Число у конца линии обозначает количество экземпляров этого конца для одного экземпляра противоположного конца: 1, 0..1, 0..N, 0..2. Кратность 0..2 для отзывов дополнительно обеспечивается двумя типами цели и уникальностью пары «запись--тип».

Четыре следующих представления образуют одну ER-модель. Повторяющиеся рамки обозначают тот же объект, а не новую сущность. Все отношения представлены горизонтальными и вертикальными отрезками без пересечений. Многозначные атрибуты фотографий указаны внутри рамок в фигурных скобках.''']
for i,v in enumerate(V[:4],1):
    parts += [r'\clearpage\begin{landscape}',r'\subsection{'+v['title']+'}',r'\begin{center}',DIAGRAMS[v['name']],r'\end{center}']
    if i==1: parts.append('Роль OWNER применяется к связи владения, роль MASTER --- к связи профессионального профиля. Ноль салонов у владельца допустим до регистрации организации.')
    if i==2: parts.append('Назначение услуги мастеру имеет составной PK. Запись ссылается на обе его части. Отмена сохраняет запись и освобождает время; отзывы разрешаются только после выполнения.')
    if i==3: parts.append('Администратор решения обязателен; из четырёх целевых ссылок заполнена ровно одна (XOR). Для фотографии дополнительно сохраняется путь элемента атрибута целевого салона или мастера.')
    if i==4: parts.append('Инициатор отмены обязателен только при отмене, автор результата --- при выполнении или неявке. Полномочия определяются ролью и принадлежностью записи.')
    parts += [r'\end{landscape}\clearpage']
parts += [r'''\section{Согласование и переход к даталогической модели}
ER-модель подготовлена для согласования с преподавателем. Фактическое согласование ещё не зафиксировано; даталогическая модель и реализация являются подготовленным вариантом для рассмотрения. Проверки программы не заменяют решения преподавателя.
''',table(['Параметр','Запись'],[['Статус','Ожидает согласования'],['Дата обсуждения','Заполняется после обсуждения'],['Результат и замечания','Заполняются преподавателем или по результатам встречи'],['Пункты для подтверждения','11 сущностей; M:N; фотографии как многозначные атрибуты; одна роль и один салон; отзывы и сохранение истории.']],[4,10.8]),
 r'''\subsection{Преобразование отношений}
Каждая из 11 сущностей преобразована в основную таблицу. Для двух многозначных атрибутов выделены отношения salon\_photo и master\_photo с ключами «родитель--путь файла». Это преобразование атрибутов для выполнения первой нормальной формы, а не изменение числа концептуальных бизнес-сущностей.

Техническая таблица master\_invitation реализует одноразовое приглашение из прецедентов регистрации и управления салоном. Она содержит хеш токена, сроки, использование и отзыв. Итого в PostgreSQL \textbf{14 таблиц}: 11 основных, две для атрибутов фотографий и одна техническая.

Связь M:N преобразована в master\_service с составным PK; запись имеет составной FK на него. Отдельные клиент, владелец и администратор не вводятся как таблицы: это роли пользователя. Автор отзыва, конкретный мастер и салон определяются по неизменной записи. Идентификаторы этих объектов в отзыве не дублируются.

Для модерации фотографии имеются составные FK «target\_salon\_id, photo\_path» и «target\_master\_id, photo\_path». При отсутствии пути действует обычная целевая ссылка. При указанном пути FK проверяет существование именно элемента атрибута данного родителя.
''']
for v in V[4:]:
    parts += [r'\clearpage\begin{landscape}',r'\subsection{'+v['title']+'}',r'\begin{center}',DIAGRAMS[v['name']],r'\end{center}',
              'На этом представлении показаны отношения даталогической модели. Рамки элементов атрибутов и технического приглашения не добавляются к числу 11 концептуальных сущностей.',r'\end{landscape}\clearpage']
parts += [r'''\section{Таблицы, ключи и нормализация}
В таблицах далее «?» означает NULL, PK --- первичный ключ, FK --- ссылка, UQ --- уникальность, G --- вычисляемый сохраняемый столбец. Составные ключи и ссылки перечислены после атрибутов. Все внешние ключи используют ON DELETE RESTRICT. Физические типы и ограничения соответствуют созданной схеме.
''']
for name in NAMES:
    parts += [r'\reserve\subsection{'+NAMES[name]+' ('+code(name)+')}',table(['Атрибут','Тип','Признаки'],[[code(c['name']),
      code('tsrange' if c['udt']=='tsrange' else 'timestamp (MSK)' if c['type']=='timestamp without time zone' else
           'numeric('+str(c['precision'])+','+str(c['scale'])+')' if c['type']=='numeric' else c['type']),
      ', '.join((['PK'] if c['name'] in PK[name] else [])+(['FK'] if any(x['table']==name and x['kind']=='f' and c['name'] in re.search(r'\(([^)]+)\)',x['definition'])[1].split(', ') for x in M['constraints']) else [])+
                (['?'] if c['nullable'] else ['NOT NULL'])+(['G'] if c['generated']=='ALWAYS' else []))]
      for c in TABLES[name]['columns']],[5.8,5.1,3.9])]
    definitions=[x['definition'] for x in M['constraints'] if x['table']==name and x['kind'] in ('p','u','f','x')]
    parts.append(r'\noindent{\footnotesize\raggedright '+r'\par '.join(code(d) for d in definitions)+r'\par}')
parts += [r'''\subsection{Функциональные зависимости}
Идентификатор услуги салона определяет салон, вид, название, цену и длительность. Пара «мастер--услуга» определяет активность назначения. Идентификатор записи определяет её участников, момент начала, снимки условий и состояние. Уникальная пара «запись--тип цели» определяет отзыв. В основных отношениях не хранятся имена владельца, клиента и мастера, выводимые из пользователя.

Отдельные строки фотографий устраняют повторяющиеся группы и обеспечивают 1НФ. Основные хранимые бизнес-атрибуты имеют зависимости от ключей, соответствующие 3НФ. Снимки цены и длительности относятся к факту подтверждения конкретной записи и не являются копией актуального каталога, которая должна обновляться вместе с ним. Это намеренное сохранение истории.

Окончание записи и интервальный столбец slot являются контролируемыми производными: PostgreSQL вычисляет их автоматически из начала и длительности. Избыточность этих служебных представлений используется для проверки времени и GiST-поиска; пользователь не может задать противоречивое окончание. Рейтинги и свободные начала вычисляются, отдельными таблицами не хранятся.

\section{Целостность данных и транзакции}
\subsection{Декларативные ограничения}
PK обеспечивает идентификацию; уникальные ограничения --- почту, единственный салон владельца, единственный профиль пользователя, повтор назначения и отзыва. CHECK ограничивает роли, состояния, положительную длительность, неотрицательную цену, оценку 1--5, шаг начала, структуру сведений об отмене и результате, XOR целей и формат метаданных файлов.

Два ограничения EXCLUDE USING gist используют расширение btree\_gist. Рабочие интервалы одного мастера не пересекаются. Записи одного мастера со статусом, отличным от CANCELLED, не пересекаются, включая сохранённую историю. Интервалы полуоткрытые: [start, end), поэтому соседние посещения разрешены. Проверка действует и при конкурентных транзакциях.
''',table(['Правило','Средство'],[
 ['Одна роль пользователя; корректные состояния','CHECK; запрет смены роли и идентичности триггером.'],
 ['Один владелец и один профиль','UQ внешних ключей; проверка OWNER и MASTER триггером.'],
 ['Мастер выполняет услугу своего салона','Составной PK назначения; FK записи на пару; триггер принадлежности.'],
 ['Нет пересечений времени','GiST EXCLUDE для рабочего времени и неотменённых записей.'],
 ['Полная услуга в одном рабочем интервале','Триггер записи; проверка диапазона, активности, публикации, даты и горизонта.'],
 ['Нет изменения подтверждённых условий',r'Триггер неизменности участников, начала и снимков; generated end\_at и slot.'],
 ['Допустимые статусы и права','Триггер переходов, времени и инициатора; API отмены и обработки результата.'],
 ['Изменение графика и отключение не нарушают записи','Триггер защиты подтверждённых записей, ещё не завершившихся по времени.'],
 ['Только выполненная запись допускает отзыв','Триггер статуса; API проверяет автора; UQ «запись--тип».'],
 ['До двух независимых отзывов','CHECK двух типов и UQ пары; скрытие не освобождает пару.'],
 ['Фотографии и аудит','Составные PK и FK атрибутов; лимит 20, метаданные JPEG/PNG до 5 МБ; только архивирование.'],
 ['Одноразовый токен','UQ хеша; один открытый токен на мастера; сроки и неизменность завершённого приглашения.'],
 ['Ровно одна цель модерации',r'CHECK num\_nonnulls=1; четыре FK; две составные ссылки на элементы фотографий.']],[6,8.8]),
 r'''\subsection{Конкурирующие изменения}
В учебной реализации все бизнес-записи получают один транзакционный advisory lock (407960, 409297). Statement-триггеры берут его до блокировок строк; API получает его до чтения изменяемых условий. Затем проверка и изменение происходят в одной транзакции READ COMMITTED. После ожидания следующий запрос видит зафиксированное состояние. Другой уровень изоляции для бизнес-записи явно отклоняется, чтобы не использовать устаревший снимок.

Такой порядок упрощает согласование записи, графика, каталога, ограничений доступа, квот фото и токенов и не блокирует обычные читающие запросы. Цена решения --- последовательное выполнение изменений всей платформы. Это сознательное ограничение учебной версии; производительность при 20 параллельных клиентах не подтверждена этими проверками. Для масштабирования потребуется согласованный порядок блокировок отдельных салонов и мастеров с повторной проверкой гонок.

Полуоткрытый диапазон записи имеет конец start\_at + duration\_snapshot минут. Новая запись получает CONFIRMED; отмена разрешена только до начала. Выполнение или неявка отмечаются мастером либо владельцем только после планового окончания. Переход по одному лишь наступлению времени не выполняется. Конечные состояния в обычном API не меняются.

Снятие салона с публикации и блокировка учётной записи мастера сохраняют существующие записи. Владелец может урегулировать их. Администратор отменяет будущую запись в исключительном случае блокировки владельца; причина обязательна. Деактивация профиля или услуги владельцем, напротив, отклоняется при затрагивании ещё не завершённой подтверждённой записи.

\subsection{Доступ и граница ответственности}
Бизнес-процедуры выполняются с правами владельца (SECURITY DEFINER) и фиксированным search\_path. Общая роль PUBLIC не имеет доступа к схеме, таблицам, последовательностям и функциям. Доверенная серверная роль получает право использования схемы и вызова разрешённых процедур. Прямой DML и закрытые помощники ей не выдаются.

Идентификатор актора передаёт доверенный backend после аутентификации пользователя. Произвольный клиент не должен получать доступ к этой роли: переданный идентификатор сам по себе не удостоверяет личность. Функции проверяют бизнес-роль, активность и принадлежность объектов; браузерные сессии, CSRF и управление серверными секретами относятся к последующей реализации приложения.

База проверяет метаданные изображения. Файловый сервис проверяет само содержимое JPEG и PNG, удаляет EXIF, выбирает безопасное имя и согласует файл с транзакцией. Синтетические тестовые пути не являются загруженными изображениями.

\section{Критические функции и процедуры}
''']
API={
 'register_user':('П1','Создание клиента или владельца; нормализация почты, salted bcrypt.'),'authenticate':('П1','Проверка пароля и активности без возврата хеша.'),
 'invite_master':('П1, П8','Атомарное создание ожидающего активации пользователя, профиля и хеша токена.'),'reissue_invitation':('П1, П8','Отзыв предыдущего токена и выдача нового.'),'accept_invitation':('П1','Проверка срока, однократное использование, установка пароля и активация.'),
 'available_slots':('П3, П4, П12','Свободные начала для конкретной пары мастер--услуга и даты; интервал и занятость.'),'book_appointment':('П4, П12','Повторная проверка условий, снимки, атомарное предотвращение конфликта.'),
 'cancel_appointment':('П5, П10','Права, время, причина и идемпотентная отмена.'),'mark_visit':('П10','Выполнение или неявка после окончания.'),'add_review':('П6','Автор, выполненная запись, отдельная оценка и уникальность цели.'),
 'moderate':('П7, П11','Состояние объекта и неизменяемое решение в одной транзакции; путь элемента фото.'),
 'set_master_service':('П8','Назначение или деактивация пары своего салона.'),'save_work_interval':('П8','Создание и изменение графика с защитой записей.'),'delete_work_interval':('П8','Удаление интервала только без нарушения записей.'),
 'save_service':('П8','Каталог своего салона; защита будущих записей при отключении.'),'save_master_profile':('П8, П9','Разрешённое изменение опыта и специализации.'),'create_salon':('П7','Заявка владельца с адресом и координатами.'),'resubmit_salon':('П7','Повторная подача возвращённой заявки.'),
 'put_photo':('П8, П9','Загрузка элемента атрибута с проверкой актора и метаданных.'),'archive_photo':('П8, П9','Архивирование фотографии с сохранением аудита.'),'search_salons':('П2','Единый набор фильтров; тип и цена одной услуги; район, карта или радиус; доступность.'),'appointment_journal':('П5, П9, П10','Личные записи или журнал собственного салона без реквизитов учётных записей.')}
parts.append(table(['Функция / процедура','Прецеденты','Назначение'],[[code(k),v[0],v[1]] for k,v in API.items()],[5.1,2.1,7.6]))
parts += [r'''Пишущие функции и процедуры реализованы PL/pgSQL. available\_slots использует SQL, так как подбор выражается одним запросом. Публичный поиск возвращает единый отсортированный набор: список применяет LIMIT/OFFSET, маркеры получают тот же набор без страничного ограничения. При выборе даты проверяется наличие подходящего мастера для той же услуги, которая удовлетворяет цене и типу. Опубликованный салон без каталога виден только при отсутствии фильтров, требующих услуги.

Рейтинги представлены отдельными view salon\_rating и master\_rating. В них учитываются только опубликованные отзывы соответствующего типа. Отсутствие строки означает отсутствие оценки, а не нулевой рейтинг. Изменение видимости отзыва меняет результат view и не позволяет повторить отзыв по той же паре.

\section{Индексы и анализ прецедентов}
Первичные, уникальные и exclusion-ограничения сами создают необходимые индексы. Они не дублируются обычными индексами. Дополнительно создано 19 индексов запросов и один частичный уникальный индекс открытых приглашений. В базе всего 43 индекса, включая индексы ограничений.
''']
INDEX_PURPOSE={
 'idx_salon_public_district':'П2: фильтр района по опубликованной части каталога.', 'idx_salon_public_coordinates':'П2: ограничение прямоугольником карты; координаты позволяют предварительно сузить выборку.',
 'idx_service_salon_type_price':'П2, П3: подходящие услуги внутри салона и минимальная цена.', 'idx_service_type_price':'П2: вид услуги и диапазон цены с возвратом салонов.',
 'idx_master_salon':'П3, П8: активные мастера своего салона.', 'idx_assignment_service':'П3, П4: мастера выбранной услуги; обратный порядок к составному PK.',
 'idx_work_master_date':'П4, П9, П12: рабочие интервалы одного мастера в выбранную дату.', 'idx_appointment_client_time':'П5: история клиента и сортировка по времени.',
 'idx_appointment_master_time':'П9, П10: расписание мастера за день и история посещений.', 'idx_appointment_service_future':'П8: защита активной услуги при изменениях; только подтверждённые записи.',
 'idx_appointment_busy':'П4, П12: пересечение с небольшой подтверждённой частью истории; GiST по диапазону.',
 'idx_review_published_target':'П3, П6, П11: отдельные рейтинги и опубликованные отзывы нужной цели.',
 'idx_salon_photo_visible':'П3: видимые элементы интерьера в порядке показа.', 'idx_master_photo_visible':'П3: видимые работы мастера в порядке показа.',
 'idx_moderation_user':'П11: история решений по пользователю.', 'idx_moderation_salon':'П7, П11: история заявки и публикации салона.',
 'idx_moderation_master':'П11: история ограничений профиля и работ.', 'idx_moderation_review':'П11: история скрытия и восстановления отзыва.',
 'idx_invitation_master_history':'П1, П8: история и повторная выдача приглашений.', 'uq_invitation_open':'П1: не более одного неиспользованного и неотозванного токена мастера.'}
parts.append(table(['Индекс','Обоснование'],[[code(k),v] for k,v in INDEX_PURPOSE.items()],[6.8,8]))
def plan_indexes(n): return ([n['Index Name']] if 'Index Name' in n else [])+sum([plan_indexes(x) for x in n.get('Plans',[])],[])
LABELS={'client_history':'История клиента','master_day':'Посещения мастера за день','working_date':'Рабочие интервалы даты','busy_overlap':'Проверка пересечения','service_and_price':'Вид услуги и цена'}
parts += [r'\reserve\subsection{Проверка планов запросов}',table(['Запрос','Фактически выбранные индексы','Время, мс'],
 [[LABELS[k],r'\par '.join(code(x) for x in plan_indexes(v['explain'][0]['Plan'])),str(v['explain'][0]['Execution Time'])] for k,v in PLANS.items()],[4.3,8.1,2.4]),
 r'''Планы получены EXPLAIN (ANALYZE, BUFFERS, FORMAT JSON) без отключения последовательного сканирования. Они подтверждают использование индексов в пяти характерных запросах на тестовых данных. Время относится к локальным SQL-запросам, без HTTP, сети, файлов и параллельной нагрузки, и не является подтверждением целевого SLA первого этапа.

B-tree полезен для равенств, диапазона даты и сортировки; GiST --- для оператора пересечения диапазонов. Частичные индексы сокращают обработку неопубликованных объектов, скрытых отзывов и завершённой истории. В маленьких справочниках или таблицах аудита планировщик может предпочесть последовательное сканирование. Индекс координат не заменяет географический индекс для большого объёма и не ускоряет сам расчёт расстояния по радиусу; расстояние вычисляется по отобранным кандидатам.

\section{Скрипты и воспроизведение}
Основные файлы в каталоге sql:
''',table(['Файл','Назначение'],[[code(x),y] for x,y in [
 ('00_create_database.sql','Создание явно указанной UTF-8 базы; запуск из postgres вне транзакции.'),('01_tables.sql','Схема, расширения, 14 таблиц, ключи, проверки и исключения.'),('02_seed.sql','Синтетическая история и данные каталога для новой базы.'),('03_integrity.sql','Триггеры, блокировка и защищённые помощники.'),('04_routines.sql','Бизнес-функции, процедуры и представления рейтингов.'),('05_indexes.sql','19 индексов запросов.'),('06_grant_backend.sql','EXECUTE API для существующей доверенной серверной роли.'),('install.sql','Атомарная установка с необязательными демоданными, ограничение прав и ANALYZE.'),('99_drop_database.sql','Удаление указанной базы без FORCE и завершения чужих сеансов.')]], [6,8.8]),
 r'''\subsection{Порядок запуска}
Нужны PostgreSQL и psql; установка проверена на версии 17.4. Пользователь установки должен владеть базой и иметь права на создание схемы и расширений btree\_gist и pgcrypto. Для создания базы нужно CREATEDB; на учебном сервере можно установить схему в уже выделенную базу, пропустив создание.

Следующие команды выполняются из каталога второго этапа. HOST и USER заменяются параметрами своего сервера:
{\footnotesize\begin{verbatim}
psql -h HOST -U USER -d postgres \
  -v db_name=beauty_course -f sql/00_create_database.sql
psql -h HOST -U USER -d beauty_course \
  -v with_demo_data=true -f sql/install.sql
psql -h HOST -U USER -d beauty_course \
  -v backend_role=EXISTING_SERVER_ROLE -f sql/06_grant_backend.sql
psql -h HOST -U USER -d postgres \
  -v db_name=beauty_course -f sql/99_drop_database.sql
\end{verbatim}}
Без with\_demo\_data=true создаётся пустая рабочая схема. Исторические демоданные загружаются между созданием таблиц и установкой бизнес-триггеров, в одной транзакции install. Декларативные ограничения всё время включены, дополнительно проверяются принадлежность назначения, выполнение оцениваемого посещения и рабочие интервалы истории. Этот путь предназначен для новой демонстрационной базы, а не для импорта в существующую рабочую базу. Флаг обхода проверок в обычном API отсутствует.

Скрипты PowerShell создают и удаляют базу, компилируют отчёт и запускают тесты. Тестовая программа создаёт проектный кластер с отдельным портом и локальным доступом. Она не подключается к установленной пользовательской службе. По завершении тестовый сервер остановлен. Воспроизведение на helios в данной работе не заявляется.

\section{Результаты проверки}
\subsection{Состав тестовых данных}
Данные синтетические, адреса электронной почты используют домен example.test. История привязана к дате установки, поэтому будущие интервалы остаются доступными при повторном запуске на новой базе. Фотографии представлены метаданными, без внешних файлов. В наборе есть завершения, неявки, отмены, ещё не обработанные прошлые записи, будущие записи, скрытый отзыв, заблокированный мастер и ожидающий активации профиль.
''',table(['Таблица','Строк после заполнения'],[[code(k),str(v)] for k,v in COUNTS.items()],[8,6.8]),
 r'\subsection{Функциональные и конкурентные проверки}',
 f"Выполнено {T['total']} проверок; все {T['passed']} завершились успешно. Проверялись создание базы и схемы, допустимые и запрещённые бизнес-сценарии, права серверной роли, планы запросов, установка пустой схемы и удаление отдельной тестовой базы.",
 table(['Группа','Проверенный результат'],[
 ['Время и условия','Соседние записи разрешены; пересечение, перерыв, прошлое, день за пределами горизонта и неправильный шаг отклонены. Снимки сохраняются при изменении каталога.'],
 ['Роли и принадлежность','Чужая отмена, неверная роль владельца, смена роли и салона, межсалонное назначение и доступ к чужой работе отклонены.'],
 ['Состояния и история','Ранняя отметка результата, отмена начавшейся записи, изменение конечного состояния, удаление истории и редактирование отзыва отклонены.'],
 ['График и активности','Отключение мастера, услуги и назначения, сокращение и удаление занятого графика отклонены. Свободный график изменяется.'],
 ['Отзывы и фотографии','Два типа отзывов разрешены; повтор и оценка вне диапазона отклонены. Скрытие влияет только на соответствующий рейтинг. Проверены XOR, путь фото, размер, MIME и квота.'],
 ['Приглашения и доступ','Занятая почта, отозванный, истёкший и использованный токены отклонены; пароль проверяется; прямой доступ backend к таблицам и помощникам запрещён.'],
 ['Поиск','Тип и цена проверяются для одной услуги; георежимы взаимоисключающие; область карты и видимость салона без каталога проверены.']],[5,9.8]),
 r'''Конкурентные проверки выполнены в четырёх парах реальных серверных сеансов. Первый запрос удерживал транзакцию две секунды, второй ожидал блокировку более секунды. При одинаковом времени сохранялась одна запись; второй запрос получал ошибку пересечения (23P01). Сокращение графика после конкурентной записи отклонялось (23514). Второй одинаковый отзыв отклонялся UQ (23505). Второе использование приглашения отклонялось (22023). Эти проверки подтверждают обработку соответствующих гонок; нагрузочное испытание не проводилось.

Геометрическая проверка шести представлений зафиксировала ноль диагональных сегментов, ноль пересечений или перекрытий разных связей и ноль проходов через внутренность рамок. PDF дополнительно проверен после рендеринга. Машинные результаты, метаданные реально созданной схемы и JSON-планы сохранены в verification.

\clearpage\section{Заключение}
Разработана концептуальная ER-модель из 11 сущностей с M:N между мастерами и услугами салона. Фотографии сохранены как составные многозначные атрибуты; при переходе к отношениям они разложены в две таблицы элементов. С учётом технического приглашения реализованы 14 таблиц PostgreSQL.

Подготовлены DDL, триггеры, функции и процедуры, индексы, создание и удаление базы и демоданные. Проверены основные бизнес-инварианты, доступ доверенного backend и четыре конкурентных сценария. Индексы обоснованы прецедентами и фактическими планами запросов. ER-модель и переход к даталогической модели подготовлены для обсуждения; фактическое согласование с преподавателем остаётся отдельным обязательным действием.
\end{document}
''']
(S/'report/stage2_report.tex').write_text('\n\n'.join(parts),encoding='utf-8')
print(f"Generated {len(V)} orthogonal views, 11 conceptual entities and report from {len(TABLES)} live tables; crossings=0.")
