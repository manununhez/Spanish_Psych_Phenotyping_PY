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

def run(profile: str, config_name: str, input_csv: pathlib.Path, output_csv: pathlib.Path):
    cfg = load_yaml(BASE / "configs" / config_name)
    fenos_cfg = load_yaml(BASE / "configs" / "fenotipos.yml")
    text_col = cfg["text_column"]

    nlp_obj = build_pipeline(profile, fenos_cfg)

    df = pd.read_csv(input_csv)
    if text_col not in df.columns:
        raise ValueError(f"La columna '{text_col}' no existe en {input_csv}. Columnas: {list(df.columns)}")

    # List of dictionaries to store features for each row
    features_list = []

    print(f"Propagando {len(df)} textos...")
    for txt in df[text_col].astype(str):
        doc = nlp_obj(txt)
        
        # Dictionary for the current row
        row_features = {}
        
        for ent in doc.ents:
            label = ent.label_
            
            # Check negation
            is_negated = getattr(ent._, "is_negated", False)
            
            # Logic:
            # If concept is detected and NOT negated -> 1
            # If concept is detected BUT negated -> 0
            # If concept is NOT detected -> 0 (handled by fillna later)
            
            # We preserve the generic rule: if it appears multiple times, 
            # as long as ONE instance is positive (not negated), we count it as 1.
            # If all instances are negated, it stays 0.
            
            if not is_negated:
                row_features[label] = 1
            else:
                # If it was already set to 1 by a previous instance in the same text, keep it 1.
                # Only set to 0 if it's not currently set.
                if label not in row_features:
                    row_features[label] = 0
        
        features_list.append(row_features)

    # Convert features to DataFrame
    df_features = pd.DataFrame(features_list)
    
    # Fill NaN with 0 (concepts not detected in a row are 0)
    df_features = df_features.fillna(0).astype(int)
    
    # Concatenate with original data
    df_out = pd.concat([df, df_features], axis=1)

    output_csv.parent.mkdir(parents=True, exist_ok=True)
    df_out.to_csv(output_csv, index=False, encoding="utf-8")
    print(f"✅ Guardado: {output_csv} | filas={len(df_out)} | conceptos detectados={len(df_features.columns)}")

if __name__ == "__main__":
    p = argparse.ArgumentParser(description="Baseline A/D - rule-based")
    p.add_argument("--profile", choices=["col","py"], required=True, help="col (original) | py (tus patrones Concept_PY)")
    p.add_argument("--config", default="col_config.yml", help="archivo en configs/ (col_config.yml | py_config.yml)")
    p.add_argument("--input", required=True, help="CSV de entrada")
    p.add_argument("--output", required=True, help="CSV de salida")
    args = p.parse_args()

    run(args.profile, args.config, pathlib.Path(args.input), pathlib.Path(args.output))