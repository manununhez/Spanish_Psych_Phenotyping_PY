# `Concept_PY`: adaptación regional paraguaya

## Propósito

`Concept_PY` es la capa de adaptación regional paraguaya que se carga encima de `Concept_Core`. Su objetivo es ampliar cobertura léxica mediante variantes locales, jopará, abreviaturas institucionales y expresiones frecuentes en notas clínicas del IPS.

No reemplaza al core: lo extiende.

## Estructura activa del snapshot

Folders presentes:

- `Ansiedad/`
- `Depresion/`
- `Contexto/`

Conteo actual de archivos JSON:

- `Ansiedad`: `8`
- `Depresion`: `13`
- `Contexto`: `2`

## Qué añade metodológicamente

`Concept_PY` añade cobertura regional sobre tres frentes:

- síntomas ansiosos y depresivos ya presentes en el dominio clínico del proyecto;
- expresiones locales o abreviadas que el core no capturaba bien;
- algunas categorías auxiliares de contexto útiles para consumo y entorno clínico.

No cambia la tarea supervisada principal del proyecto, que sigue siendo binaria:

- `ansiedad`
- `depresion`

## Cobertura actual

### Ansiedad

Archivos activos:

- `Agitacinpsicomotora.json`
- `AngustiaMiedoTemor.json`
- `Irritabilidad.json`
- `Pnico.json`
- `Prospeccindesesperanzada.json`
- `Rumiacin.json`
- `Sntomasansiososgenerales.json`
- `SntomassomticosEjemplos.json`

### Depresión

Archivos activos:

- `Anhedonia.json`
- `Animodeprimido.json`
- `Apata.json`
- `Apetitoaumentode.json`
- `Apetitodisminucinde.json`
- `Bajaconcentracin.json`
- `Culpa.json`
- `Fatiga.json`
- `Ideacinsuicida.json`
- `RetraimientosocialAislamiento.json`
- `Rumiacin.json`
- `Soledad.json`
- `SueoAlterado.json`

### Contexto

Archivos activos:

- `Alcohol.json`
- `UsoSustancias.json`

A diferencia del core, en esta capa las reglas de contexto actuales emiten categorías específicas (`Alcohol`, `UsoSustancias`) en lugar de colapsarse bajo `Contexto`.

## Manifiesto

`lexicon_manifest.csv` documenta el mapeo de términos y variantes. Campos relevantes:

- `term_original`
- `variant`
- `fenotipo_canonico`
- `categoria_core`
- `carpeta`

## Cómo se usa

Se carga como perfil `py`:

- `Concept_Core` + `Concept_PY`

Recomendación metodológica vigente:

1. validar primero la cobertura con `05_brecha_lexica_co_core_py.ipynb`;
2. generar luego features híbridas en `06_ingenieria_features_hibridas.ipynb`;
3. usar el perfil `py` en entrenamiento y ablación cuando ya se quiera medir el aporte regional sobre el híbrido.

## Qué no hace

`Concept_PY` no redefine los labels supervisados del proyecto ni sustituye el núcleo clínico. Su rol es ampliar cobertura y auditabilidad regional.
