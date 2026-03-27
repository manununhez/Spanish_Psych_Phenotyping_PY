# Núcleo Clínico Depurado (`Concept_Core`)

## 📋 Propósito

Esta carpeta contiene el **núcleo clínico depurado** del proyecto. En la convención canónica del repositorio principal, esta capa se llama `Concept_Core`.

Su función es reunir reglas más portables y menos dependientes de localismos, sobre las que luego puede cargarse la capa regional paraguaya (`Concept_PY`).

## 🎯 Caso de Uso Principal

**Clasificación binaria rule-based** de relatos clínicos en español para determinar presencia de:
- **Ansiedad**: 18 fenotipos específicos
- **Depresión**: 31 fenotipos específicos
- **Compartidos**: 5 fenotipos


## 📊 Ventajas sobre Corpus Separados

### Comparación: CSJDM vs HOMO vs Unified

| Aspecto | CSJDM | HOMO | **Unified** |
|---------|-------|------|-------------|
| **Cobertura** | Media | Media | **Alta** ✅ |
| **Errores ortográficos** | Sí | No | **Sí** ✅ |
| **Variantes formales** | No | Sí | **Sí** ✅ |
| **Duplicados** | N/A | N/A | **Eliminados** ✅ |
| **Mantenimiento** | 2 archivos | 2 archivos | **1 archivo** ✅ |

### Ejemplo Práctico: "Ansiedad"

**CSJDM solo**:
```json
["ansiedad", "anisiosa", "ansioso", "anisoa", "asnioso", "ansiad"]
```

**HOMO solo**:
```json
["ansiedad", "ansiosa", "ansioso", "ansiosas", "ansiosos"]
```

**Unified (RECOMENDADO)**:
```json
["anisiosa", "anisoa", "ansiad", "ansiedad", "ansiosa", "ansiosas", 
 "ansioso", "ansiosos", "asnioso"]
```

✅ Captura **errores + variantes correctas** = Máxima recall

## 📁 Contenido

### Fenotipos de Depresión (31)
```
Animodeprimido.json          - Ánimo deprimido, tristeza
Anhedonia.json               - Pérdida de placer
Sntomasdepresivosgenerales.json - Síntomas depresivos globales
Bajaconcentracin.json        - Dificultad de concentración
Culpa.json                   - Sentimientos de culpa
Desesperanza.json            - Visión pesimista del futuro
Rumiacin.json                - Pensamientos repetitivos negativos
Prospeccindesesperanzada.json - Prospección negativa
Apata.json                   - Falta de motivación
Abulia.json                  - Ausencia de voluntad
Bajaenerga.json              - Fatiga, cansancio
Fatiga.json                  - Fatiga persistente
Retrasopsicomotor.json       - Enlentecimiento motor/cognitivo
Llantofcil.json              - Llanto frecuente
Disforia.json                - Malestar emocional
Irritabilidad.json           - Irritabilidad
Hipotimia.json               - Ánimo bajo
SueoInsomnio.json            - Insomnio
SueoDespertartemprano.json   - Despertar precoz
SueoHipersomnio.json         - Sueño excesivo
SueoAlterado.json            - Patrón de sueño alterado
Apetitodisminucinde.json     - Pérdida de apetito
Apetitoaumentode.json        - Aumento de apetito
PesoPrdida.json              - Pérdida de peso
PesoIncremento.json          - Aumento de peso
Ideacinsuicida.json          - Ideas suicidas
Ideasdemuerte.json           - Preocupación por la muerte
Intentosuicida.json          - Conducta suicida
Autolesin.json               - Autolesiones
RetraimientosocialAislamiento.json - Aislamiento social
Soledad.json                 - Sentimiento de soledad
```

### Fenotipos de Ansiedad (18)
```
Ansiedad.json                - Ansiedad generalizada
AngustiaMiedoTemor.json      - Angustia, miedo, ataques de nervios
Sntomasansiososgenerales.json - Síntomas ansiosos globales
Pnico.json                   - Ataques de pánico
DespersonalizacinDesrealizacin.json - Síntomas disociativos
Obsesiones.json              - Pensamientos obsesivos
Compulsiones.json            - Comportamientos compulsivos
SueoPesadillas.json          - Pesadillas
SntomassomticosEjemplos.json - Manifestaciones somáticas
Agitacinpsicomotora.json     - Inquietud motora
Labilidademocional.json      - Variabilidad emocional
Ideacinpersecutoria.json     - Ideas persecutorias
Paranoia.json                - Paranoia
```

## 🔧 Uso en Modelo Rule-Based

### Estrategia de Clasificación Binaria

```python
# Pseudocódigo para clasificación
def classify_clinical_text(text):
    # 1. Cargar patrones unificados
    depression_phenotypes = load_unified_phenotypes("depression")
    anxiety_phenotypes = load_unified_phenotypes("anxiety")
    
    # 2. Extraer menciones
    depression_mentions = extract_mentions(text, depression_phenotypes)
    anxiety_mentions = extract_mentions(text, anxiety_phenotypes)
    
    # 3. Calcular scores
    depression_score = len(depression_mentions) / len(depression_phenotypes)
    anxiety_score = len(anxiety_mentions) / len(anxiety_phenotypes)
    
    # 4. Clasificar
    threshold = 0.15  # Ajustar según validación
    
    has_depression = depression_score >= threshold
    has_anxiety = anxiety_score >= threshold
    
    return {
        "depression": has_depression,
        "anxiety": has_anxiety,
        "comorbid": has_depression and has_anxiety,
        "depression_score": depression_score,
        "anxiety_score": anxiety_score,
        "depression_phenotypes": depression_mentions,
        "anxiety_phenotypes": anxiety_mentions
    }
```

### Ventajas del Enfoque Rule-Based

✅ **Interpretabilidad**: Cada predicción es explicable  
✅ **Bajo costo computacional**: No requiere GPU  
✅ **Adaptabilidad**: Fácil agregar/modificar patrones  
✅ **Sin entrenamiento**: Funciona inmediatamente  
✅ **Multilingüe**: Patrones en español nativo  

## 🧪 Validación Recomendada

### Antes de usar en producción:

1. **Validación con corpus paraguayo**:
   ```bash
   # Anotar muestra de 100-200 relatos clínicos de Paraguay
   # Calcular métricas: precision, recall, F1
   ```

2. **Ajuste de umbrales**:
   - Validar threshold óptimo para clasificación binaria
   - Considerar umbrales diferentes para ansiedad vs depresión

3. **Análisis de falsos positivos/negativos**:
   - Identificar patrones faltantes específicos de Paraguay
   - Agregar reglas locales si es necesario

4. **Comparación con anotadores humanos**:
   - Inter-annotator agreement (Kappa)
   - Concordancia con diagnósticos clínicos


## 🔄 Actualización

Estos archivos fueron generados automáticamente fusionando:
- `escribe/patterns/Concept/CSJDM/*.json`
- `escribe/patterns/Concept/HOMO/*.json`


## 📚 Referencias

- **Corpus origen**: Hospitales de Medellín, Colombia
- **Códigos diagnósticos**: CIE-10 (F32, F33, F40, F41, F42)
- **Criterios**: DSM-5 para trastornos depresivos y de ansiedad
