import os
import pandas as pd
from medspacy import load, ner

nlp            = load( 'es_core_news_md', enable=['tok2vec', 'morphologizer', 'attribute_ruler', 'lemmatizer'] )
sentencizer    = nlp.replace_pipe('medspacy_pyrush',         'medspacy_pyrush',         config={'rules_path': 'escribe/patterns/RuSH_ES.tsv'})
target_matcher = nlp.replace_pipe('medspacy_target_matcher', 'medspacy_target_matcher', config={'rules'     : None})
context        = nlp.replace_pipe('medspacy_context',        'medspacy_context',        config={'rules'     : 'escribe/patterns/ConText_ES.json'})

print("Components in NLP pipeline:")
for p in nlp.pipe_names:
    print('\t-',p)

def load_json_patterns_from_dir( json_dir ):
    
    rules_json = [json for json in os.listdir(json_dir) if '.json' in json]
    rules      = sum([pd.read_json(json_dir+'/'+file)['target_rules'].tolist() for file in rules_json],[])
    rules_tbl  = pd.DataFrame( rules ).assign(target_rules = [ner.TargetRule.from_dict(rule) for rule in rules])
    rules_tbl  = rules_tbl.set_index('category').sort_index()

    return rules_tbl

def select_concepts( nlp, json_dir = 'escribe/patterns/Concept/HOMO', concepts = ['all'], verbose=True ):

    target_matcher = nlp.replace_pipe('medspacy_target_matcher', 'medspacy_target_matcher', config={'rules':None})
    patterns = load_json_patterns_from_dir( json_dir = json_dir)
    if 'all' in concepts:
        _ = [target_matcher.add( rule ) for rule in patterns['target_rules']]
    else:
        _ = [target_matcher.add( rule ) for rule in patterns.loc[concepts,'target_rules']]

    if verbose:
        print("Concepts included:")
        rules = list(set([rule.category for rule in target_matcher.rules]))
        rules.sort()
        _ =[print('   ',rule) for rule in rules]

    return nlp
