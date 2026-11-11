# Spanish Psych Phenotyping PY

Recurso de extracción de menciones psiquiátricas en español, basado en reglas explícitas de spaCy/medspaCy. Conserva una base histórica colombiana, un núcleo depurado y una extensión paraguaya. Se usa como dependencia clínica versionada del pipeline de investigación; **no diagnostica ansiedad o depresión ni entrena un clasificador**.

## Qué es el diccionario
El diccionario es un conjunto de archivos JSON que vinculan expresiones con categorías clínicas. No es una lista de pacientes, etiquetas de referencia ni respuestas de un LLM.

Cada regla contiene:

- `literal`: nombre legible de la expresión o del patrón.
- `category`: categoría técnica emitida al detectar una coincidencia.
- `pattern`: secuencia de condiciones sobre tokens, como `LOWER`, alternativas `IN` o condiciones morfológicas.

Una regla puede cubrir varias variantes y varias reglas pueden emitir la misma categoría. Las carpetas organizan el recurso, pero no convierten una mención en diagnóstico: sueño, fatiga o irritabilidad pueden aparecer en más de un dominio.

Ejemplo real de la capa PY, simplificado a una regla:

```json
{
  "target_rules": [
    {
      "literal": "Bajoneado",
      "category": "Animodeprimido",
      "pattern": [{"LOWER": "bajoneado"}]
    }
  ]
}
```

La coincidencia identifica una mención de `Animodeprimido`; no decide la clase de la nota ni confirma que el fenómeno esté vigente o afirmado.

## Capas y perfiles
| Capa | Papel | Perfil que la carga |
|---|---|---|
| `Concept_CO` | Base histórica colombiana de referencia | `co` |
| `Concept_Core` | Núcleo depurado, con patrones generales y contexto | `core` y `py` |
| `Concept_PY` | Variantes regionales y abreviaturas añadidas al núcleo | `py`, junto con Core |

`co = Concept_CO`; `core = Concept_Core`; `py = Concept_Core + Concept_PY`. PY extiende Core, no lo reemplaza.

Inventario de las capas en la versión 2.0.0 (ver [manifiesto](escribe/patterns/MANIFIESTO_LEXICO.json) y [cambios](CHANGELOG.md)):

| Capa | Archivos JSON | Reglas declaradas | Categorías distintas |
|---|---:|---:|---:|
| CO | 51 | 424 | 46 |
| Core | 55 | 446 | 48 |
| PY, solo extensión | 23 | 51 | 22 |

El perfil compuesto PY carga 497 reglas y reúne 50 categorías distintas. Los conceptos compartidos entre `Ansiedad/` y `Depresion/` (en Core: sueño alterado, insomnio, fatiga, irritabilidad y baja concentración; en PY, además, rumiación) tienen una copia idéntica en cada carpeta; al cargar ambas carpetas sus reglas se repiten, por eso el número de reglas distintas efectivas es menor (co 370, core 395, py 444). No son 497 features ni 497 conceptos independientes: hay categorías compartidas y patrones solapados. Estos conteos excluyen las reglas de ConText y de segmentación.

Detalle por capa: [CO](escribe/patterns/Concept_CO/README.md), [Core](escribe/patterns/Concept_Core/README.md) y [PY](escribe/patterns/Concept_PY/README.md).

## Cómo se formó y qué se puede acreditar
El historial conserva el recurso original `Spanish_Psych_Phenotyping` y su reorganización en capas. CO permite comparar con la referencia histórica; Core incorpora cambios de patrones y organización, una categoría separada de minusvalía y contexto; PY contiene expresiones regionales y sus mapeos a categorías.

Los JSON prueban qué patrones quedaron implementados. El manifiesto PY relaciona términos y variantes con categorías, pero no registra fuente individual, responsable de validación, corpus consultado, fecha de aprobación ni revisión clínica de cada expresión. No demuestra que cada variante sea exclusiva de Paraguay, que Core se obtuviera eliminando únicamente colombianismos ni que la ingeniería inicial fuera independiente del texto posteriormente asignado a prueba.

El proyecto consumidor describe apoyo del LLM para revisión léxica y otra operación distinta de extracción semántica. Este repositorio no contiene un procedimiento LLM reproducible de generación o filtrado de cada término. No debe atribuirse a todos los patrones un mismo prompt, modelo o validación que no estén acreditados. El congelamiento técnico permite reproducir un snapshot, no reconstruye por sí solo esa procedencia.

## Componentes y configuración
`escribe/default_nlp.py` crea el objeto NLP y configura:

1. Modelo español spaCy: intenta `es_core_news_md`; si falta, intenta `es_core_news_sm`.
2. `medspacy_pyrush`: segmentación con [RuSH_ES.tsv](escribe/patterns/RuSH_ES.tsv).
3. `medspacy_target_matcher`: coincidencias con los JSON seleccionados.
4. `medspacy_context`: atributos de aseveración con [ConText_ES.json](escribe/patterns/ConText_ES.json).

ConText debe ejecutarse **después** del matcher. Detectar una expresión y atribuirle negación, temporalidad o sujeto son operaciones distintas.

Los [archivos de configuración](configs/) definen `concept_layers`, `concept_folders` y `patterns_root`. La selección por `concepts` se realiza por carpeta (`Ansiedad`, `Depresion`, `Contexto`), no por nombre de categoría. En `build_pipeline`, el argumento `fenos_cfg` no determina las carpetas efectivas: se leen de la configuración del perfil.

## Entorno
Usar el entorno fijado por el proyecto consumidor y el modelo español correspondiente. Son dependencias directas spaCy, medspaCy, pandas y PyYAML; medspaCy aporta también la segmentación utilizada. Este snapshot no dispone de un instalador de paquete ni de un lockfile propio: no presentar `pip install .` como una instalación soportada.

El import de `escribe.default_nlp` carga el modelo y configura componentes, pero no carga automáticamente todas las reglas Core. No hay llamadas a un LLM en esta extracción local. Registrar versiones y modelo efectivo: el fallback a `sm` puede cambiar el comportamiento.

## Ejemplo ejecutable desde Python
Ejecutar desde la raíz de este repositorio, con sus dependencias instaladas. El texto siguiente es sintético. La vía recomendada es `build_pipeline`, que crea un objeto propio por perfil:

```python
from cli import build_pipeline

core = build_pipeline("core")   # objeto nuevo
py = build_pipeline("py")       # otro objeto: no modifica core
doc = py("Paciente bajoneado. Niega ansiedad.")
for entity in doc.ents:
    print(entity.text, entity.label_, entity._.is_negated)
```

También se puede cargar por capas con `select_concepts` sobre un objeto creado con `make_nlp()`:

```python
from pathlib import Path
from escribe.default_nlp import make_nlp, select_concepts

patterns = Path("escribe/patterns")
folders = ("Ansiedad", "Depresion", "Contexto")

pipeline = select_concepts(
    make_nlp(), json_dir=str(patterns / "Concept_Core"),
    concepts=folders, reset=True,
)
pipeline = select_concepts(
    pipeline, json_dir=str(patterns / "Concept_PY"),
    concepts=folders, reset=False,
)

assert pipeline.pipe_names.index("medspacy_target_matcher") < (
    pipeline.pipe_names.index("medspacy_context")
)
doc = pipeline("Paciente bajoneado. Niega ansiedad.")
for entity in doc.ents:
    print(entity.text, entity.label_, entity._.is_negated)
```

Con el entorno comprobado, detecta `bajoneado -> Animodeprimido` sin negación y `ansiedad -> Ansiedad` con negación. Para Core, omitir la segunda carga; para CO, cargar únicamente `Concept_CO` con `reset=True`.

**Objetos por perfil (desde 2.0.0):** `make_nlp()` y `build_pipeline()` crean un objeto nuevo en cada llamada, de modo que construir un perfil no modifica otro. El objeto global `escribe.default_nlp.nlp` se conserva por compatibilidad: `select_concepts` sobre ese objeto sigue modificándolo, igual que antes.

## Estado de cli.py y orden de ConText
[cli.py](cli.py) expone funciones Python como `build_pipeline` y `load_concept_layer`. Aunque importa `argparse`, no implementa un punto de entrada para exportar CSV: los comandos `python cli.py --profile ... --input ... --output ...` no son una interfaz funcional.

**Corregido en 2.0.0.** Hasta el commit `916c1d9`, `build_pipeline` quitaba el matcher y lo volvía a añadir al final, detrás de ConText: `Niega ansiedad` quedaba con `is_negated=False`. Ahora el detector conserva su posición antes de ConText y `check_order()` hace fallar cualquier pipeline con el orden invertido. Las etiquetas detectadas no cambian; sí cambian los atributos de contexto (negación, antecedente, familiar). Ver el impacto medido en [CHANGELOG.md](CHANGELOG.md).

Los resultados históricos del proyecto consumidor generados con la versión anterior conservan su evidencia; recalcularlos con 2.0.0 cambia las columnas que dependen de ConText. Los cargadores pueden omitir reglas inválidas: las pruebas verifican que las reglas cargadas sean exactamente las declaradas.

## Versión, manifiesto y pruebas
- `escribe/patterns/MANIFIESTO_LEXICO.json`: versión del léxico, SHA-256 de cada JSON, conteos por capa/carpeta/perfil y hashes de ConText, RuSH y configuraciones. Se congela **antes** de procesar datos nuevos; cambiar una regla exige versión y manifiesto nuevos.
- `python tools/manifiesto_lexico.py verificar` compara los archivos con el manifiesto; `inventario` imprime el informe de cobertura del recurso (capas, carpetas, reglas por categoría). No procesa textos.
- `python -m unittest discover -s tests -v` (o `python -m pytest tests -q`): orden, independencia de perfiles, reglas cargadas = declaradas, regresión de ConText con frases sintéticas, determinismo entre APIs, unicidad, sincronía de conceptos compartidos y manifiesto. Requieren el modelo spaCy español.

## Medicación: procedencia y alcance
`medication_anxiety` y `medication_depression` (Core, y su copia histórica en CO) son un componente diseñado a partir del trabajo de Ruiz Olazar et al. (2026, *Monitoring Therapeutic Plans and Risk Signals from Clinical Narratives in Mental Health*, FLAIRS 39), que extrajo el plan terapéutico de notas de pacientes con depresión del mismo entorno; el proyecto consumidor lo extendió a ansiedad.

Las listas reflejan lo que se prescribe a cada población clínica, no una indicación farmacológica exclusiva: el solapamiento (ISRS, IRSN, benzodiacepinas) es esperable por comorbilidad, y los antipsicóticos y estabilizadores de la lista de depresión reflejan esquemas reales (síntomas psicóticos, potenciación, bipolaridad). Una coincidencia de medicación es evidencia terapéutica, no diagnóstico ni síntoma. Queda propuesto, sin aplicar, un mapa complementario fármaco → clase farmacológica (ATC) que no reemplace estas listas.

## Integración y límites
El subrepositorio aporta menciones y contexto. El proyecto consumidor implementa la elegibilidad de notas, la atribución de negación al paciente, las columnas `rule_*`/`niega_*`, el split, modelos y evaluación.

La unión sintomática `feat_X = max(rule_X, llm_X)` se realiza fuera de este recurso. Los medicamentos siguen como evidencia terapéutica separada; ni una prescripción ni una coincidencia léxica acreditan diagnóstico. Más cobertura no demuestra mayor exactitud clínica, mejora predictiva ni aporte causal de PY. La revisión clínica formal del recurso y del filtro no debe inferirse de los JSON o del manifiesto.

## Reproducibilidad y licencia
Conservar el commit del recurso, la versión del manifiesto, hashes de JSON/configuración, entorno, modelo spaCy, perfiles, carpetas y orden de componentes. Comprobar extracción y contexto con ejemplos sintéticos antes de procesar datos autorizados. Cambiar patrones, categorías o carga requiere nueva trazabilidad; no sobrescribir la evidencia del experimento congelado.

Los cambios del subrepositorio requieren su propio commit. Después, el proyecto consumidor debe actualizar el puntero del submódulo; publicar solo ese puntero sin el commit accesible impide reproducir el cambio.

Licencia [MIT](LICENSE), con atribución original a `clarafrydman` (2024). La licencia del código no autoriza distribuir notas clínicas. No incorporar datos de pacientes, credenciales ni salidas individuales a este repositorio.
