# Spanish Psych Phenotyping — LATAM (`Concept_CO` + `Concept_Core` + `Concept_PY`)

Este submódulo versiona el recurso clínico rule-based que usa el proyecto principal para extraer fenotipos psiquiátricos sobre texto clínico en español.

Su punto de partida es el baseline histórico de `Spanish_Psych_Phenotyping` para Colombia, pero el snapshot actual reorganiza ese recurso en una arquitectura por capas para separar:

- baseline histórico reproducible;
- núcleo clínico depurado y portable;
- adaptación regional paraguaya.

## Rol dentro del proyecto principal

En el repositorio principal este submódulo se usa como dependencia clínica reproducible para:

- denoising clínico en `03_denoising_reglas_core.ipynb`;
- extracción de evidencia simbólica `rule_*` y `niega_*`;
- evidencia terapéutica separada `rule_medication_*`;
- comparación de perfiles `co`, `core` y `py`;
- trazabilidad de la ontología clínica congelada.

No debe leerse solo como un clasificador rule-based autónomo. Su función principal en este proyecto es servir como base clínica versionada para el pipeline híbrido.

## Arquitectura por capas

La nomenclatura activa del proyecto principal es:

- `Concept_CO` = baseline histórico colombiano congelado;
- `Concept_Core` = núcleo clínico depurado y portable;
- `Concept_PY` = capa regional paraguaya.

### `Concept_CO/`
Perfil histórico de referencia. Se conserva para comparación y trazabilidad.

### `Concept_Core/`
Núcleo clínico depurado con correcciones generales, mejor control de ruido estructural y organización estable por carpetas clínicas.

### `Concept_PY/`
Capa opcional de adaptación paraguaya que se carga encima del core. Amplía cobertura léxica regional y puede añadir algunas categorías auxiliares de contexto, pero no redefine la tarea supervisada principal del proyecto.

## Estructura del recurso

```text
escribe/patterns/
├─ Concept_CO/
├─ Concept_Core/
├─ Concept_PY/
├─ ConText_ES.json
└─ RuSH_ES.tsv

configs/
├─ fenotipos.yml
├─ co_config.yml
├─ core_config.yml
└─ py_config.yml

cli.py
```

Folders clínicos activos:

- `Ansiedad/`
- `Depresion/`
- `Contexto/`

## Qué representa cada archivo JSON

Cada archivo `.json` contiene una o más `TargetRule` de medSpaCy.

Campos relevantes:

- `category`: categoría emitida por la regla y usada downstream para construir columnas `rule_<category>`;
- `literal`: etiqueta humana auxiliar del archivo o de la evidencia específica;
- `pattern`: patrón tokenizado o literal a detectar.

Regla práctica:

- en `Ansiedad/` y `Depresion/`, el nombre del archivo suele coincidir con la categoría emitida;
- en `Contexto/`, varios archivos del core emiten la categoría común `Contexto` y usan `literal` para distinguir subtipos como `Alcohol`, `UsoSustancias` o `Agresividad`;
- las reglas de medicación emiten categorías separadas como `medication_anxiety` y `medication_depression`.

## Perfiles operativos

La carga estándar usa estos perfiles:

- `co`   -> `Concept_CO`
- `core` -> `Concept_Core`
- `py`   -> `Concept_Core` + `Concept_PY`

El perfil `py` no reemplaza al core: lo extiende.

## Uso con CLI

```bash
python cli.py --profile co   --config co_config.yml   --input data/ips_clean.csv --output outputs/rules_co.csv
python cli.py --profile core --config core_config.yml --input data/ips_clean.csv --output outputs/rules_core.csv
python cli.py --profile py   --config py_config.yml   --input data/ips_clean.csv --output outputs/rules_py.csv
```

## Uso desde Python

```python
from pathlib import Path
from escribe.default_nlp import nlp, select_concepts

BASE = Path("escribe/patterns")

nlp_co = select_concepts(nlp, json_dir=str(BASE / "Concept_CO"), concepts=("all",), reset=True)
nlp_core = select_concepts(nlp, json_dir=str(BASE / "Concept_Core"), concepts=("all",), reset=True)

nlp_py = select_concepts(nlp, json_dir=str(BASE / "Concept_Core"), concepts=("all",), reset=True)
nlp_py = select_concepts(nlp_py, json_dir=str(BASE / "Concept_PY"), concepts=("all",), reset=False)
```

## Configuración

Archivos principales:

- `configs/fenotipos.yml`: folders conceptuales activos.
- `configs/co_config.yml`: perfil `co`.
- `configs/core_config.yml`: perfil `core`.
- `configs/py_config.yml`: perfil `py`.

La carga por capas la resuelve `cli.py`:

- la primera capa resetea el `target_matcher`;
- las siguientes se cargan encima sin reset.

## Lectura recomendada

Para entender el detalle clínico del snapshot actual, revisar además:

- `escribe/patterns/Concept_CO/README.md`
- `escribe/patterns/Concept_Core/README.md`
- `escribe/patterns/Concept_PY/README.md`

## Alcance y límites

Este submódulo define extracción clínica rule-based. No define por sí solo:

- el `patient-level split`;
- la selección del backbone contextual;
- la fusión tardía con LLM;
- el cierre formal del mejor híbrido.

Esas decisiones pertenecen al repositorio principal.
