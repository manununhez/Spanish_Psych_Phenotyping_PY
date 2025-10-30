# Spanish Psych Phenotyping — Paraguay (Fork A/D)

Este fork está basado en el proyecto original [`Spanish_Psych_Phenotyping`](https://github.com/clarafrydman/Spanish_Psych_Phenotyping),
pero se especializa en **trastornos de depresión y ansiedad**.

Incluye un CLI unificado (`cli.py`) con dos perfiles:
- `col`: baseline colombiano (usa `escribe/patterns/Concept/`)
- `py`: versión paraguaya (usará `escribe/patterns/Concept_PY/`)

## Uso básico
```bash
python cli.py --profile col \
  --input ../psych-phenotyping-paraguay/data/ips_clean.csv \
  --output ../psych-phenotyping-paraguay/data/rule_based_col.csv
```

## Estructura

escribe/patterns/Concept/        → patrones originales del proyecto
escribe/patterns/Concept_PY/     → versión adaptada para Paraguay
escribe/patterns/ContextRules/   → reglas contextuales originales
configs/
  col_config.yml                 → config para baseline colombiano
  py_config.yml                  → config para futura versión PY
cli.py


---

## 6️⃣ `.gitignore` y `requirements.txt`

**.gitignore**
```txt
__pycache__/
outputs/
.ipynb_checkpoints/
*.pyc
.DS_Store
```

## Nota metodológica
Este fork especializa el proyecto **Spanish_Psych_Phenotyping** en los fenotipos de **Ansiedad** y **Depresión**, filtrando los *concepts* del repositorio original para enfocarse en el bloque afectivo según **CIE-10**.

- **Ansiedad / Pánico:** **F40–F41**  
- **Depresión:** **F32.2, F32.3, F33.1, F33.2, F33.3, F33.4**  
- **Sueño (comórbidos A/D):** síntomas frecuentes en F32.x y F41.x (insomnio, hipersomnia, despertar temprano, etc.)

> **Proveniencia:** todos los JSON listados provienen del set original (CSJDM) y se incluyen aquí como **filtro temático** (ansiedad, depresión y sueño).  
> **Nota:** algunos archivos del set original pueden no contener reglas/patrones; se conservan por **trazabilidad** y para unificar criterios diagnósticos.

---

## Estructura de directorios (filtrada)

```
escribe/patterns/Concept/
├─ Ansiedad/
├─ Depresion/
└─ Sueno/
```

---

## Fenotipos de **Ansiedad / Pánico** (CIE-10: F40–F41)

| Archivo JSON | Constructo clínico | CIE-10 (referencia) | Comentario |
|---|---|---:|---|
| `Ansiedad.json` | Ansiedad inespecífica / GAD | F41.1 | Preocupación, activación somato-psíquica |
| `AngustiaMiedoTemor.json` | Angustia / miedo | F41.0–F41.9 | Afecto ansioso prominente, crisis subjetivas |
| `Irritabilidad.json` | Irritabilidad | F41.1 | Síntoma transversal en ansiedad generalizada |

> **Observación:** en el set original no aparece un JSON específico para **ataque de pánico (F41.0)** con síntomas autonómicos (palpitaciones, disnea/ahogo, temblor, sudoración, miedo a morir/perder control). La cobertura de pánico se apoya aquí en “Angustia/Miedo/Temor”.

---

## Fenotipos de **Depresión** (CIE-10: F32.2, F32.3, F33.1–F33.4)

| Archivo JSON | Constructo clínico | CIE-10 (referencia) | Comentario |
|---|---|---:|---|
| `Agitacinpsicomotora.json` | Agitación psicomotora | F32.3 | Marcador de gravedad |
| `Anhedonia.json` | Pérdida de interés/placer | F32–F33 | Síntoma nuclear |
| `Animodeprimido.json` | Ánimo deprimido | F32–F33 | Síntoma nuclear |
| `Animoexpansivo.json` | Ánimo expansivo | — | **No depresivo**; útil para control/exclusión diferencial |
| `Apata.json` | Apatía | F32–F33 | Motivacional |
| `Apetitoaumentode.json` | Aumento de apetito | F33.1 | Subtipo atípico |
| `Apetitodisminucinde.json` | Disminución del apetito | F32.2 | Somático frecuente |
| `Bajaconcentracin.json` | Dificultad de concentración | F32.3 | Cognitivo |
| `Culpa.json` | Culpa excesiva/inadecuada | F32.3, F33.x | Cognición negativa |
| `Desesperanza.json` | Hopelessness | F32.3, F33.x | Predictor de gravedad |
| `Fatiga.json` | Fatiga / cansancio | F32.2–F33.1 | Somático |
| `Ideacinsuicida.json` | Ideación suicida | F32.3, F33.x | Suicidabilidad (gravedad) |
| `Ideasdemuerte.json` | Ideas de muerte | F32.3, F33.x | Suicidabilidad |
| `Intentosuicida.json` | Intento suicida | F33.3–F33.4* | Especificador de curso/gravedad |
| `Llantofcil.json` | Labilidad/llanto fácil | F32–F33 | Apoyo clínico |
| `Negativismo.json` | Valencia negativa persistente | F32–F33 | Distorsión cognitiva asociada |
| `RetraimientosocialAislamiento.json` | Retraimiento/aislamiento social | F32–F33 | Comportamental |
| `Retrasopsicomotor.json` | Retardo psicomotor | F32.3 | Marcador de gravedad |
| `Sntomasdepresivosgenerales.json` | Síntomas depresivos inespecíficos | F32–F33 | Sostén / screening |

\* La suicidabilidad no es un diagnóstico independiente en CIE-10, pero se reporta por su relevancia clínica en episodios depresivos graves y trastornos recurrentes.

---

## Fenotipos de **Sueño** (comórbidos con A/D)

| Archivo JSON | Constructo clínico | CIE-10 (referencia) | Comentario |
|---|---|---:|---|
| `SueoInsomnio.json` | Insomnio | F32.x / F41.x | Muy prevalente en A/D |
| `SueoHipersomnio.json` | Hipersomnia | F32.1–F33.1 | Subtipo atípico/curso |
| `SueoDespertartemprano.json` | Despertar precoz | F32.x | Patrón melancólico |
| `SueoAlterado.json` | Alteración del sueño (inespecífica) | F32–F41 | Sostén |
| `SueoPesadillas.json` | Pesadillas | F41.x | Arousal/ansiedad |
| `Somnolencia.json` | Somnolencia diurna | F32.x | Somático relacionado |

---

## Criterios de inclusión / exclusión

- **Incluidos:** síntomas nucleares y asociados de **ansiedad/pánico (F40–F41)** y **depresión (F32.2–F33.4)**; y **sueño** por comorbilidad frecuente en ambos cuadros.  
- **Excluidos:** fenómenos fuera del espectro A/D (psicosis, TOC, bipolaridad, sustancias, etc.), salvo `Animoexpansivo.json`, que se conserva para **control** (útil en análisis diferenciales).  
- **Integridad del set:** si algún JSON del original no trae reglas/patrones, igualmente se **enumera** aquí por trazabilidad diagnóstica; su estado no afecta el criterio de inclusión temática.

---

## Justificación diagnóstica (CIE-10)

- **Trastornos de ansiedad y pánico (F40–F41):** preocupación excesiva, síntomas de activación autonómica (palpitaciones, disnea, sudoración, temblor), tensión muscular, hipervigilancia, irritabilidad, angustia/miedo.  
- **Episodio depresivo y trastorno depresivo recurrente (F32.2–F33.4):** ánimo deprimido, anhedonia, fatiga, alteraciones psicomotoras, dificultades cognitivas (concentración), distorsiones negativas (culpa, desesperanza), e indicios de suicidabilidad (ideas de muerte/ideación/intentona).  
- **Sueño:** insomnio/hipersomnia/despertar temprano como manifestaciones somáticas frecuentes que modulan diagnóstico y gravedad.

---

## Alcance y propósito

Esta selección **filtra** el repositorio original para delimitar un **baseline clínico** centrado en A/D, mejorando coherencia diagnóstica, interpretabilidad y comparabilidad con datasets clínicos alineados a **F40–F41** y **F32–F33**.  
El objetivo es **reproducibilidad** y **trazabilidad**: cada fenotipo mantiene nombre y referencia al concepto original, documentado aquí con su mapeo CIE-10.
