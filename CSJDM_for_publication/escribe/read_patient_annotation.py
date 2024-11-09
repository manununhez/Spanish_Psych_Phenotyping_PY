import pandas as pd
from .util import concept_ids, all_labels, fill_in_values_below

def load_patient_annotation( filepath ):
    pt_tbl = pd.read_table(filepath)

    # fix patient info
    pt_tbl["patient"] = fill_in_values_below( pt_tbl["patient"] )
    pt_tbl["patient"] = pt_tbl["patient"].str.extract(r'(CSJDM-[0-9]+|HOMO-[0-9]+|\b[0-9]{3}-[0-9]+| \b[0-9]{4}\b)')[0].str.strip()

    # fix index
    pt_tbl['level'] = pt_tbl['level'].fillna('NA')
    pt_tbl = pt_tbl.set_index(['patient','level'])

    # rename columns
    pt_tbl = pt_tbl.rename( columns= concept_ids )
    pt_tbl.loc[:,[c for c in all_labels if c not in pt_tbl.columns]] = ''

    pt_tbl = pt_tbl.fillna('')
    return pt_tbl[all_labels]


def format_patient_annotation( pt_tbl_load, relevance_dict=None, binary=None ):
    
    # identify concepts with any mention
    pt_tbl = (pt_tbl_load!='').astype(int)

    # group levels by relevance from dict
    if isinstance( relevance_dict, dict):
        pt_tbl = pt_tbl.reset_index()
        pt_tbl['relevant'] = [relevance_dict[x] for x in pt_tbl['level']]
        pt_tbl = pt_tbl.drop(columns='level').groupby(['patient','relevant']).max()
    
        # select only the binary level
        if isinstance( binary, str ) and binary in pt_tbl.reset_index()['relevant'].unique():
            pt_tbl = pt_tbl.reset_index().set_index(['relevant','patient']).loc[binary]
    
    # return presence of the concept only
    else:
        pt_tbl = pt_tbl.reset_index().drop(columns='level').groupby('patient').max()

    return pt_tbl.sort_index()


