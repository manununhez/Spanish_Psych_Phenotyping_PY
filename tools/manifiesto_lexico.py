#!/usr/bin/env python3
"""Manifiesto versionado del léxico: hashes, conteos e inventario de cobertura.

Uso (desde la raíz del repositorio):
    python tools/manifiesto_lexico.py verificar    # compara los archivos con el manifiesto congelado
    python tools/manifiesto_lexico.py inventario   # informe de cobertura por capa, carpeta y categoría
    python tools/manifiesto_lexico.py generar --version X.Y.Z --fecha AAAA-MM-DD   # solo al publicar una versión

No procesa textos clínicos. El manifiesto describe el recurso, no su uso en un corpus.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PATTERNS = ROOT / "escribe" / "patterns"
MANIFEST = PATTERNS / "MANIFIESTO_LEXICO.json"
LAYERS = ("Concept_CO", "Concept_Core", "Concept_PY")
PROFILES = {"co": ("Concept_CO",), "core": ("Concept_Core",), "py": ("Concept_Core", "Concept_PY")}
FOLDERS = ("Ansiedad", "Depresion", "Contexto")
AUX = ("ConText_ES.json", "RuSH_ES.tsv")


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def rules_of(path: Path) -> list[dict]:
    obj = json.loads(path.read_text(encoding="utf-8"))
    return obj.get("target_rules", []) if isinstance(obj, dict) else obj


def rule_key(rule: dict) -> str:
    """Firma de una regla: categoría + patrón (o literal en minúsculas si no hay patrón)."""
    pat = rule.get("pattern")
    body = json.dumps(pat, sort_keys=True, ensure_ascii=False) if pat else "LIT:" + str(rule.get("literal", "")).lower()
    return f"{rule.get('category')}|{body}"


def json_files(layer: str, folders=FOLDERS):
    for folder in folders:
        d = PATTERNS / layer / folder
        if d.exists():
            for p in sorted(d.glob("*.json")):
                if not p.name.startswith("."):
                    yield folder, p


def describe() -> dict:
    files, layers = {}, {}
    for layer in LAYERS:
        carpetas, cats = {}, set()
        for folder, p in json_files(layer):
            rs = rules_of(p)
            rel = p.relative_to(PATTERNS).as_posix()
            files[rel] = {"sha256": sha256(p), "reglas": len(rs)}
            c = carpetas.setdefault(folder, {"archivos": 0, "reglas": 0})
            c["archivos"] += 1
            c["reglas"] += len(rs)
            cats |= {r.get("category") for r in rs}
        layers[layer] = {"archivos": sum(v["archivos"] for v in carpetas.values()),
                         "reglas": sum(v["reglas"] for v in carpetas.values()),
                         "categorias": len(cats), "carpetas": carpetas}
    profiles = {}
    for prof, ls in PROFILES.items():
        cats = set()
        for layer in ls:
            for _, p in json_files(layer):
                cats |= {r.get("category") for r in rules_of(p)}
        profiles[prof] = {"capas": list(ls), "reglas_declaradas": sum(layers[l]["reglas"] for l in ls), "categorias": len(cats)}
    aux = {name: sha256(PATTERNS / name) for name in AUX}
    for cfg in sorted((ROOT / "configs").glob("*.yml")):
        aux[f"configs/{cfg.name}"] = sha256(cfg)
    return {"capas": layers, "perfiles": profiles, "archivos": files, "auxiliares_sha256": aux}


def generar(version: str, fecha: str, base: str | None) -> None:
    doc = {"version": version, "fecha": fecha, "commit_base": base, **describe(),
           "nota": "Congelado antes de procesar datos nuevos. Cambiar una regla exige nueva versión y nuevo manifiesto."}
    MANIFEST.write_text(json.dumps(doc, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"Manifiesto {version} escrito en {MANIFEST.relative_to(ROOT)}")


def verificar() -> list[str]:
    if not MANIFEST.exists():
        return ["Falta escribe/patterns/MANIFIESTO_LEXICO.json"]
    frozen = json.loads(MANIFEST.read_text(encoding="utf-8"))
    now = describe()
    errs = []
    a, b = frozen["archivos"], now["archivos"]
    for k in sorted(set(a) | set(b)):
        if k not in b:
            errs.append(f"falta archivo: {k}")
        elif k not in a:
            errs.append(f"archivo no registrado: {k}")
        elif a[k]["sha256"] != b[k]["sha256"]:
            errs.append(f"hash distinto: {k}")
    for k, h in frozen["auxiliares_sha256"].items():
        if now["auxiliares_sha256"].get(k) != h:
            errs.append(f"hash distinto: {k}")
    return errs


def inventario() -> None:
    d = describe()
    print("Capa | archivos | reglas | categorías")
    for layer, v in d["capas"].items():
        print(f"{layer} | {v['archivos']} | {v['reglas']} | {v['categorias']}")
        for folder, c in v["carpetas"].items():
            print(f"  {folder}: {c['archivos']} archivos, {c['reglas']} reglas")
    print("\nPerfil | reglas declaradas | categorías")
    for prof, v in d["perfiles"].items():
        print(f"{prof} ({' + '.join(v['capas'])}) | {v['reglas_declaradas']} | {v['categorias']}")
    print("\nReglas por categoría (perfil py):")
    cnt = Counter()
    for layer in PROFILES["py"]:
        for _, p in json_files(layer):
            cnt.update(r.get("category") for r in rules_of(p))
    for cat, n in sorted(cnt.items()):
        print(f"  {cat}: {n}")


def duplicados(layer: str) -> dict:
    """(carpeta, firma) repetida dentro de una capa → lista de archivo#índice."""
    seen = defaultdict(list)
    for folder, p in json_files(layer):
        for i, r in enumerate(rules_of(p)):
            seen[(folder, rule_key(r))].append(f"{p.name}#{i}")
    return {k: v for k, v in seen.items() if len(v) > 1}


def compartidos_desincronizados(layer: str) -> list[str]:
    """Conceptos con el mismo archivo en Ansiedad/ y Depresion/ cuyo contenido difiere."""
    a, d = PATTERNS / layer / "Ansiedad", PATTERNS / layer / "Depresion"
    if not (a.exists() and d.exists()):
        return []
    out = []
    for p in sorted(a.glob("*.json")):
        q = d / p.name
        if q.exists() and sorted(map(rule_key, rules_of(p))) != sorted(map(rule_key, rules_of(q))):
            out.append(p.name)
    return out


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    g = sub.add_parser("generar")
    g.add_argument("--version", required=True)
    g.add_argument("--fecha", required=True)
    g.add_argument("--base", default=None, help="commit del que parte la versión")
    sub.add_parser("verificar")
    sub.add_parser("inventario")
    args = ap.parse_args(argv)
    if args.cmd == "generar":
        generar(args.version, args.fecha, args.base)
    elif args.cmd == "verificar":
        errs = verificar()
        for e in errs:
            print("ERROR:", e)
        print("Manifiesto OK" if not errs else f"{len(errs)} diferencias")
        return 1 if errs else 0
    else:
        inventario()
    return 0


if __name__ == "__main__":
    sys.exit(main())
