"""Validate deliverables, hash them, and package a portable submission without runtimes."""
import hashlib
import json
import re
import zipfile
from pathlib import Path
from rdflib import Graph, URIRef, RDF, OWL, Namespace

HERE = Path(__file__).resolve().parent
NS = Namespace('https://example.org/lol-ontology#')


def main():
    output_dir = HERE/'output'
    graph = Graph().parse(output_dir/'ontologies'/'lol_demo_inferred.owl')
    asserted = Graph().parse(output_dir/'ontologies'/'lol_demo.owl')
    manifest = json.loads((output_dir/'verification'/'build_manifest.json').read_text(encoding='utf-8'))
    for name, expected in manifest['source']['hashes'].items():
        assert hashlib.sha256((HERE/'source'/name).read_bytes()).hexdigest() == expected, name
    for name in ['README.md','EXPERIMENT_RU.md']:
        text = (HERE/name).read_text(encoding='utf-8')
        for target in re.findall(r'!\[[^\]]*\]\(([^)]+)\)',text):
            assert (HERE/target).is_file(), target
    data = json.loads((output_dir/'visualizations'/'webvowl'/'lol_demo.webvowl.json').read_text(encoding='utf-8'))
    project_classes = {URIRef(c['iri']) for c in data['classAttribute'] if c.get('iri','').startswith(str(NS))}
    project_properties = {URIRef(p['iri']) for p in data['propertyAttribute'] if p.get('iri','').startswith(str(NS))}
    assert project_classes == {c for c in asserted.subjects(RDF.type,OWL.Class) if str(c).startswith(str(NS))}
    assert project_properties == set(asserted.subjects(RDF.type,OWL.ObjectProperty)) | set(asserted.subjects(RDF.type,OWL.DatatypeProperty))
    for path in (output_dir/'visualizations'/'reactodia').glob('*.reactodia.json'):
        diagram = json.loads(path.read_text(encoding='utf-8'))
        assert len(diagram['layoutData']['elements']) == 9, path
        for edge in diagram['layoutData']['links']:
            assert (URIRef(edge['sourceIri']),URIRef(edge['property']),URIRef(edge['targetIri'])) in graph, edge
    for path in (output_dir/'visualizations').rglob('*.svg'):
        import xml.etree.ElementTree as ET
        ET.parse(path)
    for variant in ['demo','full']:
        log = (output_dir/'verification'/f'hermit_{variant}_verification.txt').read_text(encoding='utf-8')
        assert 'FAIL' not in log and 'PASS Ontology is consistent' in log and 'PASS Mutation:' in log

    files = [p for pattern in ['*.py','*.md','requirements.txt','mechanics_annotations.csv',
                               'queries/*','output/**/*','source/*','evidence/*',
                               'tools/*.java','tools/*.ps1','tools/*.xml'] for p in HERE.glob(pattern) if p.is_file()]
    files = sorted(set(files))
    checksums = {p.relative_to(HERE).as_posix():hashlib.sha256(p.read_bytes()).hexdigest() for p in files}
    record = {'date':'2026-11-03','timezone':'Europe/Moscow','sha256':checksums,
              'checks':{'webvowl_named_classes':len(project_classes),'webvowl_properties':len(project_properties),
                        'reactodia_layouts':3,'ontology':'OWL 2 DL; HermiT consistent',
                        'ontodia_original_service':'unavailable; Reactodia used as a documented alternative'}}
    index = HERE/'submission_manifest.json'
    index.write_text(json.dumps(record,ensure_ascii=False,indent=2),encoding='utf-8')
    destination = HERE/'LoL_Ontology_Submission.zip'
    with zipfile.ZipFile(destination,'w',compression=zipfile.ZIP_DEFLATED,compresslevel=9) as z:
        for p in files+[index]:
            z.write(p,arcname='LoL_Ontology/'+p.relative_to(HERE).as_posix())
    with zipfile.ZipFile(destination) as z:
        assert z.testzip() is None
        assert not any('.venv' in name or name.endswith('.jar') for name in z.namelist())
    print(f'Validated {len(project_classes)} WebVOWL classes, {len(project_properties)} properties, 3 Reactodia layouts.')
    print(f'Packaged {len(files)+1} files, {destination.stat().st_size:,} bytes: {destination}')


if __name__=='__main__':
    main()
