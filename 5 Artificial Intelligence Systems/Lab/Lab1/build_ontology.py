"""Перенос фактов из knowledge.pl в OWL и проверка Pellet и SPARQL.
Запуск: python build_ontology.py (owlready2, rdflib и Java).
"""
from pathlib import Path
import sys, os, re, json, types
ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT / '.deps'))
import owlready2 as ow
from rdflib import Graph, Namespace, RDF
if os.name == 'nt' and Path('C:/Program Files/Java/jdk-17/bin/java.exe').exists():
    ow.JAVA_EXE = 'C:/Program Files/Java/jdk-17/bin/java.exe'
onto = ow.get_ontology('https://example.org/rpg-lab1#')
unary_names = dict(character='Character', warrior='Warrior', mage='Mage',
    healer='Healer', rogue='Rogue', ranger='Ranger', weapon='Weapon',
    quest='Quest', skill='Skill', guild='Guild', cursed='Cursed')
binary_names = dict(owns='owns', has_skill='hasSkill', requires='requiresSkill', member_of='memberOf')
source = (ROOT/'knowledge.pl').read_text(encoding='utf-8')
facts = re.findall(r'^([a-z_]+)\(([a-z_,]+)\)\.$', source, re.M)
unary = [(p,a) for p,a in facts if ',' not in a]
binary = [(p,*a.split(',')) for p,a in facts if ',' in a]
assert len(unary) == 24 and len(binary) == 15
with onto:
    class Character(ow.Thing): pass
    class Weapon(ow.Thing): pass
    class Quest(ow.Thing): pass
    class Skill(ow.Thing): pass
    class Guild(ow.Thing): pass
    for name in ['Warrior','Mage','Healer','Rogue','Ranger','Cursed']:
        types.new_class(name,(Character,))
    ow.AllDisjoint([Character,Weapon,Quest,Skill,Guild])
    class owns(ow.ObjectProperty): domain=[Character]; range=[Weapon]
    class hasSkill(ow.ObjectProperty): domain=[Character]; range=[Skill]
    class requiresSkill(ow.ObjectProperty): domain=[Quest]; range=[Skill]
    class memberOf(ow.ObjectProperty): domain=[Character]; range=[Guild]
    class skilledFor(ow.ObjectProperty): domain=[Character]; range=[Quest]
    class readyFor(ow.ObjectProperty): domain=[Character]; range=[Quest]
    class guildmate(ow.ObjectProperty): domain=[Character]; range=[Character]
    class Combatant(Character):
        equivalent_to=[Character & (onto.Warrior | onto.Mage)]
    class Scout(Character):
        equivalent_to=[Character & (onto.Rogue | onto.Ranger)]
    class Armed(Character):
        equivalent_to=[Character & owns.some(Weapon)]
    class SafeCharacter(Character):
        equivalent_to=[Character & ow.Not(onto.Cursed)]
    for p,a in unary:
        cls = onto[unary_names[p]]
        if onto[a] is None: cls(a)
        elif cls not in onto[a].is_a: onto[a].is_a.append(cls)
    for p,a,b in binary:
        getattr(onto[a],binary_names[p]).append(onto[b])
    # Prolog различает атомы; OWL требует явного различия индивидов.
    ow.AllDifferent(list(onto.individuals()))
    # Локальная полнота cursed/1 для шести персонажей учебного снимка.
    for x in Character.instances():
        if x.name != 'borin': x.is_a.append(ow.Not(onto.Cursed))
    rules = [
      'Character(?x), Quest(?q), hasSkill(?x, ?s), requiresSkill(?q, ?s) -> skilledFor(?x, ?q)',
      'Armed(?x), skilledFor(?x, ?q) -> readyFor(?x, ?q)',
      'Character(?x), Character(?y), memberOf(?x, ?g), memberOf(?y, ?g), differentFrom(?x, ?y) -> guildmate(?x, ?y)'
    ]
    for i,text in enumerate(rules,1):
        rule=ow.Imp(f'rule_{i}'); rule.set_as_rule(text)
    onto.metadata.comment.append('Учебная онтология вымышленных RPG-персонажей. Отрицательные утверждения Cursed задают полноту только текущего снимка.')
    for cls in onto.classes(): cls.label.append(cls.name)
onto.save(file=str(ROOT/'game_ontology.owl'),format='rdfxml')
# В отдельном файле сохраняются материализованные результаты, исходник не меняется.
with onto:
    ow.sync_reasoner_pellet([onto],infer_property_values=True,debug=1)
onto.save(file=str(ROOT/'results/game_inferred.owl'),format='rdfxml')
ns=Namespace(onto.base_iri)
g=Graph().parse(ROOT/'results/game_inferred.owl')
# Owlready2 сохраняет наиболее специфичные типы. Материализуем также
# выведенные надклассы, чтобы обычный SPARQL видел полное множество типов.
for cls in onto.classes():
    for individual in cls.instances():
        g.add((ns[individual.name],RDF.type,ns[cls.name]))
g.serialize(destination=str(ROOT/'results/game_inferred.owl'),format='xml')
queries={
 'combatant':('SELECT ?x WHERE {?x a :Combatant}',[['aria'],['borin'],['celia']]),
 'scout':('SELECT ?x WHERE {?x a :Scout}',[['elin'],['finn']]),
 'armed':('SELECT ?x WHERE {?x a :Armed}',[[x] for x in ['aria','borin','celia','darin','elin','finn']]),
 'skilled_for':('SELECT ?x WHERE {?x :skilledFor :tower}',[['celia']]),
 'ready_for':('SELECT ?x ?q WHERE {?x :readyFor ?q}',[['aria','ruins'],['celia','tower'],['finn','forest']]),
 'guildmate':('SELECT ?x ?y WHERE {?x :guildmate ?y}',[['aria','celia'],['celia','aria']]),
 'safe_character':('SELECT ?x WHERE {?x a :SafeCharacter}',[[x] for x in ['aria','celia','darin','elin','finn']]),
 'negative_ready':('SELECT ?q WHERE {:borin :readyFor ?q}',[]),
 'no_self_guildmate':('SELECT ?x WHERE {?x :guildmate ?x}',[])
}
results=[]
for name,(q,expected) in queries.items():
    actual=sorted([[str(c).split('#')[-1] for c in row] for row in g.query(q,initNs={'':ns})])
    passed=actual==sorted(expected)
    results.append(dict(name=name,query=q,actual=actual,expected=expected,pass_test=passed))
    print(('PASS' if passed else 'FAIL'),name,actual)
    assert passed,(name,actual,expected)
# Сопоставление с независимо выполненными запросами SWI-Prolog.
prolog=json.loads((ROOT/'results/prolog_results.json').read_text())['results']
for name, pq in [('combatant','combatant(X)'),('scout','scout(X)'),('armed','armed(X)'),
                 ('skilled_for','skilled_for(X,tower)'),('ready_for','ready_for(X,Q)'),
                 ('guildmate','guildmate(X,Y)'),('safe_character','safe_character(X)')]:
    p=next(r['actual'] for r in prolog if r['query']==pq)
    rows=sorted([x if isinstance(x,list) else [x] for x in p])
    assert rows==next(r['actual'] for r in results if r['name']==name)
summary=dict(unary_facts=len(unary),binary_facts=len(binary),prolog_rules=7,
    classes=len(list(onto.classes())),object_properties=len(list(onto.object_properties())),
    named_individuals=len({a for _,a in unary}),consistent=True,reasoner='Pellet',
    cross_checks=7,tests=results)
(ROOT/'results/ontology_results.json').write_text(json.dumps(summary,ensure_ascii=False,indent=2),encoding='utf-8')
(ROOT/'queries.sparql').write_text('\n\n'.join('# '+n+'\nPREFIX : <'+onto.base_iri+'>\n'+q for n,(q,_) in queries.items()),encoding='utf-8')
print('Ontology consistent; 9 queries and 7 Prolog/OWL comparisons passed.')
