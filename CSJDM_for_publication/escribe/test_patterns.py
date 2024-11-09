import spacy
import seaborn as sns
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

from medspacy.ner import TargetRule
from medspacy.visualization import visualize_ent, visualize_dep

from sklearn.metrics import precision_recall_fscore_support, confusion_matrix, cohen_kappa_score

#####
#####

def setup_new_concept_in_pipeline( nlp_, concept, num=1, directory = 'json_patterns/concepts/dev/' ):
    # reset matcher
    target_matcher = nlp_.replace_pipe('medspacy_target_matcher', 'medspacy_target_matcher', 
                                      config={'rules'     : None})
    # read new rules
    target_rules = pd.read_json(directory+concept+'.json')['target_rules'].tolist()

    # add last rule(s)
    num = num if num>0 else len(target_rules)
    print('Loading '+ str(num) +' rules')
    for n in range(1,num+1):
        new_rule = target_rules[-n]
        target_matcher.add(TargetRule.from_dict(new_rule))
    
    # present the added rule
    for rule in target_matcher.rules:
        print('--'*10)
        rule = rule.to_dict()
        for key in rule.keys():
            print(key,'\t',rule[key])
    return target_matcher

def test_nlp_for_concept( nlp_, ann_tbl, concept ):
    
    # get text and annotation to compare
    tbl = ann_tbl[['text',concept]].copy(deep=True)

    tbl['docs'] = [nlp_(text) for text in tbl['text']]
    tbl['pred'] = [concept in [ent.label_ for ent in doc.ents] for doc in tbl['docs']]

    stats = get_stats( tbl[concept], tbl['pred'], concept )

    display(stats.round(2))
    return tbl, stats

def get_stats(true, pred, name):
    conf_matrix  =                confusion_matrix( true, pred ).flatten()
    pr_rc_f1_spt = precision_recall_fscore_support( true, pred )
    kappa        =               cohen_kappa_score( true, pred )

    if conf_matrix.shape==(1,):
        return pd.Series([conf_matrix[0],0,0,0] + [0,0,0,0] + [0],
                         index=['TN','FP','FN','TP','Pr','Rc','F1','supt','kappa'], name=name)
    
    stats = pd.Series([s    for s in conf_matrix ] + \
                      [s[1] for s in pr_rc_f1_spt] + \
                      [              kappa       ],
          index=['TN','FP','FN','TP','Pr','Rc','F1','supt','kappa'], name=name)
    return stats

#####
#####

def find_FP(tbl, concept):
    for i,doc in tbl.loc[(tbl['pred']) & (tbl[concept]==0)].iterrows():
        print( '--'*10,'\n document i:', i )
        visualize_ent( doc['docs'] )
        
def find_FN( tbl, concept, text_tbl, concept_tbl ):
    for i,doc in tbl.loc[(~tbl['pred']) & (tbl[concept]>0)].iterrows():
        for j,eg in concept_tbl.loc[(concept_tbl['section']==text_tbl.loc[i]['section'])&
                                    (concept_tbl[  'entry']==text_tbl.loc[i][  'entry'])&
                                    (concept_tbl[  'label']==concept) ].iterrows():
            print( '--'*10,'\n document i:', i, '\t' ,
                 doc['text'][ max(0,eg['start_ch']-15) : min(eg['end_ch']+15, len(doc['text'])) ])

#####
#####

def test_all_patterns_for_concept( nlp_, ann_tbl, concept, directory = 'json_patterns/concepts/dev/' ):

    results_preds = []
    results_stats = []
    
    # read-in rules
    target_rules = pd.read_json(directory+concept+'.json')['target_rules'].tolist()

    for rule in target_rules:

        # reset matcher
        target_matcher=nlp_.replace_pipe('medspacy_target_matcher','medspacy_target_matcher',config={'rules':None})

        # add rule
        new_rule = TargetRule.from_dict(rule)
        target_matcher.add(new_rule)

        # display the rule being evaulated
        print('--'*10)
        new_rule = new_rule.to_dict()
        for key in new_rule.keys():
            print(key,'\t',new_rule[key])

        # run the pattern on the texts and compare with annotations
        preds, stats = test_nlp_for_concept( nlp_, ann_tbl, concept )
        results_preds.append(preds.rename(columns={'pred':new_rule['literal']}))
        results_stats.append(stats.rename(                new_rule['literal'] ))

    results_preds = pd.concat(
        [p.drop(columns='docs').reset_index().set_index(['index','text',concept]) for p in results_preds],
                             axis=1).astype(int).reset_index()
    
    results_stats = pd.concat(results_stats,axis=1).T.round(2)    
    results_stats.index.name = 'literal'

    return results_preds, results_stats
    
#####
#####

def saturation_curve(results_preds, results_stats, concept):
    
    lits_pats = results_stats.sort_values(['Rc','Pr'],ascending=False).index.tolist()
    cumm_pats = []

    for i in range(1,len(lits_pats)+1):
        cumm_pats.append( get_stats( results_preds[ concept ], 
                                     (results_preds[ lits_pats[:i] ].sum(1)>0).astype(int) ,
                                     lits_pats[i-1] ))

    cumm_pats = pd.concat(cumm_pats,axis=1).T.round(2)
    cumm_pats.index.name = 'literal'
    
    return cumm_pats

def plot_saturation_curve( cumm_tbl, figsize='auto', legend=True ):
    
    # invert order of patterns
    l = cumm_tbl.index.tolist()
    l.reverse()
    cumm_tbl_ = cumm_tbl.loc[l]
    
    # get the size right:
    if figsize=='auto': figsize = (3.5, len(l)/3)

    # plot as points
    ax = cumm_tbl_.reset_index().plot(y='literal',x='Rc',kind='scatter',xlim=(0,1.05),figsize=figsize)
    ax = cumm_tbl_.reset_index().plot(y='literal',x='Pr',kind='scatter',ax=ax, color='orange')
    
    _ = sns.despine()
    _ = ax.set_ylabel('')
    _ = ax.set_xlabel('Precision & Recall')
    if legend: _ = ax.legend(['Recall','Precision'])
    return ax

#####
#####

def prep_template(concept, db, fpd=None):
    with open(fpd+concept+'.json', mode='w') as f:
        f.write(
        '{\n'
        '  "target_rules": [\n'
        '    {\n'
        '      "literal" : "", \n'
        '      "category" : "'+concept+'",\n'
        '      "pattern" : [\n'
        '        {\n'
        '          "LOWER": {\n'
        '            "IN": [""]\n'
        '          }\n'
        '        },\n'
        '        {\n'
        '          "OP":"{,2}"\n'
        '        },\n'
        '        {\n'
        '          "LOWER": {\n'
        '            "IN": [""]\n'
        '          }\n'
        '        }\n'
        '      ]\n'
        '    },\n'
        '    {\n'
        '      "literal" : "", \n'
        '      "category" : "'+concept+'"\n'
        '    }\n'
        '  ]\n'
        '}\n'
        )

        literals = db.loc[db['label']==concept]['literal'].drop_duplicates().sort_values()
        for l in literals:
            f.write(l+'\n')
        print(len(literals),'\t', concept)
        
#####
#####
from .util import concept_ids

def add_concepts_in_checks( tbl, checks, mapping ):
    new_tbl = tbl.copy(deep=True)
    for chk,sx in mapping:
        new_tbl[sx] = pd.concat([ tbl[sx], checks[chk]], axis=1 ).max(1)
    return new_tbl

def add_concepts_in_hierarchy( tbl, hierarchy ):
    new_tbl = tbl.copy(deep=True)
    for sx in hierarchy.keys():
        new_tbl[concept_ids.get(sx,sx)] = tbl[[concept_ids[c] for c in hierarchy[sx]]].max(1)
    return new_tbl

def get_metrics( annotation, prediction, concepts ):
    
    metrics = pd.concat([get_stats(annotation[col], prediction[col], col) for col in concepts], axis=1).T
    
    metrics = metrics.astype({'TN':int,'FP':int,'FN':int,'TP':int,'supt':int})
    metrics[['Pr','Rc','F1','kappa']] = metrics[['Pr','Rc','F1','kappa']].round(2)
    
    return metrics

#####
#####

def plot_prec_rec_f1( metrics_tbl ):
    fig, ax = plt.subplots(1,3,figsize=(15,4), sharey=False, sharex=True)

    ax[0] = metrics_tbl['Pr'].hist(bins=20, grid=False, ax=ax[0])
    ax[0].set_title('precision')

    ax[1] = metrics_tbl['Rc'].hist(bins=20, grid=False, ax=ax[1])
    ax[1].set_title('recall')

    ax[2] = metrics_tbl['F1'].hist(bins=20, grid=False, ax=ax[2])
    ax[2].set_title('F1')

    ax[2].set_xlim(-0.05,1.05)
    sns.despine()