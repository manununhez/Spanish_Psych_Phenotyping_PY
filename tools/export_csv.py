# tools/export_csv.py
import yaml, pandas as pd, pathlib
lex = pathlib.Path("assets/lexicons/depression_anxiety/concepts_PY.yml")
rows = []
for item in yaml.safe_load(lex.read_text(encoding="utf-8")):
    rows.append({
        "canonical_label": item.get("canonical_label",""),
        "core_terms": "; ".join(item.get("core_terms",[])),
        "variants_py": "; ".join(item.get("variants_py",[])),
        "scale_item": item.get("scale_item",""),
        "code_system": item.get("code_system",""),
        "code": item.get("code",""),
        "notes": item.get("notes","")
    })
df = pd.DataFrame(rows, columns=["canonical_label","core_terms","variants_py","scale_item","code_system","code","notes"])
out = pathlib.Path("assets/lexicons/depression_anxiety/diccionario_PY.csv")
df.to_csv(out, index=False, encoding="utf-8")
print(f"Exportado: {out}")
