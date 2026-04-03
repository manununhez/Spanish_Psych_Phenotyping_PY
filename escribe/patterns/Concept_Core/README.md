# `Concept_Core`: núcleo clínico depurado

## Propósito

`Concept_Core` es la capa clínica estable que el proyecto usa como base portable para extraer evidencia psiquiátrica sobre texto clínico en español. Su función es separar:

- mejoras generales del recurso clínico;
- control de ruido estructural y organización por carpetas clínicas;
- adaptaciones regionales posteriores, que viven en `Concept_PY`.

No debe interpretarse como un benchmark independiente ni como un clasificador binario completo por sí solo. En el proyecto principal funciona como recurso de extracción y soporte del pipeline híbrido.

## Estructura activa del snapshot

Folders clínicos presentes en este snapshot:

- `Ansiedad/`
- `Depresion/`
- `Contexto/`

Conteo actual de archivos JSON:

- `Ansiedad`: `18`
- `Depresion`: `34`
- `Contexto`: `3`

## Cómo se usa downstream

Cada archivo `.json` aporta reglas `TargetRule` de medSpaCy. Los campos relevantes son:

- `category`: nombre técnico que emite la regla y que downstream se transforma en columnas `rule_<category>`;
- `literal`: rótulo humano de la evidencia concreta;
- `pattern`: patrón tokenizado o literal.

Regla práctica:

- en `Ansiedad/` y `Depresion/`, la mayoría de los archivos emiten una categoría específica propia;
- en `Contexto/`, los archivos actuales emiten la categoría común `Contexto`, mientras que el detalle clínico de subtipos queda en `literal`.

## Cobertura clínica actual

### Ansiedad

Archivos activos:

- `Agitacinpsicomotora.json`
- `AngustiaMiedoTemor.json`
- `Ansiedad.json`
- `Bajaconcentracin.json`
- `Compulsiones.json`
- `DespersonalizacinDesrealizacin.json`
- `Fatiga.json`
- `Ideacinpersecutoria.json`
- `Irritabilidad.json`
- `Obsesiones.json`
- `Paranoia.json`
- `Pnico.json`
- `Sntomasansiososgenerales.json`
- `SntomassomticosEjemplos.json`
- `SueoAlterado.json`
- `SueoInsomnio.json`
- `SueoPesadillas.json`
- `medication_anxiety.json`

Qué aporta:

- ansiedad general y síntomas ansiosos globales;
- miedo/angustia y pánico;
- somatización;
- alteraciones de sueño;
- obsesividad/compulsividad;
- fenómenos persecutorios o de desrealización cuando aparecen explicitados en la nota;
- evidencia farmacológica separada para el dominio ansioso.

### Depresión

Archivos activos:

- `Abulia.json`
- `Anhedonia.json`
- `Animodeprimido.json`
- `Apata.json`
- `Apetitoaumentode.json`
- `Apetitodisminucinde.json`
- `Autolesin.json`
- `Bajaconcentracin.json`
- `Bajaenerga.json`
- `Culpa.json`
- `Desesperanza.json`
- `Disforia.json`
- `Fatiga.json`
- `Hipotimia.json`
- `Ideacinsuicida.json`
- `Ideasdemuerte.json`
- `Intentosuicida.json`
- `Irritabilidad.json`
- `Labilidademocional.json`
- `Llantofcil.json`
- `Minusvala.json`
- `PesoIncremento.json`
- `PesoPrdida.json`
- `Prospeccindesesperanzada.json`
- `RetraimientosocialAislamiento.json`
- `Retrasopsicomotor.json`
- `Rumiacin.json`
- `Sntomasdepresivosgenerales.json`
- `Soledad.json`
- `SueoAlterado.json`
- `SueoDespertartemprano.json`
- `SueoHipersomnio.json`
- `SueoInsomnio.json`
- `medication_depression.json`

Qué aporta:

- ánimo deprimido, anhedonia, apatía y abulia;
- baja energía, fatiga y enlentecimiento;
- culpa, desesperanza, prospección negativa y rumiación;
- ideación suicida, ideas de muerte, intento y autolesión;
- alteraciones vegetativas y del sueño;
- evidencia farmacológica separada para el dominio depresivo.

### Contexto

Archivos activos:

- `Agresividad.json`
- `Alcohol.json`
- `Usodesustancias.json`

En el snapshot actual estos archivos emiten `category = Contexto` y usan `literal` para distinguir la evidencia contextual específica.

Qué aporta:

- marcadores auxiliares de consumo y agresividad;
- soporte para denoising, auditoría y análisis contextual;
- no redefine por sí solo la tarea supervisada principal `ansiedad` vs `depresion`.

## Medicación como evidencia separada

`medication_anxiety` y `medication_depression` se conservan como categorías independientes porque downstream el proyecto las trata como evidencia terapéutica separada. No se fusionan directamente con síntomas ni con LLM para decidir la tarea diferencial.

## Rol metodológico en el proyecto principal

`Concept_Core` participa en:

- `03_denoising_reglas_core.ipynb`: señal clínica mínima para conservar notas;
- `05_brecha_lexica_co_core_py.ipynb`: comparación de cobertura entre perfiles;
- `06_ingenieria_features_hibridas.ipynb`: construcción de `rule_*`, `niega_*` y `rule_medication_*`;
- `07_entrenamiento_modelos_hibridos.ipynb`: base simbólica del híbrido;
- `09b_cierre_modelos_dev.ipynb`: soporte indirecto para auditabilidad e interpretabilidad.

## Qué no debe inferirse de esta carpeta

`Concept_Core` por sí sola no define:

- un umbral oficial de clasificación binaria;
- un modelo final cerrado;
- selección de backbone contextual;
- la comparación con `TF-IDF`, `BETO` o `RoBERTa`;
- la rúbrica multicriterio del cierre en `dev`.

Esas decisiones viven en el repositorio principal.
