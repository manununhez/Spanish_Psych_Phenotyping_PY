import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

from escribe.test_patterns import get_stats
from escribe.util_clara import symptom_translation_dict


#### Find support on doc set functions ####

def match_rules_on_doc_set( rules_concept_tbl, doc_set, nlp_ ):
    rules_in_set = rules_concept_tbl.copy(deep=True)
    rules_in_set['matches'] = ''

    for i,rule in rules_in_set.iterrows():

        print('--------\n',i)
        nlp_ = replace_matcher_with_new_rule( rule['target_rules'], nlp_ )
        rule['matches'] = get_supporting_docs( doc_set  , nlp_ )
        print( len(rule['matches']),':',rule['matches'] )

    return rules_in_set

def sample_of_docs_to_get_support( rules_in_set, doc_set, reps, sample_range ):
    for i in sample_range:
        for j in range(reps):
            k = str(i)+' '+str(j)
            doc_sample = doc_set.sample(i).sort_index()
            rules_in_set['sample '+k] = ''

            for l,pattern in rules_in_set.iterrows():
                rules_in_set.loc[l,'sample '+k] = int(doc_sample.index.isin(pattern['matches']).sum()>0)

            print(' - ',i,j, rules_in_set['sample '+k].mean().round(2))
            print(rules_in_set['sample '+k].value_counts().sort_index().to_string())
            print()
    return rules_in_set

def pivot_matches_to_docs_x_rules( rules_in_set, doc_set ):
    # prep to pivot
    rules_in_set_ = rules_in_set[['category','literal','matches']].explode('matches')

    # make sure to include all rules
    rules_in_set_ = rules_in_set_.fillna(-1)
    rules_in_set_ = rules_in_set_.groupby(['category','literal','matches']).size().unstack()
    rules_in_set_ = rules_in_set_.drop(columns=-1)

    # make sure to include all documents (BASED ON INDEX)
    rules_in_set_[[i for i in doc_set.index if i not in rules_in_set_.columns]] = 0

    # fix format
    rules_in_set_ = rules_in_set_.T.sort_index().fillna(0).astype(int)
    return rules_in_set_

#### Prepping functions ####

def replace_matcher_with_new_rule( rule, nlp_ ):
    target_matcher = nlp_.replace_pipe('medspacy_target_matcher', 'medspacy_target_matcher', config={'rules':None})
    target_matcher.add( rule )
    _ = [print( rule.category, '-->', rule.literal ) for rule in nlp_.get_pipe('medspacy_target_matcher').rules]
    return nlp_

def get_supporting_docs( doc_set, nlp_ ):
    return doc_set.loc[[len(nlp_(text).ents)>0 for text in doc_set['text']]].index.tolist()

'''
def run_concept_on_sentences( doc_set, concept, nlp_ ):
    concept_tbl = doc_set[[concept]].copy(deep=True).rename(columns={concept:'true'})
    concept_tbl['ents'] = [nlp_(text).ents for text in doc_set['text']]
    concept_tbl['pred'] = (concept_tbl['ents'].str.len()>0).astype(int)
    return concept_tbl
'''

#### Saturation curve functions ####

def saturation_curve_concept( concept, concepts_rules_devset_samples, gs_pred_by_concept_rule, documents_GS ):
    concept_stats = []
    rules_in_concept = concepts_rules_devset_samples.loc[concepts_rules_devset_samples['category']==concept]

    # iterate over all samples K
    for i in range(100,1700,100):
        for j in range(5):
            k = str(i)+' '+str(j)

            # identify the list of rules for the concept that were selected in each sample k
            supported_rules = rules_in_concept.loc[ rules_in_concept['sample '+k]==1 ]['literal'].tolist()

            # can I predict the concept in each document of the GS set? 
                # from the rules for the concept that were found in the sample k
            gs_pred_by_concept = (gs_pred_by_concept_rule[concept][supported_rules].sum(1)>0).astype(int)
            
            # compare the prediction with the annotation to get the stats for sample k
            sample_stats = get_stats( documents_GS[concept], gs_pred_by_concept , k )

            # collect additional info
            sample_stats[ 'N_docs'] = i
            sample_stats[    'rep'] = j
            sample_stats['n_rules'] = len(supported_rules)

            concept_stats.append(sample_stats)

    concept_stats = pd.concat(concept_stats, axis=1).T
    return concept_stats

def plot_saturation_curves(concept_list, concepts_rules_devset_samples, gs_pred_by_concept_rule, documents_GS,
                           n_ver, n_hor, metric='Rc', figsize=(15,15), english_name=False):
    # prep canvas
    fig, ax = plt.subplots( n_ver, n_hor, figsize=figsize, sharex=True, sharey=True)
    ax = ax.flatten()

    for i in range(len(ax)):
        concept = concept_list[i]
        satur_curve_ = saturation_curve_concept( concept = concept, 
                           concepts_rules_devset_samples = concepts_rules_devset_samples, 
                                 gs_pred_by_concept_rule = gs_pred_by_concept_rule,
                                            documents_GS = documents_GS)
        
        # plot
        ax[i] = sns.lineplot( data=satur_curve_, x="N_docs", y=metric, ax=ax[i] )
        if(english_name):
            if concept in symptom_translation_dict:
                concept_english=symptom_translation_dict[concept]
                _ = ax[i].set_title(concept_english, {'fontsize': 10})
            else:
                _ = ax[i].set_title(concept)
        else:
            _ = ax[i].set_title(concept)

    _ = ax[0].set_ylim(-0.05,1.05)
    sns.despine()

    return fig, ax