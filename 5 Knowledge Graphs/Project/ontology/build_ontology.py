"""Воспроизводимая сборка OWL из локального снимка Data Dragon и разметки.

Запуск: .venv/Scripts/python.exe build_ontology.py
Исходные данные не изменяются. Разметка отделена от автоматического импорта.
"""
from __future__ import annotations

import csv
import hashlib
import json
from pathlib import Path

from rdflib import BNode, Graph, Literal, Namespace, RDF, RDFS, OWL, URIRef, XSD
from rdflib.collection import Collection
from rdflib.namespace import DCTERMS

HERE = Path(__file__).resolve().parent
SOURCE = HERE.parent / 'data' / '16.20.1' / 'ru_RU' / 'all'
if not (SOURCE / 'champions.json').is_file():
    SOURCE = HERE / 'source'
NS = Namespace('https://example.org/lol-ontology#')
ONT = URIRef('https://example.org/lol-ontology')
DEMO = {'Lux', 'Morgana', 'Karma'}

CLASSES = {
    'Champion': 'Игровой чемпион.',
    'ChampionCategory': 'Категория Data Dragon (Mage, Support и т. п.), не позиция на карте.',
    'Ability': 'Основное умение P/Q/W/E/R.',
    'PassiveAbility': 'Пассивное умение, слот P.',
    'ActiveAbility': 'Активное умение, слот Q/W/E/R.',
    'AbilityEffect': 'Один эффект умения с собственной целью и условием.',
    'Mechanic': 'Тип механики: щит, урон, обездвиживание и т. п.',
    'MovementControlMechanic': 'Механика ограничения передвижения: Root, Slow или Stun.',
    'TargetType': 'Тип получателя конкретного эффекта, не конкретный участник матча.',
    'SourceDocument': 'Документ, подтверждающий данные.',
    'MageChampion': 'Чемпион с категорией Mage; классифицируется ризонером.',
    'AllyShieldChampion': 'Чемпион с хотя бы одним эффектом щита для союзников.',
    'EnemyMovementControlChampion': 'Чемпион с хотя бы одним эффектом ограничения передвижения врага.',
    'SupportControlMage': 'Маг, способный дать союзнику щит и ограничить передвижение врага. Умения могут быть разными.',
}
OBJECTS = {
    'hasAbility': ('Champion', 'Ability', 'У чемпиона есть умение.'),
    'isAbilityOf': ('Ability', 'Champion', 'Умение принадлежит чемпиону; обратное hasAbility.'),
    'hasCategory': ('Champion', 'ChampionCategory', 'Категория чемпиона в Data Dragon.'),
    'hasEffect': ('Ability', 'AbilityEffect', 'Умение имеет конкретный эффект.'),
    'effectOf': ('AbilityEffect', 'Ability', 'Эффект относится к умению; обратное hasEffect.'),
    'hasMechanic': ('AbilityEffect', 'Mechanic', 'Механика конкретного эффекта.'),
    'hasTargetType': ('AbilityEffect', 'TargetType', 'Получатель конкретного эффекта.'),
    'hasSource': (None, 'SourceDocument', 'Источник сведений об объекте.'),
    'canApplyMechanic': ('Champion', 'Mechanic', 'Выводится цепочкой hasAbility / hasEffect / hasMechanic; не хранит условия.'),
}
DATA = {
    'entityId': (None, XSD.string), 'name': (None, XSD.string),
    'description': (None, XSD.string), 'gameVersion': (None, XSD.string),
    'sourceURL': ('SourceDocument', XSD.anyURI), 'slot': ('Ability', XSD.string),
    'baseHP': ('Champion', XSD.decimal), 'baseMP': ('Champion', XSD.decimal),
    'baseArmor': ('Champion', XSD.decimal), 'baseAttackDamage': ('Champion', XSD.decimal),
    'baseMoveSpeed': ('Champion', XSD.decimal), 'title': ('Champion', XSD.string),
    'resourceType': ('Champion', XSD.string), 'tooltipText': ('Ability', XSD.string),
    'conditionText': ('AbilityEffect', XSD.string), 'evidenceText': ('AbilityEffect', XSD.string),
    'evidenceField': ('AbilityEffect', XSD.string), 'reviewStatus': (None, XSD.string),
}
MECHANICS = {
    'Damage': 'Урон', 'Shield': 'Щит', 'Root': 'Обездвиживание',
    'Slow': 'Замедление', 'Stun': 'Оглушение', 'Heal': 'Лечение',
    'MovementSpeedBoost': 'Ускорение', 'Reveal': 'Раскрытие цели',
    'CooldownReduction': 'Сокращение перезарядки',
    'Empower': 'Усиление умения', 'ControlImmunity': 'Защита от эффектов контроля',
}


def rdf_list(g, values):
    head = BNode()
    Collection(g, head, values)
    return head


def intersection(g, *values):
    node = BNode()
    g.add((node, RDF.type, OWL.Class))
    g.add((node, OWL.intersectionOf, rdf_list(g, values)))
    return node


def restriction(g, prop, value, has_value=False):
    node = BNode()
    g.add((node, RDF.type, OWL.Restriction))
    g.add((node, OWL.onProperty, NS[prop]))
    g.add((node, OWL.hasValue if has_value else OWL.someValuesFrom, value))
    return node


def schema():
    g = Graph()
    for prefix, namespace in [('lol', NS), ('owl', OWL), ('rdf', RDF), ('rdfs', RDFS), ('xsd', XSD)]:
        g.bind(prefix, namespace)
    g.add((ONT, RDF.type, OWL.Ontology))
    g.add((ONT, OWL.versionInfo, Literal('1.0 / Data Dragon 16.20.1 / ru_RU')))
    g.add((ONT, RDFS.label, Literal('League of Legends: champions, abilities and effects', lang='en')))
    for annotation in [DCTERMS.title, DCTERMS.description]:
        g.add((annotation, RDF.type, OWL.AnnotationProperty))
    g.add((ONT, DCTERMS.title, Literal('League of Legends: champions, abilities and effects', lang='en')))
    g.add((ONT, DCTERMS.description, Literal(
        'An OWL 2 DL ontology of champions, abilities and qualified effects. '
        'The demo contains Lux, Morgana and Karma. Effect conditions and source evidence are preserved. '
        'Data Dragon 16.20.1, ru_RU. Effect annotations reviewed by an assistant.', lang='en')))
    g.add((ONT, RDFS.comment, Literal(
        'Учебная онтология. Качественная разметка эффектов проверена ассистентом только для Lux, Morgana, Karma. '
        'Условия сохранены текстом; вывод означает наличие способности при указанных условиях, а не результат любого применения. '
        'Отсутствие разметки не означает отсутствие механики. Числа из шаблонов tooltip не угадываются.', lang='ru')))
    for cls, comment in CLASSES.items():
        g.add((NS[cls], RDF.type, OWL.Class))
        g.add((NS[cls], RDFS.label, Literal(cls)))
        g.add((NS[cls], RDFS.comment, Literal(comment, lang='ru')))
    for sub, parent in [('PassiveAbility', 'Ability'), ('ActiveAbility', 'Ability'),
                        ('MovementControlMechanic', 'Mechanic')]:
        g.add((NS[sub], RDFS.subClassOf, NS[parent]))
    g.add((NS.PassiveAbility, OWL.disjointWith, NS.ActiveAbility))
    disjoint = BNode()
    g.add((disjoint, RDF.type, OWL.AllDisjointClasses))
    g.add((disjoint, OWL.members, rdf_list(g, [NS[x] for x in
        ['Champion', 'ChampionCategory', 'Ability', 'AbilityEffect', 'Mechanic', 'TargetType', 'SourceDocument']])))
    for prop, (domain, range_, comment) in OBJECTS.items():
        g.add((NS[prop], RDF.type, OWL.ObjectProperty))
        g.add((NS[prop], RDFS.label, Literal(prop)))
        g.add((NS[prop], RDFS.comment, Literal(comment, lang='ru')))
        if domain:
            g.add((NS[prop], RDFS.domain, NS[domain]))
        g.add((NS[prop], RDFS.range, NS[range_]))
    g.add((NS.hasAbility, OWL.inverseOf, NS.isAbilityOf))
    g.add((NS.hasEffect, OWL.inverseOf, NS.effectOf))
    g.add((NS.canApplyMechanic, OWL.propertyChainAxiom,
           rdf_list(g, [NS.hasAbility, NS.hasEffect, NS.hasMechanic])))
    for prop, (domain, range_) in DATA.items():
        g.add((NS[prop], RDF.type, OWL.DatatypeProperty))
        g.add((NS[prop], RDFS.label, Literal(prop)))
        if domain:
            g.add((NS[prop], RDFS.domain, NS[domain]))
        g.add((NS[prop], RDFS.range, range_))

    mage = intersection(g, NS.Champion, restriction(g, 'hasCategory', NS.Category_Mage, True))
    shield_effect = intersection(g, NS.AbilityEffect,
        restriction(g, 'hasMechanic', NS.Shield, True), restriction(g, 'hasTargetType', NS.Ally, True))
    control_effect = intersection(g, NS.AbilityEffect,
        restriction(g, 'hasMechanic', NS.MovementControlMechanic), restriction(g, 'hasTargetType', NS.Enemy, True))
    for cls, expression in [
        ('MageChampion', mage),
        ('AllyShieldChampion', intersection(g, NS.Champion, restriction(g, 'hasAbility',
            restriction(g, 'hasEffect', shield_effect)))),
        ('EnemyMovementControlChampion', intersection(g, NS.Champion, restriction(g, 'hasAbility',
            restriction(g, 'hasEffect', control_effect)))),
        ('SupportControlMage', intersection(g, NS.MageChampion, NS.AllyShieldChampion, NS.EnemyMovementControlChampion)),
    ]:
        g.add((NS[cls], OWL.equivalentClass, expression))
        g.add((NS[cls], RDFS.subClassOf, NS.Champion))
    return g


def individual(g, id_, cls, name=None):
    node = NS[id_]
    g.add((node, RDF.type, OWL.NamedIndividual))
    g.add((node, RDF.type, NS[cls]))
    g.add((node, RDFS.label, Literal(id_)))
    if name:
        g.add((node, NS.name, Literal(name, datatype=XSD.string)))
    return node


def data(g, node, prop, value):
    if value is not None and value != '':
        if DATA[prop][1] == XSD.decimal:
            value = str(value)
            if '.' not in value:
                value += '.0'
        g.add((node, NS[prop], Literal(value, datatype=DATA[prop][1])))


def make_graph(champions, abilities, annotations):
    g = schema()
    categories = {tag for c in champions for tag in c['classes']} | {'Mage'}
    for tag in sorted(categories):
        individual(g, 'Category_' + tag, 'ChampionCategory', tag)
    for id_, name in MECHANICS.items():
        individual(g, id_, 'MovementControlMechanic' if id_ in {'Root', 'Slow', 'Stun'} else 'Mechanic', name)
    for id_, name in {'Ally': 'Союзник', 'Enemy': 'Противник', 'Self': 'Сам чемпион', 'OwnAbility': 'Собственное умение'}.items():
        individual(g, id_, 'TargetType', name)
    for group in [[NS[t] for t in MECHANICS], [NS[t] for t in ['Ally', 'Enemy', 'Self', 'OwnAbility']],
                  [NS['Category_' + t] for t in sorted(categories)]]:
        node = BNode()
        g.add((node, RDF.type, OWL.AllDifferent))
        g.add((node, OWL.distinctMembers, rdf_list(g, group)))
    for c in champions:
        node = individual(g, c['champion_id'], 'Champion', c['name'])
        doc = individual(g, 'Source_' + c['champion_id'], 'SourceDocument')
        data(g, doc, 'sourceURL', c['source_url'])
        data(g, doc, 'gameVersion', c['version'])
        g.add((node, NS.hasSource, doc))
        for prop, value in [('entityId', c['champion_id']), ('title', c['title']),
                            ('gameVersion', c['version']), ('resourceType', c['resource_type'])]:
            data(g, node, prop, value)
        for prop, field in [('baseHP', 'hp'), ('baseMP', 'mp'), ('baseArmor', 'armor'),
                            ('baseAttackDamage', 'attackdamage'), ('baseMoveSpeed', 'movespeed')]:
            data(g, node, prop, c['stats'][field])
        for tag in c['classes']:
            g.add((node, NS.hasCategory, NS['Category_' + tag]))
        data(g, node, 'reviewStatus', 'effects_reviewed_by_assistant' if c['champion_id'] in DEMO else 'effects_not_reviewed')
    for a in abilities:
        id_ = a['ability_id'].replace(':', '_')
        node = individual(g, id_, 'PassiveAbility' if a['kind'] == 'passive' else 'ActiveAbility', a['name'])
        g.add((NS[a['champion_id']], NS.hasAbility, node))
        g.add((node, NS.hasSource, NS['Source_' + a['champion_id']]))
        for prop, field in [('entityId', 'ability_id'), ('slot', 'slot'), ('description', 'description_text'),
                            ('tooltipText', 'tooltip_text'), ('gameVersion', 'version')]:
            data(g, node, prop, a[field])
    included = {a['ability_id'] for a in abilities}
    for r in annotations:
        if r['ability_id'] not in included:
            continue
        node = individual(g, r['effect_id'], 'AbilityEffect')
        g.add((NS[r['ability_id'].replace(':', '_')], NS.hasEffect, node))
        g.add((node, NS.hasMechanic, NS[r['mechanic']]))
        g.add((node, NS.hasTargetType, NS[r['target']]))
        g.add((node, NS.hasSource, NS['Source_' + r['ability_id'].split(':')[0]]))
        for prop, field in [('conditionText', 'condition'), ('evidenceText', 'evidence_text'),
                            ('evidenceField', 'evidence_field'), ('reviewStatus', 'review_status'), ('gameVersion', 'version')]:
            data(g, node, prop, r[field])
    return g


def validate_annotations(annotations, abilities):
    by_id = {a['ability_id']: a for a in abilities}
    seen = set()
    for r in annotations:
        assert r['effect_id'] not in seen, r['effect_id']
        seen.add(r['effect_id'])
        assert r['ability_id'].split(':')[0] in DEMO, r
        assert r['mechanic'] in MECHANICS and r['target'] in {'Ally', 'Enemy', 'Self', 'OwnAbility'}, r
        assert r['evidence_field'] in {'description_text', 'tooltip_text'}, r
        assert r['evidence_text'] and r['evidence_text'] in by_id[r['ability_id']][r['evidence_field']], r
        assert r['condition'] and r['review_status'] == 'reviewed_by_assistant', r
        assert r['version'] == by_id[r['ability_id']]['version'] == '16.20.1', r
    assert {r['ability_id'] for r in annotations} == {a['ability_id'] for a in abilities if a['champion_id'] in DEMO}


def main():
    champions = json.loads((SOURCE / 'champions.json').read_text(encoding='utf-8'))
    abilities = json.loads((SOURCE / 'abilities.json').read_text(encoding='utf-8'))
    with (HERE / 'mechanics_annotations.csv').open(encoding='utf-8-sig', newline='') as f:
        annotations = list(csv.DictReader(f))
    validate_annotations(annotations, abilities)
    ontology_dir = HERE / 'output' / 'ontologies'
    verification_dir = HERE / 'output' / 'verification'
    ontology_dir.mkdir(parents=True, exist_ok=True)
    verification_dir.mkdir(parents=True, exist_ok=True)
    stats = {}
    for variant, cc, aa in [
        ('demo', [c for c in champions if c['champion_id'] in DEMO], [a for a in abilities if a['champion_id'] in DEMO]),
        ('full', champions, abilities),
    ]:
        g = make_graph(cc, aa, annotations)
        for ext, fmt in [('owl', 'xml'), ('ttl', 'turtle')]:
            path = ontology_dir / f'lol_{variant}.{ext}'
            g.serialize(path, format=fmt, encoding='utf-8')
            # Round trip checks catch serializer/list errors before opening in Protégé.
            loaded = Graph().parse(path, format='xml' if ext == 'owl' else 'turtle')
            from rdflib.compare import isomorphic
            assert isomorphic(g, loaded), path
        stats[variant] = {
            'classes': len(set(g.subjects(RDF.type, OWL.Class)) & set(NS[x] for x in CLASSES)),
            'object_properties': len(OBJECTS), 'data_properties': len(DATA),
            'champions': len(cc), 'abilities': len(aa), 'annotated_champions': sorted(DEMO),
            'effect_assertions': len(annotations),
            'individuals': len(set(g.subjects(RDF.type, OWL.NamedIndividual))), 'triples': len(g),
        }
    schema().serialize(ontology_dir / 'lol_schema.owl', format='xml', encoding='utf-8')
    stats['source'] = {'version': '16.20.1', 'locale': 'ru_RU', 'snapshot': str(SOURCE),
        'hashes': {f: hashlib.sha256((SOURCE/f).read_bytes()).hexdigest()
                   for f in ['champions.json', 'abilities.json', 'manifest.json']},
        'annotations_sha256': hashlib.sha256((HERE/'mechanics_annotations.csv').read_bytes()).hexdigest(),
        'annotation_scope': 'Qualitative effects for 3 champions; reviewed by assistant, not independently approved by a human.'}
    (verification_dir / 'build_manifest.json').write_text(json.dumps(stats, ensure_ascii=False, indent=2), encoding='utf-8')
    print(json.dumps({k:v for k,v in stats.items() if k != 'source'}, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
