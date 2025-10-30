#!/usr/bin/env python3
# ===============================================================
# CLI — Psych Phenotyping (A/D)
# Perfiles:
#   - col: usa patrones del repo colombiano (Concept/)
#   - py : usa tus patrones locales (Concept_PY/)
# ===============================================================
import argparse, pathlib, yaml, pandas as pd
from escribe.default_nlp import nlp, select_concepts

BASE = pathlib.Path(__file__).parent

def load_yaml(path):
    with open(path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)

def build_pipeline(profile: str, fenos_cfg: dict):
    """
    Construye el pipeline cargando SOLO los conceptos activos.
    Para 'col': carga desde escribe/patterns/Concept/
    Para 'py' : carga desde escribe/patterns/Concept_PY/
    Además permite, si lo deseas, filtrar por archivos dentro de cada concepto
    (opcional: ver configs/fenotipos.yml: 'include_files').
    """
    if profile == "col":
        json_dir = None
        concepts = fenos_cfg["active_concepts"]  # p.ej. ["Ansiedad","Depresion","Sueno"]
        nlp_obj = select_concepts(nlp, concepts=concepts)
    elif profile == "py":
        json_dir = str(BASE / "escribe" / "patterns" / "Concept_PY")
        nlp_obj = select_concepts(nlp, json_dir=json_dir)  # carga TODO lo de Concept_PY/*
        # Si querés limitar a 'active_concepts' dentro de Concept_PY, mantenemos el flag:
        # (select_concepts no filtra por subcarpeta; al cargar por json_dir ya va todo lo que haya)
    else:
        raise ValueError("Perfil no reconocido. Usa 'col' o 'py'.")

    return nlp_obj

def collapse_to_AD(doc):
    """
    Colapsa entidades a una etiqueta {depresion, ansiedad, sueno, neutral}.
    Regla simple: cuenta hits válidos (no negados) por familias semánticas.
    """
    dep_hits, anx_hits, slp_hits = 0, 0, 0
    dep_terms, anx_terms, slp_terms = [], [], []
    for ent in getattr(doc, "ents", []):
        if getattr(ent._, "is_negated", False):
            continue
        lab = ent.label_.lower()
        # Agrupación por nombre de label. Ajusta si tus labels cambian:
        if "depres" in lab or "anhedon" in lab or "suicid" in lab or "culpa" in lab or "desesper" in lab or "apat" in lab or "psicomot" in lab or "concentr" in lab or "triste" in lab:
            dep_hits += 1; dep_terms.append(ent.label_)
        elif "ansie" in lab or "miedo" in lab or "temor" in lab or "angu" in lab or "irritab" in lab or "evit" in lab or "pan" in lab or "vigil" in lab:
            anx_hits += 1; anx_terms.append(ent.label_)
        elif "sue" in lab or "insom" in lab or "hipersom" in lab:
            slp_hits += 1; slp_terms.append(ent.label_)

    if dep_hits == anx_hits == slp_hits == 0:
        return "neutral", 0, ""
    # prioridad por la mayor cuenta; si empata con sueño, prioriza A/D
    if dep_hits >= anx_hits and dep_hits >= slp_hits:
        return "depresion", dep_hits, ";".join(dep_terms)
    if anx_hits >= dep_hits and anx_hits >= slp_hits:
        return "ansiedad", anx_hits, ";".join(anx_terms)
    return "sueno", slp_hits, ";".join(slp_terms)

def run(profile: str, config_name: str, input_csv: pathlib.Path, output_csv: pathlib.Path):
    cfg = load_yaml(BASE / "configs" / config_name)
    fenos_cfg = load_yaml(BASE / "configs" / "fenotipos.yml")
    text_col = cfg["text_column"]

    nlp_obj = build_pipeline(profile, fenos_cfg)

    df = pd.read_csv(input_csv)
    if text_col not in df.columns:
        raise ValueError(f"La columna '{text_col}' no existe en {input_csv}. Columnas: {list(df.columns)}")

    preds, scores, terms = [], [], []
    for txt in df[text_col].astype(str):
        doc = nlp_obj(txt)
        label, score, found = collapse_to_AD(doc)
        preds.append(label); scores.append(score); terms.append(found)

    df_out = df.copy()
    df_out["pred_label"] = preds
    df_out["pred_score"] = scores     # proxy simple (recuento de hits válidos)
    df_out["pred_terms"] = terms
    output_csv.parent.mkdir(parents=True, exist_ok=True)
    df_out.to_csv(output_csv, index=False, encoding="utf-8")
    print(f"✅ Guardado: {output_csv}  | filas={len(df_out)}")

if __name__ == "__main__":
    p = argparse.ArgumentParser(description="Baseline A/D - rule-based")
    p.add_argument("--profile", choices=["col","py"], required=True, help="col (original) | py (tus patrones Concept_PY)")
    p.add_argument("--config", default="col_config.yml", help="archivo en configs/ (col_config.yml | py_config.yml)")
    p.add_argument("--input", required=True, help="CSV de entrada")
    p.add_argument("--output", required=True, help="CSV de salida")
    args = p.parse_args()

    run(args.profile, args.config, pathlib.Path(args.input), pathlib.Path(args.output))