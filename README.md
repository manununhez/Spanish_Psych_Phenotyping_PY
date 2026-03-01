# Spanish Psych Phenotyping — LATAM (CO baseline + PY adaptation)

Este fork está basado en el proyecto original **Spanish_Psych_Phenotyping** (DeLaHoz2015),
pero se reorganiza para soportar una arquitectura **Core + Adaptation Layers** enfocada en
**fenotipado psiquiátrico en EHR en español**.

La motivación práctica (IPS/Paraguay) es que muchas notas clínicas combinan:

- *Narrativa clínica* (síntomas / evolución / plan)
- *Plantillas administrativas* (formularios repetitivos) que generan falsos positivos

Este repositorio no “reemplaza” el baseline publicado: lo **congela**, y permite medir
cuánto mejora una adaptación local.

## Arquitectura por capas

### 1) `Concept_CO/` — baseline (paper, Colombia)
Conjunto congelado para reproducir el fenotipado publicado.

### 2) `Concept_PY/` — core reproducible (IPS)
Core estable para EHR en español con **fixes generales** (anclajes, correcciones técnicas,
reducción de falsos positivos por estructura), pero sin depender de léxico cultural local.

> Nota: si movés los términos paraguayos a `Concept_PY_Lexicon/`, el core puede quedar **muy
> parecido** al baseline, pero **no necesariamente idéntico**: es válido que el core contenga
> correcciones técnicas y mejoras generalizables (p. ej. fixes `label→literal`, anclajes, ajustes
> de ventanas) mientras que el léxico local quede en la capa de adaptación.

### 3) `Concept_PY_Lexicon/` — adaptation layer (Paraguay)
Extensión opcional con **léxico paraguayo/jopará**, abreviaturas institucionales y variantes
locales. Se carga **encima del core** (sin reset del matcher) para poder comparar:

- baseline (`co`) vs core (`core`) vs core+adaptación (`py`).

Para evitar “contexto no clínico”, esta capa debe usar **anclaje clínico** (p. ej. “refiere/niega/presenta”)
(y/o ejecutarse sobre secciones narrativas), y debe correrse sobre texto normalizado.

## Normalización de texto (data cleaning, no decisión clínica)

En IPS es común que la nota incluya secciones de formulario repetitivas (2–8). Para reducir
falsos positivos en extracción basada en reglas:

> “Identificamos y eliminamos segmentos de formulario repetitivos (secciones 2–8) que no
> aportan fenomenología psiquiátrica y generan falsos positivos en extracción basada en reglas.”

Esto es normalización de formato de nota (muy común en EHR) y debe ocurrir **antes** del extractor.

## Estructura de directorios

```
escribe/patterns/
├─ Concept_CO/            # baseline (paper)
├─ Concept_PY/            # core reproducible
├─ Concept_PY_Lexicon/    # capa paraguaya (opcional)
├─ ConText_ES.json
└─ RuSH_ES.tsv

configs/
├─ fenotipos.yml          # lista de conceptos (carpetas) a activar
├─ co_config.yml
├─ core_config.yml
└─ py_config.yml

cli.py
```

## Uso (CLI)

Perfiles:

- `co`   → baseline Colombia (`Concept_CO/`)
- `core` → core reproducible (`Concept_PY/`)
- `py`   → core + adaptación (`Concept_PY/` + `Concept_PY_Lexicon/`)

```bash
python cli.py --profile co   --config co_config.yml   --input data/ips_clean.csv --output outputs/rules_co.csv
python cli.py --profile core --config core_config.yml --input data/ips_clean.csv --output outputs/rules_core.csv
python cli.py --profile py   --config py_config.yml   --input data/ips_clean.csv --output outputs/rules_py.csv
```

## Uso (Python / notebooks)

```python
from pathlib import Path
from escribe.default_nlp import nlp, select_concepts

BASE = Path("escribe/patterns")

# Baseline (CO)
nlp_co = select_concepts(nlp, json_dir=str(BASE / "Concept_CO"), concepts=("all",), reset=True)

# Core (PY)
nlp_core = select_concepts(nlp, json_dir=str(BASE / "Concept_PY"), concepts=("all",), reset=True)

# Core + Adaptación (PY)
nlp_py = select_concepts(nlp, json_dir=str(BASE / "Concept_PY"), concepts=("all",), reset=True)
nlp_py = select_concepts(nlp_py, json_dir=str(BASE / "Concept_PY_Lexicon"), concepts=("all",), reset=False)
```

## Configuración

- `configs/fenotipos.yml` define qué carpetas cargar (por defecto: Ansiedad, Depresion, Contexto).
- `configs/*_config.yml` define la columna de texto (`text_column`) y nombres de proyecto.

