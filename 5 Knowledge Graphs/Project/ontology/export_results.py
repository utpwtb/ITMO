"""Проверка запросов и экспорт объяснимых результатов после материализации HermiT."""
import csv
import json
from pathlib import Path
from rdflib import Graph, Namespace, RDF, RDFS, URIRef, Literal
from rdflib.namespace import OWL

HERE = Path(__file__).resolve().parent
NS = Namespace('https://example.org/lol-ontology#')


def run(g, name):
    return g.query((HERE/'queries'/name).read_text(encoding='utf-8'))


def write_result(g, query, destination):
    result = run(g, query)
    rows = list(result)
    with destination.open('w', encoding='utf-8-sig', newline='') as f:
        writer = csv.writer(f)
        writer.writerow([str(v) for v in result.vars])
        writer.writerows([[str(x).removeprefix(str(NS)) for x in row] for row in rows])
    return rows


def main():
    ontology_dir = HERE/'output'/'ontologies'
    results_dir = HERE/'output'/'results'
    verification_dir = HERE/'output'/'verification'
    results_dir.mkdir(parents=True, exist_ok=True)
    verification_dir.mkdir(parents=True, exist_ok=True)
    summary = {}
    for variant in ['demo', 'full']:
        asserted = Graph().parse(ontology_dir/f'lol_{variant}.owl')
        inferred = Graph().parse(ontology_dir/f'lol_{variant}_inferred.owl')
        explained = write_result(asserted, '01_competency_question.rq', results_dir/f'{variant}_query_explanations.csv')
        cls = write_result(inferred, '03_inferred_class.rq', results_dir/f'{variant}_inferred_matches.csv')
        inverse = write_result(inferred, '02_inverse_ownership.rq', results_dir/f'{variant}_inverse_relations.csv')
        effects = write_result(asserted, '04_ability_effects.rq', results_dir/f'{variant}_effect_evidence.csv')
        expected = {NS.Karma, NS.Lux, NS.Morgana}
        assert {r[0] for r in explained} == expected == {r[0] for r in cls}
        assert len(list(run(asserted, '03_inferred_class.rq'))) == 0
        assert len(list(run(asserted, '02_inverse_ownership.rq'))) == 0
        assert len(inverse) == (15 if variant == 'demo' else 865)
        assert len(explained) == 7 and len(effects) == 28
        summary[variant] = {'query_matches': sorted(str(x).removeprefix(str(NS)) for x in expected),
            'explanation_rows': len(explained), 'effect_evidence_rows': len(effects),
            'inverse_relations_asserted': 0, 'inverse_relations_after_hermit': len(inverse),
            'target_class_assertions_before_hermit': 0, 'target_class_instances_after_hermit': len(cls)}
    # Reactodia uses the native Turtle parser; materialized facts expose inverse and derived links.
    Graph().parse(ontology_dir/'lol_demo_inferred.owl').serialize(
        ontology_dir/'lol_demo_inferred.ttl', format='turtle', encoding='utf-8')
    (verification_dir/'query_validation.json').write_text(json.dumps(summary, indent=2), encoding='utf-8')
    print(json.dumps(summary, indent=2))


if __name__ == '__main__':
    main()
