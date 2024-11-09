#!/usr/bin/env python
# coding: utf-8

# In[ ]:


import spacy
import pandas as pd
import os
import medspacy
from medspacy.ner import TargetRule
from medspacy.visualization import visualize_ent, visualize_dep

from escribe.test_patterns import *
from escribe.util import all_labels, subset_tables_to_equal_dims # we prbably don't need subset_tables_to_equal_dims

pd.options.display.max_rows    = 150
pd.options.display.min_rows    = 150
pd.options.display.max_columns = 150

get_ipython().run_line_magic('load_ext', 'autoreload')
get_ipython().run_line_magic('autoreload', '2')


# In[ ]:


# Main function:
def run_NLP_on_records_separate_concepts( nlp, tbl, cols, context=True, concepts_root_dir="/home/cfrydman/NLP/Juan_nlp_paper/CSJDM/json_patterns_separate_concepts/concepts/dev_clara/", junk_substring=None ):
    """
    Main function to run NLP pipeline on table of notes, with or without context awareness, and return results.

    Args:
        nlp (XXX): nlp object.
        tbl (pd.DataFrame): pandas dataframe containing one or more columns with documents to analyze.
        cols (list): list of columns of interest to analyze in tbl. These are the columns that contain the documents we want to phenotype
        context (bool): if True, we return only those phenotypes that were detected in non-negated, hypothetical, uncertain or historical contexts, or relating to other individuals.
        concepts_root_dir: root directory with all NER concept files
        junk_substring (str): optional, string to signal "cutting" documents short (to filter out junk substrings)
    Returns:
        pd.DataFrame: a dataframe with the detected concepts, containing 4 columns: (1) 'i', for the row index in the original input table where the document is
                                                                                    (2) 'field' for the column name in the original input table where the document is
                                                                                    (3) 'ent' for the recognized span
                                                                                    (4) 'concept' for the name of the concept detected
    """
    
    tbl = tbl.fillna('')
    pt_ents = []
    concept_list=os.listdir(concepts_root_dir) # Get a list of the concepts we're working with (symptoms)
    
    for individual_concept in concept_list: # Run independently on each concept so that they don't compete        
        if not individual_concept.startswith('.'):
            #concepts = load_concepts( directory = (concepts_root_dir+individual_concept), nlp=nlp,  ) # This will be just 1 concept
            concept_directory=concepts_root_dir+str(individual_concept+"/")
            print("Loading concepts from "+ str(concept_directory))
            rules_in_tbl = add_json_patterns_from_dir( direc = concept_directory, nlp_to_update = nlp)
            for i in tbl.index:
                for field in cols:
                    medical_text=tbl.loc[i, field]
                    if junk_substring and junk_substring in medical_text:
                        medical_text = medical_text[:medical_text.index(junk_substring)]
                    medical_text_filtered_conformed=' '.join(medical_text.split())
                    medical_text_filtered_conformed=medical_text_filtered_conformed.lower()
                    doc = nlp(medical_text_filtered_conformed)
                    for ent in doc.ents:
                        if context:
                            if not ent._.is_family:
                                if not ent._.is_hypothetical:
                                    if not ent._.is_negated:
                                        if not ent._.is_historical:
                                            if not ent._.is_uncertain:
                                                pt_ents.append( [i, field, ent] )

                        else:
                            pt_ents.append( [i, field, ent] )

    pt_ents = pd.DataFrame( pt_ents, columns=['i','field', 'ent'])
    # Add concept labels:
    pt_ents['concept'] = [e.label_ for e in pt_ents['ent']]
    return pt_ents


# # Set up pipeline:

# In[ ]:


from escribe.default_nlp import nlp, add_json_patterns_from_dir, run_NLP_on_records
nlp.get_pipe('medspacy_target_matcher').rules


# # Load data and apply pipeline:

# In[ ]:


# Load data:
ehr_text1 = pd.read_csv(notes_file , sep='|', index_col=0 ).fillna('') # modulate appropriately

# Define fields to apply NLP algorithm to:
fields_to_search = [ 'subjetivo', 'objetivo', 'analisis_y_conducta' ] # example, replace with your own columns of interest

# Apply pipeline
notes_ents1 = run_NLP_on_records_separate_concepts(   nlp,
                                   ehr_text1, 
                                   fields_to_search,
                                   context=True, # Set to false to scan for presence of concepts mentioned in any context 
                                    concepts_root_dir="/home/cfrydman/NLP/Juan_nlp_paper/CSJDM/json_patterns_separate_concepts/concepts/dev_clara/")



# In[ ]:




