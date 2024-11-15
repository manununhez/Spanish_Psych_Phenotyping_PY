# Extraction of Psychiatric Phenotypes from Clinical Notes in Spanish
cNLP tool for pattern-based named entity recognition of psychiatric phenotypes in Spanish

# Installation Requirements
``` 
conda create --name nlp_pheno_es -c conda-forge python=3.11 spacy=3.5 pandas -y
conda activate nlp_pheno_es

pip install --no-cache-dir medspacy
python -m spacy download es_core_news_md
``` 

## Uninstall
``` 
conda activate nlp_pheno_es

pip install pip-autoremove
pip-autoremove medspacy
pip uninstall es_core_news_md -y

conda deactivate
conda remove --name nlp_pheno_es --all
``` 

# Usage

### Load NLP object and select concepts to extract
Load all concepts by default
```
from escribe.default_nlp import nlp, select_concepts
nlp = select_concepts(nlp)
```
Load specific concepts:
```
nlp = select_concepts(nlp, concepts = ['Usodesustancias','Anhedonia'])
```
Load concepts from a specific source (replace <SOURCE> with CSJDM, HOMO, or COMBINED to load algorithm patterns):
```
nlp = select_concepts(nlp, json_dir = 'escribe/patterns/Concept/<SOURCE>')
```

### Extract concepts from text
Using the NLP object
```
doc = nlp('el padre biologico nunca sufre de anhedonia')
doc.ents                           # (anhedonia,)
doc.ents[0].label_                 # 'Anhedonia'
doc.ents[0]._.is_family            # True
doc.ents[0]._.is_historical        # False
doc.ents[0]._.is_hypothetical      # False
doc.ents[0]._.is_negated           # True
doc.ents[0]._.is_uncertain         # False
```

# Citation
```
medRxiv: ...
```
