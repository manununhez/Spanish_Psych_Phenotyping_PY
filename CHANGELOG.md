# Cambios

## 2.0.0 (04/11/2026)

Primera versión con manifiesto congelado. Parte del commit
`916c1d97b8a9df947b2a457b95a5a05c123ea0ce`, que es la referencia de las
corridas históricas del proyecto consumidor (anteproyecto y búsqueda 22.44).

### Corregido
- **Orden del pipeline (R1).** `cli._reset_target_matcher` quitaba el
  detector de términos y lo volvía a agregar al final, después de ConText. Por
  esa vía ConText no veía las menciones: ninguna quedaba negada, como
  antecedente ni como familiar.
  - **Ahora:** se vacían las reglas conservando la posición.
    `check_order()` falla si el detector queda después de ConText.
- **Perfiles independientes (R2).** `build_pipeline` reutilizaba el objeto
  global `nlp`, así que construir `py` después de `core` modificaba también
  el objeto «core».
  - **Ahora:** cada llamada crea un objeto propio con `make_nlp()`, salvo
    que se pase `nlp_obj`.
  - `fenos_cfg` pasa a ser opcional y se conserva por compatibilidad.
- **Orden determinista en `select_concepts`.** Las carpetas se recorrían con
  un `set`, cuyo orden depende de `PYTHONHASHSEED`, y el desempate entre
  categorías superpuestas variaba entre ejecuciones (por ejemplo, «sin
  energía»: Abulia o Fatiga).
  - **Ahora:** se respeta el orden de la configuración, igual que en
    `build_pipeline`.
- **Capa vacía.** `load_concept_layer` ahora falla siempre si no encuentra
  JSON. Antes solo fallaba con `verbose=True`.

### Léxico (R3)
- **Repeticiones reales eliminadas en Core:**
  - `Compulsiones` y `Obsesiones`: la regla literal «TOC», idéntica a «toc»
    porque la coincidencia no distingue mayúsculas;
  - `SueoHipersomnio`: la regla «hipersomnio», con el mismo patrón que
    «hipersomnia».
  - **Desempate de «TOC»:** se conservó la regla que mantiene el desempate
    previo entre Obsesiones y Compulsiones.
- **Conceptos compartidos sincronizados** entre `Ansiedad/` y `Depresion/`
  (copia idéntica en ambas carpetas, igual a la unión):
  - Core `SueoInsomnio`: se agregó «despertares precoces» a la copia de
    `Depresion/`;
  - PY `Rumiacin`: ambas copias contienen «preocupado por todo» y «Darle
    vueltas».
- **Concept_CO no se modificó.** Es la base histórica; sus 3 repeticiones
  equivalentes se conservan y quedan fijadas en las pruebas.

### Agregado (R5)
- `tools/manifiesto_lexico.py` (`generar`, `verificar`, `inventario`) y
  `escribe/patterns/MANIFIESTO_LEXICO.json`: versión, SHA-256 por archivo,
  conteos por capa, carpeta y perfil, y hashes de ConText, RuSH y configs.
- `tests/test_recurso.py` (12 pruebas):
  - orden;
  - independencia de perfiles;
  - reglas cargadas igual a declaradas;
  - regresión de ConText con «Niega / Antecedentes de / Madre con ansiedad»;
  - igualdad entre `select_concepts` y `build_pipeline`;
  - unicidad;
  - sincronía de conceptos compartidos;
  - manifiesto.

### Documentación
- README: perfiles independientes, corrección del orden, manifiesto y
  pruebas, y procedencia de la medicación (R4).

### Impacto en resultados (verificado con una batería sintética)
La batería tiene 1257 frases: cada literal del léxico afirmado, negado y como
antecedente. No usa textos clínicos.

| Perfil | Reglas declaradas antes → ahora | Firmas efectivas | Etiquetas frente a `build_pipeline` anterior | Atributos ConText frente al orden correcto |
|---|---|---|---|---|
| co | 424 → 424 | 370 = 370 | 0 frases distintas | 0 distintas |
| core | 448 → 446 | 395 = 395 | 0 | 0 |
| py | 497 → 497 | 444 = 444 | 0 | 0 |

- **Detección:** no cambia. Las etiquetas son las mismas que con
  `build_pipeline` 1.x.
- **Contexto:** sí cambia. Con `build_pipeline` 1.x ninguna frase de la
  batería quedaba negada (0 de 1257); con 2.0.0 quedan 347 (co), 348 (core)
  y 383 (py), igual que el orden correcto.
- **Recálculo con 2.0.0:** cambian las columnas que dependen de ConText
  (`niega_*`, filtros de retención). Las detecciones (`rule_*`) no cambian.
  Los resultados congelados con 1.x se conservan como históricos y no se
  sobrescriben.
