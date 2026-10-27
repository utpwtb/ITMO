"""Verify diagram typography, report SQL excerpts, highlights, and source packaging."""
from pathlib import Path
import json
import re
import xml.etree.ElementTree as ET
from zipfile import ZipFile, ZIP_DEFLATED

from pypdf import PdfReader
import draw_integrated_models as d

S=Path(__file__).resolve().parents[1]
FOLDER=S/"diagrams/integrated"


def tokens(sql):
    sql=re.sub(r"--[^\n]*","",sql)
    values=re.findall(r"'(?:''|[^'])*'|[A-Za-z_][A-Za-z0-9_]*|\d+|::|<>|>=|<=|=>|[^\s]",sql)
    return [v if v.startswith("'") else v.lower() for v in values]


def contains(sequence,part):
    return any(sequence[i:i+len(part)]==part for i in range(len(sequence)-len(part)+1))


def main():
    layout=json.loads((FOLDER/"logical_layout.json").read_text("utf-8"))
    audit=d.audit_layout(layout,"logical")
    svg=ET.parse(FOLDER/"logical_model.svg")
    texts=svg.findall(".//{http://www.w3.org/2000/svg}text")
    def find(value,x,y,weight):
        return any((n.text or "")==value and abs(float(n.get("x"))-x)<.01 and abs(float(n.get("y"))-y)<.01 and n.get("font-weight")==weight for n in texts)
    fields=0
    key_cells=0
    for node in layout["nodes"]:
        kw=d.key_column_width(node["id"])
        y=node["y"]+83
        for field in d.logical_fields(node["id"]):
            if field["keys"]:
                assert find(field["keys"],node["x"]+kw/2,y+2,"bold")
                key_cells+=1
            x=node["x"]+kw+12
            assert find(field["name"]+"  ",x,y,"normal")
            x+=d.text_width(field["name"]+"  ",20)
            assert find(field["type"],x,y,"bold")
            assert field["flags"] in ("NULL","NOT NULL")
            fields+=1
            y+=27
    assert not any((n.text or "").startswith("Обозначения:") for n in texts)
    rendered="\n".join(n.text or "" for n in texts)
    assert not re.search(r"\b(?:NN|UQ|G|CHECK)\b",rendered)
    assert "максимум 2 на запись" not in rendered
    assert "NOT NULL" in rendered and "UNIQUE" in rendered
    for model,vertices,edges in (("er",10,19),("logical",14,25)):
        cells=ET.parse(FOLDER/f"{model}_model.drawio").findall(".//mxCell")
        assert sum(n.get("vertex")=="1" for n in cells)==vertices
        assert sum(n.get("edge")=="1" for n in cells)==edges
    tex=(S/"report/stage2_report.tex").read_text("utf-8")
    blocks=re.findall(r"\\begin\{lstlisting\}\[style=sql\]\s*(.*?)\\end\{lstlisting\}",tex,re.S)
    source=(S/"sql/04_routines.sql").read_text("utf-8")
    actual=re.search(r"CREATE FUNCTION beauty\.book_appointment\(.*?END \$\$;",source,re.S)[0]
    shown=next(b for b in blocks if b.startswith("CREATE FUNCTION beauty.book_appointment"))
    assert tokens(shown)==tokens(actual),"Displayed booking function differs from implemented SQL"
    ddl=(S/"sql/01_tables.sql").read_text("utf-8")
    actual_tables={re.search(r"CREATE TABLE beauty\.([a-z_]+)",statement)[1]:statement for statement in re.findall(r"CREATE TABLE beauty\.[a-z_]+ \(.*?\n\);",ddl,re.S)}
    shown_tables={re.search(r"CREATE TABLE beauty\.([a-z_]+)",b)[1]:b for b in blocks if b.startswith("CREATE TABLE beauty.")}
    assert len(actual_tables)==14 and set(shown_tables)==set(actual_tables)
    for name,actual_table in actual_tables.items():
        assert tokens(shown_tables[name])==tokens(actual_table),("DDL differs from implementation",name)
    assert r"\section{Скрипты и воспроизведение}" not in tex
    assert r"\section{Результаты проверки}" not in tex
    assert "Концептуальная модель содержит" not in tex
    assert "Преобразование" not in tex
    markdown=(S/"OPERATIONS_AND_VERIFICATION.md").read_text("utf-8")
    assert "## 7. Скрипты и воспроизведение" in markdown
    assert "## 8. Результаты проверки" in markdown
    assert "79 из 79" in markdown and "```bash" in markdown
    assert r"\begin{" not in markdown
    index_sql=tokens((S/"sql/05_indexes.sql").read_text("utf-8"))
    index_block=next(b for b in blocks if b.startswith("CREATE INDEX"))
    for statement in index_block.split(";"):
        if statement.strip():
            assert contains(index_sql,tokens(statement+";"))
    review_check=next(b for b in blocks if b.startswith("IF NOT EXISTS"))
    assert contains(tokens((S/"sql/03_integrity.sql").read_text("utf-8")),tokens(review_check))
    pdf=PdfReader(str(S/"output/pdf/stage2_report.pdf"))
    assert "Заключение" in pdf.pages[-1].extract_text()
    assert sum(float(p.mediabox.width)>1000 for p in pdf.pages)==2
    colors=set()
    for page in pdf.pages:
        for operands,operator in page.get_contents().operations:
            if operator==b"rg":
                colors.add(tuple(round(float(v),3) for v in operands))
    expected=[(23/255,63/255,120/255),(106/255,43/255,138/255),(37/255,97/255,59/255)]
    for color in expected:
        assert tuple(round(v,3) for v in color) in colors,"Missing SQL syntax highlight color"
    pdf_tables=[]
    for page in pdf.pages:
        pdf_tables.extend(re.findall(r"CREATE\s+TABLE\s+beauty\.([a-z_]+)",page.extract_text() or ""))
    assert len(pdf_tables)==14 and set(pdf_tables)==set(actual_tables),pdf_tables
    # A portable source package: the main TeX and exactly the two referenced figures.
    destination=S/"output/stage2_report_sources.zip"
    with ZipFile(destination,"w",ZIP_DEFLATED) as archive:
        for name in ("stage2_report.tex","figures/er_model_a3.pdf","figures/logical_model_a2.pdf"):
            archive.write(S/"report"/name,name)
        archive.write(S/"OPERATIONS_AND_VERIFICATION.md","OPERATIONS_AND_VERIFICATION.md")
        archive.writestr("README.txt","Compile stage2_report.tex twice with XeLaTeX.\nKeep the figures/ directory beside the TeX file.\nSQL highlighting uses listings and does not require shell-escape.\nThe font setup falls back from Windows fonts to CMU fonts.\n")
    with ZipFile(destination) as archive:
        assert archive.testzip() is None
    result={"pdf_pages":len(pdf.pages),"foldout_pages":2,"logical_tables":14,
            "logical_fields":fields,"bold_key_cells":key_cells,"bold_types":fields,
            "bottom_description_removed":True,"logical_relationships":audit["relationship_count"],
            "full_NOT_NULL_and_UNIQUE":True,"no_G_or_box_constraint_notes":True,
            "complete_CREATE_TABLE_statements":len(shown_tables),
            "model_sections_have_no_preface":True,"former_sections_7_8_in_markdown":True,
            "SQL_excerpts_match_implementation":True,"SQL_highlight_colors_present":True,
            "source_archive":str(destination),"source_archive_CRC_valid":True}
    (S/"verification/report_artifact_checks.json").write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding="utf-8")
    print(json.dumps(result,ensure_ascii=False,indent=2))


if __name__=="__main__":
    main()
