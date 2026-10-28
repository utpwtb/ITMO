"""Render UML class/package diagrams from final Java member declarations (Graphviz DOT)."""
import hashlib
import html
import json
from pathlib import Path
import re
import subprocess
ROOT=Path(__file__).resolve().parents[1]
DEST=ROOT.parent/'report/Lab2/uml'
DEST.mkdir(parents=True,exist_ok=True)
source=ROOT/'src/main/java/ru/itmo/movie'
def members(path):
    text=path.read_text(encoding='utf-8')
    fields=re.findall(r'public\s+(?!class|enum|static)([\w<>.]+)\s+(\w+)\s*(?:=[^;]*)?;',text)
    return [f'+ {name}: {type}' for type,name in fields]
def node(name,rows,stereotype=''):
    title=html.escape(name)
    if stereotype:title=html.escape('«'+stereotype+'»')+'<BR/>'+title
    label='<TABLE BORDER="0" CELLBORDER="1" CELLSPACING="0" CELLPADDING="6"><TR><TD BGCOLOR="#e8edf1"><B>'+title+'</B></TD></TR><TR><TD ALIGN="LEFT">'+'<BR ALIGN="LEFT"/>'.join(html.escape(r) for r in rows)+'</TD></TR></TABLE>'
    return '"'+name+'" [label=<'+label+'>];'
def render(name,nodes,edges,direction="LR"):
    lines=['digraph UML {','graph [rankdir='+direction+',bgcolor="white",nodesep=0.4,ranksep=0.65,pad=0.2];','node [shape=plain,fontname="Arial",fontsize=11];','edge [fontname="Arial",fontsize=10,arrowsize=0.8];']+nodes+edges+['}']
    path=DEST/(name+'.dot');path.write_text('\n'.join(lines),encoding='utf-8')
    for fmt in ('pdf','png','svg'):subprocess.run(['dot','-T'+fmt,str(path),'-o',str(DEST/(name+'.'+fmt))],check=True)
domain=['Movie','Person','Coordinates','Location','AppState']
render('classes-domain',[node(n,members(source/'domain'/(n+'.java')),'entity') for n in domain],['Movie -> Coordinates [label="coordinates 1",arrowhead=vee];','Movie -> Person [label="director / screenwriter / operator 0..1",arrowhead=vee];','Person -> Location [label="location 0..1",arrowhead=vee];'])
nodes=[node(n,members(source/'domain'/(n+'.java')),'entity') for n in ['AppUser','ImportOperation']]
nodes += [node('UserRole',['USER','ADMIN'],'enumeration'),node('ImportStatus',['RUNNING','SUCCESS','FAILED'],'enumeration')]
render('classes-history',nodes,['ImportOperation -> AppUser [label="user 1",arrowhead=vee];','AppUser -> UserRole [style=dashed,arrowhead=vee];','ImportOperation -> ImportStatus [style=dashed,arrowhead=vee];'])
spec={
 'ImportResource':['+ upload(): Response','+ list(page, size): Object','+ get(id): Object'],
 'ImportService':['+ upload(user, filename, bytes): Map','- person(em, input, cache): Person','- samePerson(a, b): boolean'],
 'ImportParser':['+ parse(bytes): ImportDocument','- object(node, type, row, path): T','- value(node, type, row, path): Object'],
 'ImportDocument':['+ formatVersion: int','+ movies: List<Movie>'],
 'ImportHistoryService':['+ list(user, page, size): Map','+ get(user, id): Map','+ dto(operation): Map'],
 'MovieService':['+ save(kind, id, input): Object','+ saveInTransaction(em, kind, id, input)','+ saveImported(em, movie): Movie','+ delete / award / redistribute'],
 'MovieUniquenessValidator':['+ check(em, movie): void'],
 'MovieKey':['+ name: String','+ directorIdOrNull: Long'],
 'Database':['+ read(work): T','+ write(work): T','+ metadata(work): T','- transaction / once'],
 'AuthService':['+ identity(username): AppUser','+ register(username, password): String','+ authenticate(username, password): String']}
nodes=[node(n,rows,'record' if n in ('ImportDocument','MovieKey') else '') for n,rows in spec.items()]
edges=[f'{a} -> {b} [style=dashed,arrowhead=vee];' for a,b in [('ImportResource','ImportService'),('ImportResource','ImportHistoryService'),('ImportService','ImportParser'),('ImportService','MovieService'),('ImportService','Database'),('ImportParser','ImportDocument'),('MovieService','MovieUniquenessValidator'),('MovieService','Database'),('ImportHistoryService','Database'),('AuthService','Database'),('MovieUniquenessValidator','MovieKey')]]
render('classes-services',nodes,edges)
packages={'web':['ApiApplication, AuthFilter, ErrorMapper','AuthResource, MovieResource, ImportResource'],
 'service':['AuthService, MovieService, Problem','ImportParser (ImportDocument)','MovieUniquenessValidator (MovieKey)','ImportService, ImportHistoryService'],
 'persistence':['Database: RESOURCE_LOCAL'],
 'domain':['Movie, Person, Coordinates, Location','AppState, AppUser, ImportOperation','UserRole, ImportStatus, converters, enums'],
 'domain.validation':['ConsistentBoxOffice, BoxOfficeValidator']}
render('packages',[node(n,v,'package') for n,v in packages.items()],[f'"{a}" -> "{b}" [style=dashed,arrowhead=vee];' for a,b in [('web','service'),('service','persistence'),('service','domain'),('service','domain.validation'),('persistence','domain'),('domain','domain.validation')]],direction='TB')
(DEST/'source-hashes.json').write_text(json.dumps({str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in source.rglob('*.java')},indent=2),encoding='utf-8')
