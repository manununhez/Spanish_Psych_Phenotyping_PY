# Concept_PY_Lexicon

Capa de **adaptación léxica paraguaya** (Paraguay-first) para el fenotipado psiquiátrico en EHR en español.

## Qué contiene
- Reglas **léxicas** (variantes paraguayas / jopará / abreviaturas locales) derivadas del
  **Diccionario Maestro Psiquiátrico Paraguayo** como fuente principal, y el diccionario fenotipado como complemento
  (para verificación y deduplicación).
- Cada entrada se mapea a un **fenotipo canónico ya existente en el CORE** (mismos nombres `rule_*`).
- La carpeta **Mixto fue eliminada**: todos los términos quedaron asignados a las carpetas del CORE
  (`Ansiedad/`, `Depresion/`, `Contexto/`) para que se carguen sin cambiar `fenotipos.yml`.

## Estructura
- `Ansiedad/` y `Depresion/`: términos que aportan directamente a los fenotipos clínicos.
- `Contexto/`: marcadores de contexto (p.ej., sustancias) o categorías auxiliares. Si no querés estas features,
  podés excluir columnas `rule_*` correspondientes en 07.

## Cómo se usa
- Se carga **junto al CORE** (profile `py`): `CORE + Concept_PY_Lexicon`.
- Recomendación metodológica:
  1) Activar primero **en 09 (auditoría)** para inspeccionar `phenotype_support.csv` y `samples_by_phenotype/`.
  2) Activar luego en **07 (features)**.
  3) Mantener **03 (denoising)** con CORE hasta validar que no introduce ruido.

## Manifiesto
`lexicon_manifest.csv` contiene el mapeo:
- `term_original`: forma original en el diccionario
- `variant`: variante generada/normalizada
- `fenotipo_canonico`: etiqueta humana del fenotipo
- `categoria_core`: nombre exacto del fenotipo (columna `rule_<categoria_core>`)
- `carpeta`: carpeta destino (Ansiedad/Depresion/Contexto)
