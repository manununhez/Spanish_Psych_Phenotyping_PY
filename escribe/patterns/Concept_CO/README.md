# `Concept_CO`: baseline histórico colombiano

## Propósito

`Concept_CO` conserva el baseline histórico colombiano del recurso original de fenotipado psiquiátrico en español. En el proyecto principal se mantiene como perfil de referencia para comparación y trazabilidad, no como capa operativa principal del híbrido vigente.

## Estructura activa del snapshot

Folders presentes en este snapshot:

- `Ansiedad/`
- `Depresion/`

Conteo actual de archivos JSON:

- `Ansiedad`: `18`
- `Depresion`: `33`
- `Contexto`: no aparece como carpeta versionada en este snapshot

## Cobertura actual

### Ansiedad

Incluye el mismo bloque histórico de categorías ansiosas que hoy siguen presentes en el core, incluyendo:

- ansiedad general;
- pánico;
- somatización;
- alteraciones de sueño;
- obsesiones/compulsiones;
- ideación persecutoria/paranoia;
- `medication_anxiety`.

### Depresión

Incluye la mayor parte del bloque depresivo hoy retenido en el core, incluyendo:

- ánimo deprimido;
- anhedonia;
- apatía/abulia;
- desesperanza, culpa y rumiación;
- ideación suicida y autolesión;
- sueño, apetito y peso;
- `medication_depression`.

Diferencias visibles respecto de `Concept_Core` en el snapshot actual:

- no expone carpeta `Contexto/`;
- no contiene `Minusvala.json` como archivo separado.

## Rol metodológico

En el proyecto principal, `Concept_CO` sirve para:

- baseline histórico del perfil `co`;
- comparación de cobertura frente a `core` y `py`;
- trazabilidad de qué mejoras pertenecen al núcleo depurado y cuáles a la adaptación regional.

## Qué no representa

`Concept_CO` no debe interpretarse como:

- mejor recurso clínico vigente del proyecto;
- capa recomendada para el híbrido actual;
- cierre metodológico final.

Su valor es comparativo e histórico.
