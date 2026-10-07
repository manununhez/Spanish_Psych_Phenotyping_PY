# Concept_PY: extensión paraguaya

## Propósito
PY añade al núcleo expresiones regionales, jopará y abreviaturas utilizadas como candidatos de extracción. El perfil `py` carga `Concept_Core + Concept_PY`; esta carpeta por sí sola no representa el perfil completo.

No todas sus expresiones son exclusivas de Paraguay. Su inclusión es una decisión léxica del recurso, no una equivalencia clínica universal ni una etiqueta de ansiedad/depresión.

## Inventario
| Carpeta | Archivos JSON | Reglas declaradas |
|---|---:|---:|
| Ansiedad | 8 | 17 |
| Depresion | 13 | 27 |
| Contexto | 2 | 5 |
| Total | 23 | 49 |

La extensión reúne 22 categorías distintas. Core + PY reúne 50: reutiliza categorías sintomáticas y añade las categorías auxiliares `Alcohol` y `UsoSustancias`. A diferencia de los archivos de contexto de Core, estos no emiten solo `Contexto`. No cambian las dos etiquetas supervisadas del consumidor, pero sí pueden cambiar el esquema de variables.

## Ejemplos de mapeo
| Expresión | Categoría del recurso | Interpretación |
|---|---|---|
| Bajoneado / bajoneada | `Animodeprimido` | Candidato de mención de ánimo |
| Argel / argelado / argelada | `Irritabilidad` | Variante léxica |
| Ataque de nervios | `Pnico` | Patrón explícito, no diagnóstico confirmado |
| Vy'a'ỹ | `Animodeprimido` | Variante registrada en el JSON |
| OH / OH+ | `Alcohol` | Abreviatura contextual |

La detección depende de tokenización y patrón, no solo de que una expresión aparezca en esta tabla. Ambigüedad, sujeto, negación y temporalidad deben evaluarse por separado.

## Manifiesto y procedencia
[lexicon_manifest.csv](lexicon_manifest.csv) conserva 50 filas y los campos `term_original`, `variant`, `fenotipo_canonico`, `categoria_core` y `carpeta`. Es un mapeo de vocabulario, no un registro de autorización o validación clínica.

Las 50 filas no corresponden uno a uno a las 49 reglas: una regla puede cubrir alternativas y un literal no es necesariamente idéntico a la variante del manifiesto. La fuente ejecutable son los JSON, no la cantidad de filas de la planilla.

El manifiesto no registra fuente individual, notas o subconjuntos consultados, responsable de aprobación, prompt/modelo LLM ni validación de cada expresión. El apoyo LLM descrito por el proyecto consumidor no permite afirmar que todas las entradas se generaron o filtraron con el mismo procedimiento. No se demuestra independencia inicial respecto del texto posteriormente asignado a prueba.

## Evaluación y límites
Comparar primero cobertura con perfiles explícitos y el mismo universo; después, evaluar modelos sin cambiar la ontología congelada. Una mejora de cobertura significa más coincidencias bajo un criterio dado, no mayor precisión clínica ni mejora predictiva aislada.

El desempeño de un modelo Core + PY frente a otro Core + LLM cambia varios factores; no prueba el efecto causal de PY. La revisión clínica del mapeo debe quedar documentada antes de presentar el recurso como validado.

Volver al [README principal](../../../README.md) para ejemplo Python, limitaciones de carga, objetos compartidos y reproducibilidad.
