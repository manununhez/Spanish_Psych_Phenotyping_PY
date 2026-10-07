# Concept_Core: núcleo clínico depurado

## Propósito y formación
Core organiza el núcleo de extracción general a partir del recurso histórico, separándolo de las adiciones regionales. El historial y los JSON conservan cambios de patrones, medicación, minusvalía y contexto. No documentan una selección clínica individual de cada variante ni prueban que su construcción consistiera únicamente en eliminar colombianismos con un LLM.

El perfil `core` carga esta capa; `py` añade PY encima. La portabilidad es un objetivo de diseño, no un resultado de validación externa.

## Inventario
| Carpeta | Archivos JSON | Reglas declaradas |
|---|---:|---:|
| Ansiedad | 18 | 163 |
| Depresion | 34 | 274 |
| Contexto | 3 | 11 |
| Total | 55 | 448 |

Reúne 48 categorías distintas. La cantidad de archivos no equivale a categorías o features: por ejemplo, sueño, fatiga y concentración pueden compartir categoría entre carpetas.

## Qué representa la evidencia
Los patrones cubren síntomas, fenómenos de sueño/apetito/peso y evidencia terapéutica. `category` determina la categoría emitida; `literal` identifica el patrón de forma legible. Los identificadores técnicos, incluidos los nombres históricos sin tildes, se mantienen por compatibilidad con las columnas y modelos existentes.

Los archivos de contexto [Agresividad](Contexto/Agresividad.json), [Alcohol](Contexto/Alcohol.json) y [Uso de sustancias](Contexto/Usodesustancias.json) emiten todos `category = Contexto`; el detalle se distingue en `literal`. No suponer que cada archivo produce una columna específica con su nombre.

`medication_anxiety` y `medication_depression` son evidencia terapéutica separada. No se fusionan con síntomas ni convierten una prescripción en diagnóstico.

## Uso en el pipeline consumidor
Core participa en la elegibilidad de notas, comparación de cobertura y extracción de variables. El consumidor transforma menciones en `rule_*` y negaciones del paciente en `niega_*`; esa política de retención no reside en esta carpeta.

La carga léxica y la aseveración son operaciones diferentes. El orden requerido es matcher antes de ConText. La ruta `build_pipeline` actual altera ese orden; véase la [limitación documentada](../../../README.md). Por eso la presencia de reglas históricas, familiares o negadas en el recurso no demuestra que el filtro efectivo las haya tratado correctamente.

## Límites
Core no determina split, umbral, backbone, clasificador ni pesos del ensamble. Una entidad aceptada puede ser terapéutica/contextual y no suficiente para distinguir ansiedad de depresión. Más cobertura no acredita correctitud clínica; la auditoría experta requiere revisar menciones y notas retenidas/excluidas.

Volver al [README principal](../../../README.md) para configuración, ejemplo de carga y reproducibilidad.
