"""Standalone whole-model drawings; this script never writes the report or SQL."""
from pathlib import Path
from itertools import combinations
import hashlib
import html
import json
import math
import re
import sys
import xml.etree.ElementTree as ET

from PIL import Image, ImageDraw, ImageFont
from reportlab.pdfgen import canvas as pdfcanvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.colors import toColor

sys.stdout.reconfigure(encoding="utf-8")
ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "diagrams" / "integrated"
META = json.loads((ROOT / "verification/schema_metadata.json").read_text("utf-8"))
TABLES = {t["name"]: t for t in META["tables"]}
CONSTRAINTS = META["constraints"]
FKS = [c for c in CONSTRAINTS if c["kind"] == "f"]
FK_BY_NAME = {c["name"]: c for c in FKS}
FK_IDS = {c["name"]: f"F{i:02d}" for i, c in enumerate(FKS, 1)}
NAMES = {
    "user_account": "Пользователь", "district": "Район", "salon": "Салон",
    "service_type": "Вид услуги", "salon_service": "Услуга салона", "master": "Мастер",
    "master_service": "Назначение услуги мастеру", "work_interval": "Рабочий интервал",
    "appointment": "Запись", "review": "Отзыв", "moderation_decision": "Решение модерации",
    "salon_photo": "Фотографии интерьера", "master_photo": "Фотографии работ",
    "master_invitation": "Приглашение мастера",
}
CORE = [n for n in NAMES if n not in ("master_service", "salon_photo", "master_photo", "master_invitation")]

CONCEPT_ATTRS = {
    "user_account": ["user_id", "email", "password_hash", "display_name", "role", "account_status", "created_at"],
    "district": ["district_id", "name", "is_active"],
    "salon": ["salon_id", "name", "description", "address", "latitude, longitude", "phone", "opening_hours", "publication_status", "created_at", "{Фотографии интерьера:", "  file_path, caption, sort_order, visibility}"],
    "service_type": ["service_type_id", "name", "description", "is_active"],
    "salon_service": ["salon_service_id", "name", "description", "price", "duration_minutes", "is_active"],
    "master": ["master_id", "specialization", "experience_description", "is_active", "{Фотографии работ:", "  file_path, caption, sort_order, visibility}"],
    "work_interval": ["work_interval_id", "work_date", "start_time", "end_time"],
    "appointment": ["appointment_id", "start_at, end_at", "service_name_snapshot", "price_snapshot, duration_snapshot", "status", "created_at", "cancelled_at, cancellation_reason", "result_marked_at"],
    "review": ["review_id", "target_type", "rating", "text", "visibility", "created_at"],
    "moderation_decision": ["decision_id", "action", "reason", "created_at", "photo_path (необязательный)"],
}
NOTES = {
    "user_account": ["UQ(email); роль: CLIENT | MASTER | OWNER | ADMIN", "INVITED допустим только для MASTER"],
    "district": ["UQ(name)"],
    "salon": ["UQ(owner_user_id)", "CHECK latitude: -90..90; longitude: -180..180"],
    "service_type": ["UQ(name)"],
    "salon_service": ["CHECK price >= 0; duration_minutes > 0"],
    "master": ["UQ(user_id)"],
    "master_service": ["PK(master_id, salon_service_id)", "Мастер и услуга принадлежат одному салону"],
    "work_interval": ["CHECK start_time < end_time", "EXCLUDE (master_id =, slot &&)"],
    "appointment": ["FK (master_id, salon_service_id) → master_service", "EXCLUDE (master_id =, slot &&), кроме CANCELLED", "CHECK: шаг начала 15 мин; price >= 0; duration > 0", "Сведения об отмене и результате зависят от status"],
    "review": ["UQ(appointment_id, target_type)", "CHECK rating BETWEEN 1 AND 5", "target_type: SALON | MASTER; максимум 2 на запись"],
    "moderation_decision": ["XOR: ровно один из четырёх target_*_id", "photo_path → элемент выбранного салона / мастера", "Составные FK: (target_salon_id, photo_path)", "и (target_master_id, photo_path)"],
    "salon_photo": ["PK(salon_id, file_path)", "CHECK byte_size: 1..5242880; JPEG | PNG", "CHECK sort_order >= 0"],
    "master_photo": ["PK(master_id, file_path)", "CHECK byte_size: 1..5242880; JPEG | PNG", "CHECK sort_order >= 0"],
    "master_invitation": ["UQ(token_hash); один открытый токен на мастера", "CHECK expires_at > created_at", "used_at и revoked_at взаимоисключающие"],
}

FONT_DIR = Path("C:/Windows/Fonts")
FONT_FILES = {"normal": "arial.ttf", "bold": "arialbd.ttf", "italic": "ariali.ttf"}
FONT_CACHE = {}


def font(size, weight="normal"):
    key = size, weight
    if key not in FONT_CACHE:
        FONT_CACHE[key] = ImageFont.truetype(str(FONT_DIR / FONT_FILES[weight]), size)
    return FONT_CACHE[key]


def text_width(value, size, weight="normal"):
    return font(size, weight).getlength(value)


def wrap(value, width, size, weight="normal"):
    result, current = [], ""
    for word in value.split():
        candidate = f"{current} {word}".strip()
        if current and text_width(candidate, size, weight) > width:
            result.append(current)
            current = word
        else:
            current = candidate
    if current:
        result.append(current)
    return result or [""]


def fk_fields(constraint):
    match = re.search(r"FOREIGN KEY \(([^)]+)\) REFERENCES beauty\.([a-z_]+)\(([^)]+)\)", constraint["definition"])
    assert match, constraint
    return match[1].split(", "), match[2], match[3].split(", ")


def pk_fields(name):
    c = next(c for c in CONSTRAINTS if c["table"] == name and c["kind"] == "p")
    return re.search(r"\(([^)]+)\)", c["definition"])[1].split(", ")


def logical_fields(name):
    pk = pk_fields(name)
    unique = [re.search(r"\(([^)]+)\)", c["definition"])[1].split(", ") for c in CONSTRAINTS if c["table"] == name and c["kind"] == "u"]
    refs = {c["name"]: fk_fields(c)[0] for c in FKS if c["table"] == name}
    result = []
    for col in TABLES[name]["columns"]:
        typ = col["type"].upper().replace("TIMESTAMP WITHOUT TIME ZONE", "TIMESTAMP").replace("TIME WITHOUT TIME ZONE", "TIME")
        if col["type"] == "numeric":
            typ = f"NUMERIC({col['precision']},{col['scale']})"
        keys = []
        if col["name"] in pk:
            keys.append("PK")
        foreign=[FK_IDS[k] for k,fields in refs.items() if col["name"] in fields]
        if foreign:
            keys.append("FK "+",".join(foreign))
        if [col["name"]] in unique:
            keys.append("UQ")
        flags=[]
        flags.append("NULL" if col["nullable"] else "NN")
        if col["generated"] == "ALWAYS":
            flags.append("G")
        result.append({"name":col["name"],"type":typ,"keys":", ".join(keys),"flags":" ".join(flags)})
    return result


def logical_rows(name):
    return [f"{c['name']}  {c['type']}  {c['flags']}" for c in logical_fields(name)]


def key_column_width(name):
    return math.ceil(max([text_width(c["keys"],16,"bold") for c in logical_fields(name)]+[24])+22)


def field_spans(field):
    return [(field["name"]+"  ","normal"),(field["type"],"bold"),("  "+field["flags"],"normal")]


def endpoint_cards(e, model):
    """Values describe multiplicity of the entity at each endpoint."""
    if model == "logical":
        c = FK_BY_NAME[e["id"]]
        fields, target, _ = fk_fields(c)
        nullable = any(col["nullable"] for col in TABLES[c["table"]]["columns"] if col["name"] in fields)
        is_unique = any(
            re.search(r"\(([^)]+)\)", x["definition"])[1].split(", ") == fields
            for x in CONSTRAINTS if x["table"] == c["table"] and x["kind"] in ("p", "u")
        )
        child = "0..1" if is_unique else "0..N"
        if c["table"] == "review":
            child = "0..2"
        return child, "0..1" if nullable else "1"
    if e.get("many_to_many") or e.get("cardinality") == "M:N":
        return "0..N", "0..N"
    if e.get("cards"):
        return tuple(e["cards"])
    if e["id"] in FK_BY_NAME:
        return endpoint_cards(e, "logical")
    # Two conceptual references unfold the association's composite key.
    if e["source"] == "appointment" and e["target"] in ("master", "salon_service"):
        return "0..N", "1"
    raise ValueError(f"Missing cardinality for {e}")


def line_intersection(a, b, c, d):
    horizontal1, horizontal2 = a[1] == b[1], c[1] == d[1]
    if horizontal1 == horizontal2:
        if horizontal1 and a[1] == c[1]:
            lo, hi = max(min(a[0], b[0]), min(c[0], d[0])), min(max(a[0], b[0]), max(c[0], d[0]))
        elif not horizontal1 and a[0] == c[0]:
            lo, hi = max(min(a[1], b[1]), min(c[1], d[1])), min(max(a[1], b[1]), max(c[1], d[1]))
        else:
            return None
        if hi>lo+1e-7:
            return "overlap",lo,hi
        return ("touch",lo,hi) if abs(hi-lo)<1e-7 else None
    h1, h2, v1, v2 = (a, b, c, d) if horizontal1 else (c, d, a, b)
    x, y = v1[0], h1[1]
    if min(h1[0], h2[0])-1e-7 <= x <= max(h1[0], h2[0])+1e-7 and min(v1[1], v2[1])-1e-7 <= y <= max(v1[1], v2[1])+1e-7:
        if min(h1[0], h2[0])+1e-7 < x < max(h1[0], h2[0])-1e-7 and min(v1[1], v2[1])+1e-7 < y < max(v1[1], v2[1])-1e-7:
            return x,y
        return "touch",x,y
    return None


def audit_layout(layout, model):
    nodes = layout["nodes"]
    ids = [n["id"] for n in nodes]
    expected = set(TABLES) if model == "logical" else set(CORE)
    assert len(ids) == len(set(ids)) and set(ids) == expected, (model, "unique entities", ids)
    if model == "logical":
        assert {e["id"] for e in layout["edges"]} == set(FK_BY_NAME), "All 25 FK constraints must be drawn"
    for a, b in combinations(nodes, 2):
        assert not (max(a["x"], b["x"]) < min(a["x"]+a["w"], b["x"]+b["w"]) and max(a["y"], b["y"]) < min(a["y"]+a["h"], b["y"]+b["h"])), ("overlapping boxes", a["id"], b["id"])
    segs = []
    for e in layout["edges"]:
        for entity,point in ((e["source"],e["points"][0]),(e["target"],e["points"][-1])):
            n=next(n for n in nodes if n["id"]==entity)
            x,y=point
            assert ((x in (n["x"],n["x"]+n["w"]) and n["y"]<=y<=n["y"]+n["h"]) or
                    (y in (n["y"],n["y"]+n["h"]) and n["x"]<=x<=n["x"]+n["w"])), ("detached endpoint",e)
        for p, q in zip(e["points"], e["points"][1:]):
            assert p != q and (p[0] == q[0] or p[1] == q[1]), ("nonorthogonal", e)
            for n in nodes:
                l, r, t, b = n["x"], n["x"]+n["w"], n["y"], n["y"]+n["h"]
                if p[0] == q[0]:
                    hit = l+1e-6 < p[0] < r-1e-6 and max(min(p[1], q[1]), t) < min(max(p[1], q[1]), b)-1e-6
                else:
                    hit = t+1e-6 < p[1] < b-1e-6 and max(min(p[0], q[0]), l) < min(max(p[0], q[0]), r)-1e-6
                assert not hit, ("line through entity", e["id"], n["id"], p, q)
            segs.append((e["id"], p, q))
    crosses = []
    for a, b in combinations(segs, 2):
        if a[0] == b[0]:
            continue
        hit = line_intersection(a[1], a[2], b[1], b[2])
        if hit:
            assert hit[0] != "overlap", ("overlapping lines", a, b, hit)
            assert hit[0] != "touch", ("ambiguous touching lines",a,b,hit)
            item = {"edge1": a[0], "edge2": b[0], "point": list(hit)}
            if item not in crosses:
                crosses.append(item)
    return {"model": model, "entity_count": len(ids), "relationship_count": len(layout["edges"]), "orthogonal_routes": True,
            "duplicate_entities": 0, "lines_through_boxes": 0, "overlapping_segments": 0,
            "crossings": len(crosses), "all_crossings_have_bridges": True, "crossing_details": crosses}


class Drawing:
    def __init__(self, width, height):
        self.width, self.height = int(math.ceil(width)), int(math.ceil(height))
        self.image = Image.new("RGB", (self.width, self.height), "white")
        self.pen = ImageDraw.Draw(self.image)
        self.commands=[]
        self.svg = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{self.width}" height="{self.height}" viewBox="0 0 {self.width} {self.height}">',
                    '<rect width="100%" height="100%" fill="white"/>']

    def line(self, points, width=2, color="#202020"):
        self.commands.append(("line",points,width,color))
        self.pen.line([tuple(p) for p in points], fill=color, width=width)
        coords = " ".join(f"{x:.2f},{y:.2f}" for x, y in points)
        self.svg.append(f'<polyline points="{coords}" fill="none" stroke="{color}" stroke-width="{width}" stroke-linejoin="miter"/>')

    def rect(self, box, fill="white", stroke="#202020", width=2):
        self.commands.append(("rect",box,fill,stroke,width))
        x, y, w, h = box
        self.pen.rectangle((x, y, x+w, y+h), fill=fill, outline=stroke, width=width)
        self.svg.append(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" fill="{fill}" stroke="{stroke}" stroke-width="{width}"/>')

    def circle(self, x, y, r=6):
        self.commands.append(("circle",x,y,r))
        self.pen.ellipse((x-r, y-r, x+r, y+r), fill="white", outline="#202020", width=2)
        self.svg.append(f'<circle cx="{x}" cy="{y}" r="{r}" fill="white" stroke="#202020" stroke-width="2"/>')

    def text(self, x, y, value, size=20, weight="normal", anchor="left", color="#171717", halo=False):
        width = text_width(value, size, weight)
        left = x-width/2 if anchor == "middle" else x-width if anchor == "right" else x
        if halo:
            self.rect((left-4, y-2, width+8, size+7), "white", "white", 0)
        self.commands.append(("text",x,y,value,size,weight,anchor,color))
        self.pen.text((left, y), value, font=font(size, weight), fill=color, anchor="lt")
        svg_anchor={"left":"start","middle":"middle","right":"end"}[anchor]
        self.svg.append(f'<text x="{x}" y="{y}" dominant-baseline="text-before-edge" text-anchor="{svg_anchor}" font-family="Arial,sans-serif" font-size="{size}" font-weight="{"bold" if weight=="bold" else "normal"}" fill="{color}">{html.escape(value)}</text>')

    def rich_text(self,x,y,spans,size=20):
        for value,weight in spans:
            self.text(x,y,value,size,weight)
            x+=text_width(value,size,weight)

    def bridge(self, x, y, radius=12):
        # Horizontal connection crosses above the vertical connection; no junction dot.
        self.line([(x-radius+2,y),(x+radius-2,y)],width=6,color="white")
        self.line([(x,y-6),(x,y+6)],width=2)
        points = [(x-radius+2*radius*i/30, y-radius*math.sin(math.pi*i/30)) for i in range(31)]
        self.pen.line(points, fill="white", width=8)
        self.pen.line(points, fill="#202020", width=2)
        self.svg.append(f'<path d="M {x-radius} {y} A {radius} {radius} 0 0 1 {x+radius} {y}" fill="none" stroke="white" stroke-width="8"/>')
        self.svg.append(f'<path d="M {x-radius} {y} A {radius} {radius} 0 0 1 {x+radius} {y}" fill="none" stroke="#202020" stroke-width="2"/>')
        self.commands.append(("bridge",x,y,radius))

    def vertical_text(self,x,y,value,size=18):
        self.commands.append(("vertical_text",x,y,value,size))
        w=math.ceil(text_width(value,size))+12
        tile=Image.new("RGBA",(w,size+12),(255,255,255,255))
        ImageDraw.Draw(tile).text((6,5),value,font=font(size),fill="#171717",anchor="lt")
        tile=tile.rotate(90,expand=True,resample=Image.Resampling.BICUBIC)
        self.image.paste(tile,(round(x-tile.width/2),round(y-tile.height/2)),tile)
        self.svg.append(f'<rect x="{x-(size+12)/2}" y="{y-w/2}" width="{size+12}" height="{w}" fill="white"/>')
        self.svg.append(f'<text transform="translate({x},{y}) rotate(-90)" text-anchor="middle" dominant-baseline="middle" font-family="Arial,sans-serif" font-size="{size}" fill="#171717">{html.escape(value)}</text>')

    def export_pdf(self,path,height):
        path.parent.mkdir(parents=True,exist_ok=True)
        for weight in ("normal","bold"):
            name="Diagram-"+weight
            if name not in pdfmetrics.getRegisteredFontNames():
                pdfmetrics.registerFont(TTFont(name,str(FONT_DIR/FONT_FILES[weight])))
        c=pdfcanvas.Canvas(str(path),pagesize=(self.width,height))
        c.setTitle("Integrated database model")
        for command in self.commands:
            kind,*args=command
            if kind=="line":
                points,width,color=args
                c.setStrokeColor(toColor(color));c.setLineWidth(width)
                p=c.beginPath();p.moveTo(points[0][0],height-points[0][1])
                for x,y in points[1:]:p.lineTo(x,height-y)
                c.drawPath(p)
            elif kind=="rect":
                (x,y,w,h),fill,stroke,width=args
                c.setFillColor(toColor(fill));c.setStrokeColor(toColor(stroke));c.setLineWidth(width)
                c.rect(x,height-y-h,w,h,fill=1,stroke=int(width>0))
            elif kind=="circle":
                x,y,r=args
                c.setFillColor(toColor("#ffffff"));c.setStrokeColor(toColor("#202020"));c.setLineWidth(2)
                c.circle(x,height-y,r,fill=1,stroke=1)
            elif kind=="text":
                x,y,value,size,weight,anchor,color=args
                width=text_width(value,size,weight)
                left=x-width/2 if anchor=="middle" else x-width if anchor=="right" else x
                top=font(size,weight).getbbox(value or "A",anchor="ls")[1]
                c.setFillColor(toColor(color));c.setFont("Diagram-"+weight,size)
                c.drawString(left,height-y+top,value)
            elif kind=="bridge":
                x,y,r=args
                for color,width in (("#ffffff",8),("#202020",2)):
                    c.setStrokeColor(toColor(color));c.setLineWidth(width)
                    c.arc(x-r,height-y-r,x+r,height-y+r,startAng=0,extent=180)
            elif kind=="vertical_text":
                x,y,value,size=args
                width=text_width(value,size)+12
                c.setFillColor(toColor("#ffffff"));c.rect(x-(size+12)/2,height-y-width/2,size+12,width,fill=1,stroke=0)
                c.saveState();c.translate(x,height-y);c.rotate(90)
                c.setFillColor(toColor("#171717"));c.setFont("Diagram-normal",size)
                c.drawCentredString(0,-size*.35,value);c.restoreState()
        c.save()

    def cardinality(self, p, q, value):
        dx, dy = q[0]-p[0], q[1]-p[1]
        length = math.hypot(dx, dy)
        assert length >= 40, ("Too short endpoint for crow's foot", p, q)
        ux, uy = dx/length, dy/length
        nx, ny = -uy, ux
        def at(a, b=0):
            return p[0]+a*ux+b*nx, p[1]+a*uy+b*ny
        if value in ("0..N", "0..2", "1..N"):
            for v in (-8, 0, 8):
                self.line([at(1, v), at(16)])
            if value.startswith("0"):
                self.circle(*at(29), r=6)
            else:
                self.line([at(27,-9),at(27,9)])
            if value == "0..2":
                x,y=at(50, 13)
                if abs(uy)<.1:
                    x,y=p[0]+50*ux,p[1]+18
                self.text(x,y,"≤2",16,halo=True)
        else:
            self.line([at(9,-9),at(9,9)])
            if value == "0..1":
                self.circle(*at(25),r=6)
            else:
                self.line([at(21,-9),at(21,9)])


def body_lines(n, model, size):
    values = logical_rows(n["id"]) if model == "logical" else CONCEPT_ATTRS[n["id"]]
    rows = [(line,"normal") for value in values for line in wrap(value,n["w"]-30,size)]
    notes = NOTES[n["id"]] if model == "logical" else []
    if notes:
        rows.append(("","separator"))
        rows.extend((line,"note") for value in notes for line in wrap(value,n["w"]-30,size-2))
    return rows


def content_dimensions(entity, model):
    """Fit each box to its own text; keep the original readable font sizes."""
    size=22 if model=="er" else 20
    values=logical_rows(entity) if model=="logical" else CONCEPT_ATTRS[entity]
    widths=[text_width(value,size) for value in values]
    if model=="logical":
        widths=[key_column_width(entity)+sum(text_width(v,size,w) for v,w in field_spans(c)) for c in logical_fields(entity)]
    widths.extend((text_width(NAMES[entity],23,"bold"),text_width(entity,18)))
    width=max(220,math.ceil((max(widths)+30)/10)*10)
    n={"id":entity,"w":width}
    height=94+len(body_lines(n,model,size))*(size+7)
    return width,height


def compact_layout(layout, model):
    """Compact the route corridors, then fit individual boxes inside their slots."""
    layout=json.loads(json.dumps(layout))
    desired={n["id"]:content_dimensions(n["id"],model) for n in layout["nodes"]}
    for axis,coord,extent in ((0,"x","w"),(1,"y","h")):
        values=sorted({p[axis] for e in layout["edges"] for p in e["points"]} |
                      {n[coord] for n in layout["nodes"]} | {n[coord]+n[extent] for n in layout["nodes"]})
        index={v:i for i,v in enumerate(values)}
        constraints={i:[] for i in range(len(values))}
        for n in layout["nodes"]:
            constraints[index[n[coord]+n[extent]]].append((index[n[coord]],desired[n["id"]][axis]))
        for e in layout["edges"]:
            for p,q in ((e["points"][0],e["points"][1]),(e["points"][-1],e["points"][-2])):
                if p[axis]!=q[axis]:
                    lo,hi=sorted((p[axis],q[axis]))
                    constraints[index[hi]].append((index[lo],80 if len(e["points"])==2 else 40))
        positions=[0]*len(values)
        positions[0]=100 if axis==0 else 140
        for i in range(1,len(values)):
            positions[i]=max([positions[i-1]+32]+[positions[j]+gap for j,gap in constraints[i]])
        mapping=dict(zip(values,positions))
        for n in layout["nodes"]:
            left,right=mapping[n[coord]],mapping[n[coord]+n[extent]]
            n[coord],n[extent]=left,right-left
        for e in layout["edges"]:
            for p in e["points"]:
                p[axis]=mapping[p[axis]]
    fitted=[]
    for n in layout["nodes"]:
        slot=dict(n)
        ports=[]
        for e in layout["edges"]:
            for end,key in ((0,"source"),(-1,"target")):
                if e[key]!=n["id"]:
                    continue
                p=e["points"][end]
                sides=[]
                if p[0]==slot["x"]:sides.append("left")
                if p[0]==slot["x"]+slot["w"]:sides.append("right")
                if p[1]==slot["y"]:sides.append("top")
                if p[1]==slot["y"]+slot["h"]:sides.append("bottom")
                assert len(sides)==1,("ambiguous corner port",n["id"],p)
                ports.append((e,end,sides[0]))
        for axis,coord,extent,tangent_sides in ((0,"x","w",("top","bottom")),(1,"y","h",("left","right"))):
            tangential=[e["points"][end][axis] for e,end,side in ports if side in tangent_sides]
            wanted=desired[n["id"]][axis]
            padding=18
            if tangential:
                span=max(tangential)-min(tangential)
                padding=min(18,max(8,(wanted-span)/2))
                wanted=max(wanted,span+2*padding)
            wanted=min(wanted,slot[extent])
            lo,hi=slot[coord],slot[coord]+slot[extent]-wanted
            if tangential:
                lo=max(lo,max(tangential)+padding-wanted)
                hi=min(hi,min(tangential)-padding)
            if lo>hi:
                lo,hi=slot[coord],slot[coord]+slot[extent]-wanted
                if tangential:
                    lo=max(lo,max(tangential)-wanted)
                    hi=min(hi,min(tangential))
            assert lo<=hi,(n["id"],coord,"port span does not fit")
            n[coord]=min(max(slot[coord]+(slot[extent]-wanted)/2,lo),hi)
            n[extent]=wanted
        for e,end,side in ports:
            if side in ("left","right"):
                e["points"][end][0]=n["x"]+(n["w"] if side=="right" else 0)
            else:
                e["points"][end][1]=n["y"]+(n["h"] if side=="bottom" else 0)
        fitted.append({"entity":n["id"],"text_size":list(desired[n["id"]]),"box_size":[n["w"],n["h"]]})
    if model=="logical":
        appointment=next(n for n in layout["nodes"] if n["id"]=="appointment")
        review=next(n for n in layout["nodes"] if n["id"]=="review")
        review["x"]=appointment["x"]+appointment["w"]+120
        review["y"]=appointment["y"]+150
        for e in layout["edges"]:
            if e["id"]=="review_appointment_id_fkey":
                y=appointment["y"]+300
                e["points"]=[[review["x"],y],[appointment["x"]+appointment["w"],y]]
            elif e["id"]=="moderation_decision_target_review_id_fkey":
                e["points"][-2][1]=review["y"]+40
                e["points"][-1]=[review["x"]+review["w"],review["y"]+40]
    layout.pop("crossings",None)
    layout.pop("collisions",None)
    layout["canvas"]={"width":max(n["x"]+n["w"] for n in layout["nodes"])+100,
                      "height":max(n["y"]+n["h"] for n in layout["nodes"])+100}
    layout["content_fit"]=fitted
    return layout


def relation_label(e,model):
    if model=="logical":
        return FK_IDS[e["id"]]
    return {
        "salon_owner_user_id_fkey":"владелец", "master_user_id_fkey":"профиль",
        "appointment_client_user_id_fkey":"клиент", "appointment_cancelled_by_user_id_fkey":"отменил",
        "appointment_result_marked_by_user_id_fkey":"отметил результат",
        "moderation_decision_admin_user_id_fkey":"ADMIN",
        "moderation_decision_target_user_id_fkey":"цель USER",
        "master_provides_salon_service":"выполняет [M:N]",
    }.get(e["id"],e.get("label",""))


def label_position(e,label,layout,occupied):
    w=text_width(label,18)+12
    candidates=[]
    for p,q in zip(e["points"],e["points"][1:]):
        length=abs(q[0]-p[0])+abs(q[1]-p[1])
        if length<40:
            continue
        for fraction in (.5,.35,.65,.2,.8):
            x,y=p[0]+(q[0]-p[0])*fraction,p[1]+(q[1]-p[1])*fraction
            if p[1]==q[1]:
                candidates.extend(((x,y-27,False),(x,y+6,False)))
            else:
                candidates.extend(((x+w/2+9,y-10,False),(x-w/2-9,y-10,False)))
    for p,q in zip(e["points"],e["points"][1:]):
        if p[0]==q[0] and abs(q[1]-p[1])>w+50:
            for fraction in (.5,.35,.65,.2,.8):
                y=p[1]+(q[1]-p[1])*fraction
                candidates.extend(((p[0]+22,y,True),(p[0]-22,y,True)))
    for x,y,rotate in candidates:
        l,r,t,b=(x-15,x+15,y-w/2,y+w/2) if rotate else (x-w/2,x+w/2,y-3,y+24)
        if any(max(l,n["x"]-8)<min(r,n["x"]+n["w"]+8) and max(t,n["y"]-8)<min(b,n["y"]+n["h"]+8) for n in layout["nodes"]):
            continue
        if any(max(l,a)<min(r,c) and max(t,b0)<min(b,d) for a,b0,c,d in occupied):
            continue
        hit=False
        for other in layout["edges"]:
            if other["id"]==e["id"]:
                continue
            for p,q in zip(other["points"],other["points"][1:]):
                if p[0]==q[0]:
                    hit |= l<p[0]<r and max(t,min(p[1],q[1]))<min(b,max(p[1],q[1]))
                else:
                    hit |= t<p[1]<b and max(l,min(p[0],q[0]))<min(r,max(p[0],q[0]))
        if not hit:
            occupied.append((l,t,r,b))
            return x,y,rotate
    raise ValueError(f"No collision-free label placement: {e['id']}, {label}")


def write_drawio(path, layout, model, node_rows):
    root=ET.Element("mxfile",host="app.diagrams.net",version="26.0.0")
    diagram=ET.SubElement(root,"diagram",name="ER-модель" if model=="er" else "Даталогическая модель")
    graph=ET.SubElement(diagram,"mxGraphModel",dx="1800",dy="1200",grid="1",gridSize="10",guides="1",tooltips="1",connect="1",arrows="1",fold="1",page="0",pageScale="1",math="0",shadow="0",lineJumps="1")
    cells=ET.SubElement(graph,"root")
    ET.SubElement(cells,"mxCell",id="0")
    ET.SubElement(cells,"mxCell",id="1",parent="0")
    by={n["id"]:n for n in layout["nodes"]}
    for n in layout["nodes"]:
        size,rows=node_rows[n["id"]]
        title=html.escape(NAMES[n["id"]])+"<br><span style='font-size:18px;font-weight:normal'>"+html.escape(n["id"])+"</span>"
        value="<div style='font-family:Arial;text-align:center;font-size:23px;height:62px;line-height:27px'><b>"+title+"</b></div><div style='border-top:1px solid #202020'></div>"
        if model=="logical":
            kw=key_column_width(n["id"])
            value+="<table style='border-collapse:collapse;width:100%;font-family:Arial'>"
            for field in logical_fields(n["id"]):
                spans=html.escape(field["name"])+" &nbsp;<b>"+html.escape(field["type"])+"</b> &nbsp;"+html.escape(field["flags"])
                value+=f"<tr style='height:{size+7}px'><td style='border-right:1px solid #202020;width:{kw}px;text-align:center;font-size:16px;white-space:nowrap'><b>{html.escape(field['keys'])}</b></td><td style='text-align:left;padding-left:12px;font-size:{size}px;white-space:nowrap'>{spans}</td></tr>"
            value+="</table>"
            extra=rows[len(logical_fields(n["id"])):]
        else:
            extra=rows
        for v,k in extra:
            border="border-top:1px solid #777;" if k=="separator" else ""
            padding="padding-left:14px;padding-right:14px;box-sizing:border-box;" if model=="logical" else ""
            value+="<div style='font-family:Arial;text-align:left;"+padding+"line-height:"+str(size+7)+"px;height:"+str(size+7)+"px;"+border+"font-size:"+str(size if k=="normal" else size-2)+"px'>"+html.escape(v or " ")+"</div>"
        spacing=0 if model=="logical" else 14
        cell=ET.SubElement(cells,"mxCell",id=n["id"],value=value,style=f"rounded=0;whiteSpace=wrap;html=1;fillColor=#ffffff;strokeColor=#202020;strokeWidth=2;align=left;verticalAlign=top;spacingLeft={spacing};spacingRight={spacing};spacingTop=8;spacingBottom=8;overflow=hidden;",vertex="1",parent="1")
        ET.SubElement(cell,"mxGeometry",x=str(n["x"]),y=str(n["y"]),width=str(n["w"]),height=str(n["h"]),**{"as":"geometry"})
    arrows={"1":"ERmandOne","0..1":"ERzeroToOne","0..N":"ERzeroToMany","0..2":"ERzeroToMany","1..N":"ERmany"}
    for e in layout["edges"]:
        a,b=endpoint_cards(e,model)
        src,tgt=by[e["source"]],by[e["target"]]
        p,q=e["points"][0],e["points"][-1]
        style=f"edgeStyle=none;rounded=0;html=1;strokeWidth=2;strokeColor=#202020;startArrow={arrows[a]};endArrow={arrows[b]};startFill=0;endFill=0;jumpStyle=arc;jumpSize=16;exitX={(p[0]-src['x'])/src['w']};exitY={(p[1]-src['y'])/src['h']};entryX={(q[0]-tgt['x'])/tgt['w']};entryY={(q[1]-tgt['y'])/tgt['h']};exitPerimeter=0;entryPerimeter=0;"
        label=relation_label(e,model)
        cell=ET.SubElement(cells,"mxCell",id="edge_"+e["id"],value=label,edge="1",parent="1",source=e["source"],target=e["target"],style=style)
        geom=ET.SubElement(cell,"mxGeometry",relative="1",**{"as":"geometry"})
        arr=ET.SubElement(geom,"Array",**{"as":"points"})
        for x,y in e["points"][1:-1]:
            ET.SubElement(arr,"mxPoint",x=str(x),y=str(y))
        if label and "label_at" in e:
            segs=list(zip(e["points"],e["points"][1:]))
            total=sum(abs(q[0]-p[0])+abs(q[1]-p[1]) for p,q in segs)
            walked=0
            for p,q in segs:
                distance=abs(q[0]-p[0])+abs(q[1]-p[1])
                if walked+distance>=total/2:
                    fraction=(total/2-walked)/distance
                    midpoint=[p[0]+(q[0]-p[0])*fraction,p[1]+(q[1]-p[1])*fraction]
                    break
                walked+=distance
            ET.SubElement(geom,"mxPoint",x=str(e["label_at"][0]-midpoint[0]),y=str(e["label_at"][1]+10-midpoint[1]),**{"as":"offset"})
    ET.indent(root)
    ET.ElementTree(root).write(path,encoding="utf-8",xml_declaration=True)


def render(layout, model):
    audit=audit_layout(layout,model)
    all_x=[p[0] for e in layout["edges"] for p in e["points"]]
    all_y=[p[1] for e in layout["edges"] for p in e["points"]]
    assert min(all_x)>=50 and min(all_y)>=100
    width=max([n["x"]+n["w"] for n in layout["nodes"]]+all_x)+90
    bottom=max([n["y"]+n["h"] for n in layout["nodes"]]+all_y)+(40 if model=="logical" else 90)
    footer_height=0 if model=="logical" else 240
    drawing=Drawing(width,bottom+footer_height)
    drawing.text(60,20,"ER-модель" if model=="er" else "Даталогическая модель PostgreSQL",32,"bold")
    sub="10 сущностей · связь M:N показана напрямую" if model=="er" else "14 таблиц · 25 внешних ключей · фактические типы PostgreSQL"
    drawing.text(60,64,sub,20)
    occupied=[]
    for e in layout["edges"]:
        drawing.line(e["points"])
    for cross in audit["crossing_details"]:
        drawing.bridge(*cross["point"])
    for e in layout["edges"]:
        a,b=endpoint_cards(e,model)
        drawing.cardinality(e["points"][0],e["points"][1],a)
        drawing.cardinality(e["points"][-1],e["points"][-2],b)
        label=relation_label(e,model)
        if label:
            x,y,rotate=label_position(e,label,layout,occupied)
            e["label_at"]=[x,y]
            e["label_rotate"]=rotate
            if rotate:
                drawing.vertical_text(x,y,label)
            else:
                drawing.text(x,y,label,18,anchor="middle",halo=True)
    node_rows={}
    for n in layout["nodes"]:
        size=22 if model=="er" else 20
        rows=body_lines(n,model,size)
        needed=94+len(rows)*(size+7)
        assert needed<=n["h"],("Text does not fit",n["id"],needed,n["h"])
        node_rows[n["id"]]=(size,rows)
        x,y,w,h=n["x"],n["y"],n["w"],n["h"]
        drawing.rect((x,y,w,h))
        drawing.text(x+w/2,y+10,NAMES[n["id"]],23,"bold","middle")
        drawing.text(x+w/2,y+40,n["id"],18,anchor="middle")
        drawing.line([(x,y+70),(x+w,y+70)])
        row_y=y+83
        if model=="logical":
            kw=key_column_width(n["id"])
            fields=logical_fields(n["id"])
            drawing.line([(x+kw,y+70),(x+kw,row_y+len(fields)*(size+7)+3)],width=1)
            for field in fields:
                drawing.text(x+kw/2,row_y+2,field["keys"],16,"bold","middle")
                drawing.rich_text(x+kw+12,row_y,field_spans(field),size)
                row_y+=size+7
            extra=rows[len(fields):]
        else:
            extra=rows
        for value,kind in extra:
            if kind=="separator":
                drawing.line([(x+1,row_y+3),(x+w-1,row_y+3)],width=1,color="#777777")
            else:
                drawing.text(x+14,row_y,value,size if kind=="normal" else size-2)
            row_y+=size+7
    stem="er_model" if model=="er" else "logical_model"
    drawing.export_pdf(ROOT/"report/figures"/f"{stem}.pdf",bottom)
    if model=="er":
        drawing.line([(60,bottom),(width-60,bottom)],width=1,color="#777777")
    legend=[
        "Обозначения: || — ровно 1; ○| — 0..1; ○< — 0..N. Дуга на пересечении — линии не соединены.",
        "Каждая сущность показана один раз. Чёрные точки соединения не используются: отдельные линии — отдельные связи.",
    ]
    if model=="logical":
        legend += ["PK — первичный ключ; F01…F25 — внешние ключи; UQ — уникальность; NN — NOT NULL; G — вычисляемый столбец.",
                   "TIMESTAMP — timestamp without time zone, Europe/Moscow. Все FK: ON DELETE RESTRICT.",
                   "Четыре target_*_id решения модерации образуют XOR. Составные FK фотографий показаны отдельными линиями.",
                   "F01…F25 одинаково обозначены у полей таблиц и на соответствующих линиях."]
    else:
        legend += ["{…} — составной многозначный атрибут фотографии. Он не является отдельной сущностью.",
                   "Связь «выполняет» M:N имеет атрибут is_active; в отношениях она преобразуется в master_service.",
                   "Четыре цели модерации: XOR. Автор и объект отзыва определяются через выполненную запись.",
                   "Запись выбирает существующую пару «мастер—услуга» из связи M:N; отзывов на запись не более двух."]
    if model=="er":
        for i,value in enumerate(legend):
            drawing.text(60,bottom+22+i*31,value,21)
    drawing.svg.append("</svg>")
    stem="er_model" if model=="er" else "logical_model"
    (OUT/f"{stem}.svg").write_text("\n".join(drawing.svg),encoding="utf-8")
    drawing.image.save(OUT/f"{stem}.png",optimize=True)
    preview=drawing.image.copy()
    preview.thumbnail((2200,2200),Image.Resampling.LANCZOS)
    preview.save(OUT/f"{stem}_preview.png",optimize=True)
    write_drawio(OUT/f"{stem}.drawio",layout,model,node_rows)
    audit["canvas_pixels"]=[drawing.width,drawing.height]
    audit["body_font_px"]=22 if model=="er" else 20
    audit["all_boxes_fit_content"]=all([n["w"],n["h"]]==list(content_dimensions(n["id"],model)) for n in layout["nodes"])
    if model=="logical":
        audit["separate_bold_key_column"]=True
        audit["bold_data_types"]=True
        audit["bottom_legend_removed"]=True
    return audit


def main():
    OUT.mkdir(parents=True,exist_ok=True)
    report=ROOT/"report/stage2_report.tex"
    pdf=ROOT/"output/pdf/stage2_report.pdf"
    protected={str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in (report,pdf)}
    audits=[]
    for model in ("er","logical"):
        path=Path(__file__).parent/"diagram_layouts"/f"{model}.json"
        layout=compact_layout(json.loads(path.read_text("utf-8")),model)
        audits.append(render(layout,model))
        (OUT/f"{model}_layout.json").write_text(json.dumps(layout,ensure_ascii=False,indent=2),encoding="utf-8")
    assert all(hashlib.sha256((ROOT/p).read_bytes()).hexdigest()==digest for p,digest in protected.items())
    evidence={"models":audits,"report_unchanged_sha256":protected,"source_metadata":"verification/schema_metadata.json"}
    (OUT/"geometry_checks.json").write_text(json.dumps(evidence,ensure_ascii=False,indent=2),encoding="utf-8")
    print(json.dumps(evidence,ensure_ascii=False,indent=2))


if __name__=="__main__":
    main()
