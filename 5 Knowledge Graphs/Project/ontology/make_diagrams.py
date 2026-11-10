"""Generate readable Reactodia layouts using the format exported by RDF Explorer.

Layouts refer to real IRIs. Every displayed edge is checked against HermiT output.
The full RDF data stays in lol_demo_inferred.ttl; a diagram is a selected view.
"""
import json
from pathlib import Path
from rdflib import Graph, Namespace

HERE = Path(__file__).resolve().parent
NS = Namespace('https://example.org/lol-ontology#')


def main():
    g = Graph().parse(HERE/'output'/'ontologies'/'lol_demo_inferred.owl')
    diagram_dir = HERE/'output'/'visualizations'/'reactodia'
    diagram_dir.mkdir(parents=True, exist_ok=True)
    for champion, shield_slot, root_slot in [('Lux', 'W', 'Q'), ('Karma', 'E', 'W'), ('Morgana', 'E', 'Q')]:
        shield = f'{champion}_{shield_slot}'
        root = f'{champion}_{root_slot}'
        seffect = shield+'_Shield_Ally'
        reffect = root+'_Root_Enemy'
        positions = {champion: (0,300), root: (280,100), shield: (280,500),
                     reffect: (580,100), seffect: (580,500),
                     'Root': (1010,0), 'Enemy': (1010,200), 'Shield': (1010,400), 'Ally': (1010,600)}
        ids = {name: 'urn:reactodia:e:'+name for name in positions}
        edges = [(champion, 'hasAbility', root), (champion, 'hasAbility', shield),
                 (root, 'isAbilityOf', champion), (shield, 'isAbilityOf', champion),
                 (root, 'hasEffect', reffect), (shield, 'hasEffect', seffect),
                 (reffect, 'effectOf', root), (seffect, 'effectOf', shield),
                 (reffect, 'hasMechanic', 'Root'), (reffect, 'hasTargetType', 'Enemy'),
                 (seffect, 'hasMechanic', 'Shield'), (seffect, 'hasTargetType', 'Ally')]
        for s,p,o in edges:
            assert (NS[s],NS[p],NS[o]) in g, (s,p,o)
        diagram = {'@context': 'https://ontodia.org/context/v1.json', '@type': 'Diagram',
            'layoutData': {'@type': 'Layout', 'elements': [
                {'@type': 'Element', '@id':ids[name], 'iri':str(NS[name]), 'position':{'x':x,'y':y}}
                for name,(x,y) in positions.items()],
                'links': [
                    {'@type':'Link', '@id':'urn:reactodia:l:'+str(i), 'property':str(NS[p]),
                     'source':{'@id':ids[s]}, 'target':{'@id':ids[o]},
                     'sourceIri':str(NS[s]), 'targetIri':str(NS[o]), 'vertices':[]}
                    for i,(s,p,o) in enumerate(edges)]}, 'linkTypeOptions':[
                        {'@type':'LinkTypeOptions','property':str(NS.canApplyMechanic),
                         'visible':False,'showLabel':True}]}
        destination = diagram_dir/f'{champion.lower()}_relations.reactodia.json'
        destination.write_text(json.dumps(diagram,ensure_ascii=False,indent=2),encoding='utf-8')
        print(f'{champion}: 9 nodes, 12 verified edges -> {destination.name}')


if __name__=='__main__':
    main()
