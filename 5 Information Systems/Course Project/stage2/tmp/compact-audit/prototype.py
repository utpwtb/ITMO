"""Read-only source-layout prototype; candidates are confined to this directory."""
from pathlib import Path
import copy
import importlib.util
import json
import math
import sys

sys.stdout.reconfigure(encoding="utf-8")
HERE=Path(__file__).resolve().parent
STAGE=HERE.parents[1]
spec=importlib.util.spec_from_file_location("diagram_generator",STAGE/"scripts/draw_integrated_models.py")
d=importlib.util.module_from_spec(spec)
spec.loader.exec_module(d)


def measure(n,model):
    return d.content_dimensions(n["id"],model)


def candidate(source,model,step,direct_gap=80,endpoint_gap=40,side_review=False):
    layout=copy.deepcopy(source)
    desired={n["id"]:measure(n,model) for n in layout["nodes"]}
    # All coordinates retain their original order, so exterior route topology is unchanged.
    for axis,coord,extent in ((0,"x","w"),(1,"y","h")):
        values=sorted({p[axis] for e in layout["edges"] for p in e["points"]} |
                      {n[coord] for n in layout["nodes"]} | {n[coord]+n[extent] for n in layout["nodes"]})
        index={v:i for i,v in enumerate(values)}
        constraints={i:[] for i in range(len(values))}
        for n in layout["nodes"]:
            constraints[index[n[coord]+n[extent]]].append((index[n[coord]],desired[n["id"]][axis]))
        for e in layout["edges"]:
            segments=[(e["points"][0],e["points"][1]),(e["points"][-2],e["points"][-1])]
            for a,b in segments:
                if a[axis]!=b[axis]:
                    lo,hi=sorted((a[axis],b[axis]))
                    gap=direct_gap if len(e["points"])==2 else endpoint_gap
                    constraints[index[hi]].append((index[lo],gap))
        pos=[0]*len(values)
        pos[0]=100 if axis==0 else 140
        for i in range(1,len(values)):
            pos[i]=max([pos[i-1]+step]+[pos[j]+gap for j,gap in constraints[i]])
        mapping=dict(zip(values,pos))
        for n in layout["nodes"]:
            a,b=mapping[n[coord]],mapping[n[coord]+n[extent]]
            n[coord],n[extent]=a,b-a
        for e in layout["edges"]:
            for point in e["points"]:point[axis]=mapping[point[axis]]
    changes=[]
    for n in layout["nodes"]:
        old=copy.deepcopy(n)
        ports=[]
        for e in layout["edges"]:
            for end,key in ((0,"source"),(-1,"target")):
                if e[key]!=n["id"]:continue
                p=e["points"][end]
                choices=[]
                if p[0]==old["x"]:choices.append("left")
                if p[0]==old["x"]+old["w"]:choices.append("right")
                if p[1]==old["y"]:choices.append("top")
                if p[1]==old["y"]+old["h"]:choices.append("bottom")
                assert len(choices)==1,(n["id"],p,choices)
                ports.append((e,end,choices[0]))
        for axis,coord,extent,tangent_sides in ((0,"x","w",("top","bottom")),(1,"y","h",("left","right"))):
            t=[e["points"][end][axis] for e,end,side in ports if side in tangent_sides]
            wanted=desired[n["id"]][axis]
            padding=18 if not t else min(18,max(8,(wanted-(max(t)-min(t)))/2))
            if t:wanted=max(wanted,max(t)-min(t)+padding*2)
            wanted=min(wanted,old[extent])
            lo=old[coord]
            hi=old[coord]+old[extent]-wanted
            if t:
                lo=max(lo,max(t)+padding-wanted)
                hi=min(hi,min(t)-padding)
            # Coordinates at a corner could need a smaller margin; retain the port instead.
            if lo>hi:
                lo=old[coord];hi=old[coord]+old[extent]-wanted
                if t:lo=max(lo,max(t)-wanted);hi=min(hi,min(t))
            assert lo<=hi,(n["id"],axis,lo,hi)
            chosen=min(max(old[coord]+(old[extent]-wanted)/2,lo),hi)
            n[coord]=chosen;n[extent]=wanted
        for e,end,side in ports:
            p=e["points"][end]
            if side in ("left","right"):p[0]=n["x"]+(n["w"] if side=="right" else 0)
            else:p[1]=n["y"]+(n["h"] if side=="bottom" else 0)
        changes.append({"id":n["id"],"desired":desired[n["id"]],"actual":[n["w"],n["h"]],"slot":[old["w"],old["h"]]})
    if side_review:
        ap=next(n for n in layout["nodes"] if n["id"]=="appointment")
        review=next(n for n in layout["nodes"] if n["id"]=="review")
        review["x"]=ap["x"]+ap["w"]+120
        review["y"]=ap["y"]+150
        for e in layout["edges"]:
            if e["id"]=="review_appointment_id_fkey":
                y=ap["y"]+300
                e["points"]=[[review["x"],y],[ap["x"]+ap["w"],y]]
            elif e["id"]=="moderation_decision_target_review_id_fkey":
                e["points"][-2][1]=review["y"]+40
                e["points"][-1]=[review["x"]+review["w"],review["y"]+40]
    layout.pop("crossings",None);layout.pop("collisions",None)
    return layout,changes


def main():
    summaries=[]
    for model in ("er","logical"):
        source=json.loads((STAGE/"scripts/diagram_layouts"/f"{model}.json").read_text("utf-8"))
        for step in (24,28,30):
            layout,changes=candidate(source,model,step)
            audit=d.audit_layout(layout,model)
            coords=[p for e in layout["edges"] for p in e["points"]]
            width=max([n["x"]+n["w"] for n in layout["nodes"]]+[p[0] for p in coords])+90
            height=max([n["y"]+n["h"] for n in layout["nodes"]]+[p[1] for p in coords])+90
            layout["canvas"]={"width":width,"height":height}
            (HERE/f"{model}_{step}.json").write_text(json.dumps(layout,ensure_ascii=False,indent=2),encoding="utf-8")
            summaries.append({"model":model,"step":step,"canvas":[width,height],"audit":audit,"boxes":changes})
    (HERE/"summary.json").write_text(json.dumps(summaries,ensure_ascii=False,indent=2),encoding="utf-8")
    print(json.dumps(summaries,ensure_ascii=False,indent=2))


if __name__=="__main__":main()
