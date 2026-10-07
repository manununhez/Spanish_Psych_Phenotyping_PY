# Concept_CO: referencia histórica colombiana

## Propósito
Esta capa conserva la referencia histórica del recurso `Spanish_Psych_Phenotyping` para comparar con el núcleo depurado y la extensión paraguaya. El perfil `co` carga solo CO; no combina Core o PY ni selecciona un modelo clínico.

## Inventario
| Carpeta | Archivos JSON | Reglas declaradas |
|---|---:|---:|
| Ansiedad | 18 | 155 |
| Depresion | 33 | 269 |
| Total | 51 | 424 |

Las reglas reúnen 46 categorías distintas. Archivos, reglas y categorías son unidades diferentes; una categoría puede repetirse entre carpetas. No hay carpeta `Contexto` en esta capa: la configuración común puede avisar de su ausencia sin que eso signifique que se cargó contexto de Core.

## Contenido y lectura
Incluye patrones para ansiedad, ánimo, sueño, somatización, obsesiones/compulsiones, fenómenos persecutorios, ideación suicida y evidencia terapéutica `medication_anxiety`/`medication_depression`. Las carpetas organizan menciones, no diagnósticos exclusivos.

Frente al snapshot Core, CO no tiene `Minusvala.json` como archivo separado ni los tres archivos de contexto. Esta comparación estructural no demuestra inferioridad clínica ni que todas sus expresiones sean colombianismos.

## Reproducibilidad y límites
Mantener CO como referencia versionada. Toda modificación requiere trazabilidad; no reemplazarlo por Core bajo el mismo nombre para obtener mayor cobertura.

La carpeta no acredita validación clínica en Paraguay, procedencia individual de cada patrón ni rendimiento de clasificación. La negación y la temporalidad dependen de ConText y del orden efectivo de componentes; no basta con cargar las reglas.

Volver al [README principal](../../../README.md) para perfiles, ejemplo Python, limitaciones de carga y licencia.
