import os
import pandas as pd
import spacy
import medspacy
from medspacy.ner import TargetRule


#########################
# LOAD DEFAULT PIPELINE #
#########################

nlp            = medspacy.load(   'es_core_news_md', 
                                  enable=['tok2vec', 'morphologizer', 'attribute_ruler', 'lemmatizer'])

sentencizer    = nlp.replace_pipe('medspacy_pyrush',        'medspacy_pyrush', 
                                  config={'rules_path': 'json_patterns/sentencizer/rush_rules_mod.tsv'})

target_matcher = nlp.replace_pipe('medspacy_target_matcher', 'medspacy_target_matcher', 
                                  config={'rules'     : None})

context        = nlp.replace_pipe('medspacy_context',        'medspacy_context', 
                                  #config={'rules'     : None})
                                  #config={'rules'     : 'json_patterns/context/patterns_for_ConText_by_juan_1.json'})
                                  config={'rules'     : 'json_patterns/context/patterns_for_ConText_by_juan_2.json'})

print("Components in NLP pipeline:")
for p in nlp.pipe_names:
    print('\t-',p)
    
########################
# ADD DEFAULT PATTERNS #
########################

def add_json_patterns_from_dir( direc = 'json_patterns/concepts/done/', nlp_to_update=None ):
    
        # get rules from json files in directory
    rules_json = [json for json in os.listdir(direc) if '.json' in json]
    print("N json files:\t", len(rules_json))

    rules     = sum([pd.read_json(direc+'/'+file)['target_rules'].tolist() for file in rules_json],[])
    rules_tbl = pd.DataFrame( rules ).assign(target_rules = [TargetRule.from_dict(rule) for rule in rules])
    rules_tbl = rules_tbl.set_index('category').sort_index()

    if nlp_to_update is not None:
            # add rules to target_matcher from medspacy
        target_matcher = nlp.replace_pipe('medspacy_target_matcher', 'medspacy_target_matcher', config={'rules':None})
        _ = [target_matcher.add( rule ) for rule in rules_tbl['target_rules']]
        print("N of rules : \t", len(target_matcher.rules))
        
    return rules_tbl

#########################
# TEST ON DEFAULT TABLE #
#########################

def run_NLP_on_records( nlp, tbl, cols, context=True ):
    tbl = tbl.fillna('')

    pt_ents = []

    for i in tbl.index:
        for field in cols:

            doc = nlp(tbl.loc[i, field])
            for ent in doc.ents:

                if context:
                    if not ent._.is_family:
                        if not ent._.is_hypothetical:
                            if not ent._.is_negated:
                #                if not ent._.is_historical:
                #                    if not ent._.is_uncertain:
                                pt_ents.append( [i, field, ent] )

                else:
                    pt_ents.append( [i, field, ent] )
                    
    pt_ents = pd.DataFrame( pt_ents, columns=['EHR_ID','field', 'ent'])
    
    return pt_ents