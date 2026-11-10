"""Run the two sample queries and the one explicitly stated teaching rule."""
from pathlib import Path
import json
import platform
from decimal import Decimal
import rdflib
from rdflib import Graph, Namespace, Literal, RDF

HERE = Path(__file__).resolve().parent
LIB = Namespace('https://example.org/kg-course/library/')
full = Graph().parse(HERE / 'library-v0.1.ttl', format='turtle')
small = Graph().parse(HERE / 'rdf-sample.ttl', format='turtle')
assert len(full) == 44 and len(small) == 11
assert all(t in full for t in small)
assert len(set(full.subjects(RDF.type, None))) == 13

def query(graph, name):
    return [[str(value) for value in row] for row in graph.query(
        (HERE / name).read_text(encoding='utf-8'))]

authors = query(small, 'authors.rq')
expected_authors = [[str(LIB.Author001), '林岚'], [str(LIB.Author002), '梅雨']]
assert authors == expected_authors
assert query(full, 'authors.rq') == authors
common = query(full, 'common-authors.rq')
assert common == [[str(LIB.Author001), '林岚']]

# This is one Python forward rule, not an OWL reasoner.
derived = set()
for copy, _, edition in full.triples((None, LIB.copyOf, None)):
    for work in full.objects(edition, LIB.editionOf):
        for subject in full.objects(work, LIB.about):
            derived.add((copy, LIB.copyAbout, subject))
assert derived == {(LIB.Copy001, LIB.copyAbout, LIB.Subject001),
                   (LIB.Copy002, LIB.copyAbout, LIB.Subject001)}
assert not any(t in full for t in derived)
available = sorted(str(s) for s in full.subjects(LIB.availability, Literal('available')))
assert available == [str(LIB.Copy001)]

# Recheck Lecture1 p53's vector subtraction exactly in decimal arithmetic.
delta = [Decimal(o)-Decimal(s) for o,s in zip(['0.18','0.4','0.9'],['0.05','0.25','0.37'])]
assert delta == [Decimal('0.13'),Decimal('0.15'),Decimal('0.53')]
result = dict(python=platform.python_version(), rdflib=rdflib.__version__,
    full_triples=len(full), sample_triples=len(small), instances=13,
    authors=authors, common_authors=common, available=available,
    derived_copy_about=[list(map(str,t)) for t in sorted(derived)],
    lecture1_p53_delta=list(map(str,delta)),
    reasoning='One explicit Python rule only; no RDFS/OWL reasoner enabled',
    status='PASS')
print(json.dumps(result, ensure_ascii=False, indent=2))
