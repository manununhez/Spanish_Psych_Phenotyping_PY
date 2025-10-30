# escribe/default_nlp.py
import os
from pathlib import Path
import pandas as pd
from medspacy import load as ms_load, ner

# --- Rutas base relativas a este archivo ---
HERE = Path(__file__).resolve().parent
PATTERNS_DIR_DEFAULT = HERE / "patterns" / "Concept"          # <-- tu filtro A/D/Sueno
RUSH_RULES = HERE / "patterns" / "RuSH_ES.tsv"
CONTEXT_RULES = HERE / "patterns" / "ConText_ES.json"

# --- Carga spaCy/medspaCy con fallback de modelo ---
try:
    nlp = ms_load(
        "es_core_news_md",
        enable=["tok2vec", "morphologizer", "attribute_ruler", "lemmatizer"]
    )
except OSError:
    # Fallback si el modelo md no está instalado
    nlp = ms_load(
        "es_core_news_sm",
        enable=["tok2vec", "morphologizer", "attribute_ruler", "lemmatizer"]
    )

# --- Reemplazar componentes con reglas españolas ---
sentencizer = nlp.replace_pipe(
    "medspacy_pyrush",
    "medspacy_pyrush",
    config={"rules_path": str(RUSH_RULES)}
)
target_matcher = nlp.replace_pipe(
    "medspacy_target_matcher",
    "medspacy_target_matcher",
    config={"rules": None}
)
context = nlp.replace_pipe(
    "medspacy_context",
    "medspacy_context",
    config={"rules": str(CONTEXT_RULES)}
)

print("Components in NLP pipeline:")
for p in nlp.pipe_names:
    print("\t-", p)

def _iter_json_files(root: Path):
    """Recorre recursivamente y devuelve todos los .json válidos (evita ._ y ocultos)."""
    for p in root.rglob("*.json"):
        name = p.name
        if name.startswith("._"):
            continue
        yield p

def _load_target_rules_from_dir(json_dir: Path) -> pd.DataFrame:
    """
    Lee todos los .json que tengan 'target_rules' y devuelve un DataFrame:
      index = category, col 'target_rules' = objetos TargetRule.
    Ignora archivos que no tengan esa clave.
    """
    json_dir = Path(json_dir)
    all_rules = []
    for fp in _iter_json_files(json_dir):
        try:
            j = pd.read_json(fp)
        except ValueError:
            # algunos pueden no ser tablas; intentar con orient='records'
            try:
                j = pd.read_json(fp, orient="records", typ="frame")
            except Exception:
                continue
        # aceptar tanto 'target_rules' plano como presente en alguna columna
        if "target_rules" in j.columns:
            rules = j["target_rules"].tolist()
        else:
            # si la estructura es irregular, intentar extraer listas/dicts que contengan 'pattern' y 'category'
            rules = []
            for col in j.columns:
                try:
                    vals = j[col].tolist()
                except Exception:
                    vals = []
                for v in vals:
                    if isinstance(v, dict) and ("pattern" in v or "literal" in v) and "category" in v:
                        rules.append(v)
        if not rules:
            continue
        # convertir a TargetRule
        tr_objs = []
        for r in rules:
            try:
                tr_objs.append(ner.TargetRule.from_dict(r))
            except Exception:
                # regla inválida, se omite
                pass
        if tr_objs:
            # inferir categoría desde los objetos (se usa dentro de select_concepts)
            for tr in tr_objs:
                all_rules.append({"category": tr.category, "target_rules": tr})
    if not all_rules:
        return pd.DataFrame(columns=["target_rules"]).set_index(pd.Index([], name="category"))
    df = pd.DataFrame(all_rules)
    df = df.set_index("category").sort_index()
    return df

def select_concepts(nlp_obj, json_dir=None, concepts=("all",), verbose=True):
    """
    Carga reglas del target_matcher seleccionando por CARPETA (p.ej. Ansiedad/ Depresion/ Sueno),
    no por el campo 'category' de cada regla.

    - Si concepts=('all',), carga recursivamente TODOS los .json de json_dir.
    - Si concepts=('Ansiedad','Depresion',...), carga SOLO los .json ubicados en esas subcarpetas.
    """
    base_dir = Path(json_dir) if json_dir else PATTERNS_DIR_DEFAULT

    # reset del target matcher
    tm = nlp_obj.replace_pipe("medspacy_target_matcher", "medspacy_target_matcher", config={"rules": None})

    # 1) Armar lista de archivos a cargar según carpeta
    json_paths = []
    if concepts and (len(concepts) == 1 and concepts[0] == "all"):
        json_paths = list(_iter_json_files(base_dir))
    else:
        wanted = {str(c).strip() for c in concepts}
        for c in wanted:
            sub = base_dir / c
            if sub.exists():
                json_paths.extend(list(_iter_json_files(sub)))
            else:
                # si la subcarpeta no existe, no fallamos: avisamos
                if verbose:
                    print(f"[select_concepts] Aviso: no existe carpeta {sub}")

    # 2) Cargar reglas de esos archivos (sin filtrar por 'category')
    #    Reutilizamos el loader por conveniencia, pero lo llamamos por archivo
    total_added = 0
    cats_seen = set()
    for fp in json_paths:
        try:
            j = pd.read_json(fp)
        except ValueError:
            try:
                j = pd.read_json(fp, orient="records", typ="frame")
            except Exception:
                continue

        # localizar reglas tipo dict con 'category' y 'pattern'/'literal'
        rules = []
        if "target_rules" in j.columns:
            rules = j["target_rules"].tolist()
        else:
            for col in j.columns:
                try:
                    vals = j[col].tolist()
                except Exception:
                    vals = []
                for v in vals:
                    if isinstance(v, dict) and ("category" in v) and ("pattern" in v or "literal" in v):
                        rules.append(v)

        for r in rules:
            try:
                tr = ner.TargetRule.from_dict(r)
                tm.add(tr)
                cats_seen.add(tr.category)
                total_added += 1
            except Exception:
                pass

    if verbose:
        print("Concepts included (by folder):", ", ".join(concepts if concepts else ["(default)"]))
        if cats_seen:
            print("Rule categories loaded:", ", ".join(sorted(cats_seen)))
        print(f"Total target rules added: {total_added}")

    return nlp_obj

