
#!/usr/bin/env python3
# ===============================================================
# CLI — Psych Phenotyping (A/D)
# ===============================================================
import argparse
import pathlib
import yaml
import pandas as pd
import json
from pathlib import Path

from escribe.default_nlp import nlp  # pipeline base (medSpaCy + ConText + TM)
from medspacy import ner

BASE = pathlib.Path(__file__).parent


def load_yaml(path: pathlib.Path) -> dict:
    with open(path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def _iter_json_files(root: Path):
    # root puede no existir
    if not root.exists():
        return
    for p in root.rglob("*.json"):
        if p.name.startswith("."):
            continue
        yield p


def _as_language(nlp_obj):
    if hasattr(nlp_obj, "get_pipe") and hasattr(nlp_obj, "pipe_names"):
        return nlp_obj
    if hasattr(nlp_obj, "nlp") and hasattr(nlp_obj.nlp, "get_pipe") and hasattr(nlp_obj.nlp, "pipe_names"):
        return nlp_obj.nlp
    raise TypeError(f"Se esperaba spaCy Language, pero llegó: {type(nlp_obj)}")


def _get_target_matcher(nlp_obj):
    nlp_lang = _as_language(nlp_obj)
    return nlp_lang.get_pipe("medspacy_target_matcher")


def _reset_target_matcher(nlp_obj):
    nlp_lang = _as_language(nlp_obj)
    if "medspacy_target_matcher" in nlp_lang.pipe_names:
        nlp_lang.remove_pipe("medspacy_target_matcher")
    nlp_lang.add_pipe("medspacy_target_matcher")
    return nlp_lang


def load_concept_layer(
    nlp_obj,
    base_dir: Path,
    concepts=("all",),
    reset: bool = True,
    verbose: bool = True,
):
    base_dir = Path(base_dir)

    # Auto-fix: si quedó anidada como Concept_PY_Lexicon/Concept_PY_Lexicon/...
    nested = base_dir / base_dir.name
    if not any(_iter_json_files(base_dir)) and nested.exists():
        if verbose:
            print(
                f"[load_concept_layer] Aviso: no hay JSON directos en {base_dir}. "
                f"Detecté carpeta anidada, usando {nested}"
            )
        base_dir = nested

    # Reset matcher solo en la 1ra capa
    if reset:
        nlp_obj = _reset_target_matcher(nlp_obj)

    tm = _get_target_matcher(nlp_obj)

    # Armar lista de json_paths
    json_paths = []
    if concepts and (len(concepts) == 1 and concepts[0] == "all"):
        json_paths = list(_iter_json_files(base_dir))
    else:
        wanted = [str(c).strip() for c in concepts]
        for c in wanted:
            sub = base_dir / c
            files = list(_iter_json_files(sub))
            if files:
                json_paths.extend(files)
            else:
                if verbose:
                    print(f"[load_concept_layer] Aviso: no hay JSON en {sub}")

    if verbose:
        folder_list = ", ".join(concepts) if concepts and concepts != ("all",) else "all"
        print(f"[load_concept_layer] Base: {base_dir} | concepts: {folder_list} | json_files={len(json_paths)}")
        if len(json_paths) > 0:
            print(f"[load_concept_layer] Ejemplo JSON: {json_paths[0].name}")

    # Diagnóstico duro si no hay json
    if verbose and len(json_paths) == 0:
        try:
            subdirs = [p.name for p in base_dir.iterdir() if p.is_dir()]
            files = [p.name for p in base_dir.iterdir() if p.is_file()]
            print(f"[load_concept_layer][DIAG] base_dir subdirs={subdirs}")
            print(f"[load_concept_layer][DIAG] base_dir files={files}")
            for c in (concepts if concepts else []):
                sub = base_dir / str(c).strip()
                if sub.exists():
                    sfiles = [p.name for p in sub.iterdir() if p.is_file()]
                    print(f"[load_concept_layer][DIAG] {sub} files={sfiles[:10]}")
        except Exception as _e:
            print(f"[load_concept_layer][DIAG] no pude listar {base_dir}: {_e}")
        raise ValueError(
            f"No se encontraron JSON en {base_dir} para concepts={concepts}. "
            f"Revisar estructura/copia del Lexicon."
        )

    total_added = 0
    cats_seen = set()

    # Cargar reglas desde cada json
    for fp in json_paths:
        try:
            with open(fp, "r", encoding="utf-8") as f:
                obj = json.load(f)
        except Exception as e:
            if verbose:
                print(f"[load_concept_layer][ERROR] no se pudo leer {fp}: {e}")
            continue

        rules = []
        if isinstance(obj, dict) and isinstance(obj.get("target_rules", None), list):
            rules = obj["target_rules"]
        elif isinstance(obj, list):
            rules = obj
        elif isinstance(obj, dict):
            # fallback: alguna key tiene la lista
            for v in obj.values():
                if isinstance(v, list) and v and isinstance(v[0], dict):
                    rules.extend(v)

        if not rules:
            if verbose:
                print(f"[load_concept_layer] {fp.name}: 0 reglas (formato no reconocido)")
            continue

        for r in rules:
            if not isinstance(r, dict) or "category" not in r:
                continue

            # ---- FIX LEXICON: permitir campos extra como 'source' ----
            r = dict(r)  # copia
            src = r.pop("source", None)
            if src is not None:
                md = r.get("metadata") or {}
                if not isinstance(md, dict):
                    md = {}
                md["source"] = src
                r["metadata"] = md
            # ---------------------------------------------------------

            try:
                tr = ner.TargetRule.from_dict(r)
                tm.add(tr)
                cats_seen.add(tr.category)
                total_added += 1
            except Exception as e:
                if verbose:
                    print(f"[load_concept_layer][ERROR] from_dict falló en {fp.name}: {e}")
                continue

    if verbose:
        cats_str = ", ".join(sorted(cats_seen))
        print(f"[load_concept_layer] Rule categories loaded: {cats_str}")
        print(f"[load_concept_layer] Total target rules added: {total_added}")

    return nlp_obj


def build_pipeline(profile: str, fenos_cfg: dict, profile_cfg: dict | None = None):
    if profile_cfg is None:
        p = BASE / "configs" / f"{profile}_config.yml"
        profile_cfg = load_yaml(p)

    patterns_root = Path(profile_cfg.get("patterns_root", "escribe/patterns"))
    patterns_root = (BASE / patterns_root).resolve()

    layers = profile_cfg.get("concept_layers", [])
    if not layers:
        raise ValueError(f"El perfil '{profile}' no define concept_layers")

    concepts = tuple(profile_cfg.get("concept_folders", ("all",)))

    nlp_obj = nlp  # pipeline base singleton

    reset = True
    for layer_name in layers:
        layer_dir = patterns_root / layer_name
        if not layer_dir.exists():
            raise FileNotFoundError(f"No existe capa '{layer_name}' en {layer_dir}")
        nlp_obj = load_concept_layer(
            nlp_obj,
            base_dir=layer_dir,
            concepts=concepts,
            reset=reset,
            verbose=True,
        )
        reset = False

    return nlp_obj
