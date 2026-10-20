import json, re
from pathlib import Path

ROOT=Path(__file__).resolve().parents[2]
OUT=Path(__file__).resolve().parent
metadata=json.loads((ROOT/'verification/schema_metadata.json').read_text(encoding='utf8'))
nodes={}
def node(n,x,y,h,w=650): nodes[n]={'id':n,'x':x,'y':y,'w':w,'h':h}
node('user_account',2000,100,600)
node('salon',600,1500,700)
node('district',-600,1700,250)
node('master',3400,1500,600)
node('moderation_decision',2000,1500,600)
node('salon_photo',1200,850,450)
node('master_photo',2800,850,450)
node('master_invitation',4300,100,500)
node('work_interval',4700,1800,450)
node('salon_service',600,3500,500)
node('service_type',600,4400,300)
node('master_service',3400,3500,400)
node('appointment',2000,4700,900)
node('review',2000,6200,400)

constraints=[x for x in metadata['constraints'] if x['kind']=='f']
edges=[]
def edge(source,target,points,column=None,reverse=False):
    matches=[c for c in constraints if c['table']==source and re.search(r'REFERENCES beauty\.'+target+r'\(',c['definition'])]
    if column: matches=[c for c in matches if re.search(r'FOREIGN KEY \('+re.escape(column)+r'\)',c['definition'])]
    assert len(matches)==1,(source,target,column,matches)
    if reverse: points=points[::-1]
    edges.append({'id':matches[0]['name'],'source':source,'target':target,'points':[list(p) for p in points]})

edge('salon','user_account',[(2000,500),(900,500),(900,1500)],reverse=True)
edge('salon','district',[(600,1850),(50,1850)])
edge('master','user_account',[(2650,500),(3700,500),(3700,1500)],reverse=True)
edge('master','salon',[(1100,2200),(1100,3000),(3500,3000),(3500,2100)],reverse=True)
edge('salon_service','salon',[(900,2200),(900,3500)],reverse=True)
edge('salon_service','service_type',[(900,4000),(900,4400)])
edge('master_service','master',[(3800,3500),(3800,2100)])
edge('master_service','salon_service',[(3400,3700),(1250,3700)])
edge('work_interval','master',[(4700,2000),(4050,2000)])
edge('appointment','master_service',[(2400,4700),(2400,4400),(3700,4400),(3700,3900)])
for i,(column,uy,outerx,py) in enumerate([
    ('client_user_id',250,-1800,5200),
    ('cancelled_by_user_id',300,-1700,5150),
    ('result_marked_by_user_id',350,-1600,5100),
]):
    edge('appointment','user_account',[(2000,uy),(outerx,uy),(outerx,py),(2000,py)],column,True)
edge('salon_photo','salon',[(1400,1300),(1400,1600),(1250,1600)])
edge('master_photo','master',[(3200,1300),(3200,1600),(3400,1600)])
edge('review','appointment',[(2300,6200),(2300,5600)])
edge('moderation_decision','user_account',[(2200,1500),(2200,700)],'admin_user_id')
edge('moderation_decision','user_account',[(2300,1500),(2300,700)],'target_user_id')
edge('moderation_decision','salon',[(2000,1900),(1250,1900)])
edge('moderation_decision','master',[(2650,1900),(3400,1900)])
edge('moderation_decision','salon_photo',[(2000,1700),(1700,1700),(1700,1300)])
edge('moderation_decision','master_photo',[(2650,1700),(2900,1700),(2900,1300)])
edge('moderation_decision','review',[(2500,2100),(2500,2700),(4300,2700),(4300,6400),(2650,6400)])
edge('master_invitation','master',[(4600,600),(4600,1300),(3900,1300),(3900,1500)])
edge('master_invitation','user_account',[(4300,250),(2650,250)])

def within(v,a,b): return min(a,b)<=v<=max(a,b)
def seg_intersection(a,b,c,d):
    if a[0]==b[0] and c[1]==d[1]:
        p=(a[0],c[1])
        return p if within(p[1],a[1],b[1]) and within(p[0],c[0],d[0]) else None
    if a[1]==b[1] and c[0]==d[0]: return seg_intersection(c,d,a,b)
    if a[0]==b[0]==c[0]==d[0]:
        lo=max(min(a[1],b[1]),min(c[1],d[1]));hi=min(max(a[1],b[1]),max(c[1],d[1]))
        if lo<=hi:return ('overlap',a[0],lo,hi)
    if a[1]==b[1]==c[1]==d[1]:
        lo=max(min(a[0],b[0]),min(c[0],d[0]));hi=min(max(a[0],b[0]),max(c[0],d[0]))
        if lo<=hi:return ('overlap',a[1],lo,hi)
    return None
def audit(ns,es):
    crossings=[]; collisions=[]
    for i,e in enumerate(es):
        for endpoint,nid in [(e['points'][0],e['source']),(e['points'][-1],e['target'])]:
            n=ns[nid]; x,y=endpoint
            assert ((x in (n['x'],n['x']+n['w']) and n['y']<=y<=n['y']+n['h']) or (y in (n['y'],n['y']+n['h']) and n['x']<=x<=n['x']+n['w'])),('endpoint not on box',e['id'],endpoint,n)
        for a,b in zip(e['points'],e['points'][1:]):
            assert a[0]==b[0] or a[1]==b[1],('not orthogonal',e,a,b)
            for n in ns.values():
                x,y,w,h=n['x'],n['y'],n['w'],n['h']
                if a[0]==b[0]: hit=x<a[0]<x+w and max(min(a[1],b[1]),y)<min(max(a[1],b[1]),y+h)
                else:hit=y<a[1]<y+h and max(min(a[0],b[0]),x)<min(max(a[0],b[0]),x+w)
                if hit:collisions.append({'edge':e['id'],'node':n['id'],'segment':[a,b]})
        for f in es[i+1:]:
            for a,b in zip(e['points'],e['points'][1:]):
                for c,d in zip(f['points'],f['points'][1:]):
                    hit=seg_intersection(a,b,c,d)
                    if hit: crossings.append({'edge1':e['id'],'edge2':f['id'],'point':hit})
    for i,n in enumerate(ns.values()):
        for m in list(ns.values())[i+1:]:
            if max(n['x'],m['x'])<min(n['x']+n['w'],m['x']+m['w']) and max(n['y'],m['y'])<min(n['y']+n['h'],m['y']+m['h']):collisions.append({'node1':n['id'],'node2':m['id']})
    return crossings,collisions
crossings,collisions=audit(nodes,edges)
assert not collisions,collisions
assert len(crossings)==2,crossings
result={'nodes':list(nodes.values()),'edges':edges,'canvas':{'x_min':-2000,'y_min':-100,'width':7600,'height':6900},'crossings':crossings,'collisions':collisions,'note':'Two crossings both lie on moderation_decision_target_review_id_fkey. Draw this edge with bridge jumps at those intersections; every entity appears exactly once.'}
(OUT/'physical_candidate.json').write_text(json.dumps(result,indent=2),encoding='utf8')
print(json.dumps({'nodes':len(nodes),'edges':len(edges),'crossings':crossings,'collisions':collisions},indent=2))

# Conceptual form: direct master--salon_service M:N; appointment directly
# names its master and the purchased service. Multivalued photo attributes
# belong inside salon/master, and invitation is implementation detail.
cn={k:dict(v) for k,v in nodes.items() if k not in {'master_service','salon_photo','master_photo','master_invitation'}}
cn['service_type'].update(x=-600,y=3700)
ce=[dict(e,points=[p[:] for p in e['points']]) for e in edges if e['source'] in cn and e['target'] in cn and e['id']!='salon_service_service_type_id_fkey']
ce.append({'id':'salon_service_service_type_id_fkey','source':'salon_service','target':'service_type','points':[[600,3800],[50,3800]]})
ce.append({'id':'master_provides_salon_service','source':'master','target':'salon_service','points':[[3800,2100],[3800,3700],[1250,3700]],'cardinality':'M:N'})
ce.append({'id':'appointment_master','source':'appointment','target':'master','points':[[2400,4700],[2400,4400],[3900,4400],[3900,2100]]})
ce.append({'id':'appointment_salon_service','source':'appointment','target':'salon_service','points':[[2200,4700],[2200,4500],[900,4500],[900,4000]]})
cx,cc=audit(cn,ce)
assert not cc,cc
assert len(cx)==3,cx
cr={'nodes':list(cn.values()),'edges':ce,'canvas':result['canvas'],'crossings':cx,'collisions':cc,'note':'Ten conceptual entities, direct M:N. Three crossings, all on moderation_decision_target_review_id_fkey; bridge jumps required.'}
(OUT/'conceptual_candidate.json').write_text(json.dumps(cr,indent=2),encoding='utf8')
print(json.dumps({'conceptual_nodes':len(cn),'edges':len(ce),'crossings':cx,'collisions':cc},indent=2))
