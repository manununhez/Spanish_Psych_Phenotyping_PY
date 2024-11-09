import pandas as pd

concept_ids = pd.read_table('annotation/concept_label_dict.tsv', index_col=0)['ID'].to_dict()

all_labels = list(set(concept_ids.values()))
all_labels.sort()

gs_map = pd.read_table('annotation/selection_of_Gold_Standard_sentences.csv')
gs_map = gs_map.assign(set='GS')


def fill_in_values_below(series):
    ser = series.copy(deep=True)
    for i in ser.index:
        if not isinstance( ser.loc[i], float ):
            cur = ser.loc[i]
        else:
            ser.loc[i] = cur
    return ser

def subset_tables_to_equal_dims( tbl1, tbl2 ):
    
    # patients in both
    print( "index not in tbl1:\t", [i for i in tbl2.index    if i not in tbl1.index  ])
    print( "index not in tbl2:\t", [i for i in tbl1.index    if i not in tbl2.index  ])
    idx = list(set( tbl1.index ).intersection(set( tbl2.index )))
    idx.sort()
    print( "indices in both tables:\t", len(idx), "\n")
    
    # concepts in both
    print( "column not in tbl1:\t", [c for c in tbl2.columns if c not in tbl1.columns])
    print( "column not in tbl2:\t", [c for c in tbl1.columns if c not in tbl2.columns])
    col = list(set(tbl1.columns).intersection(set(tbl2.columns)))
    col.sort()
    print( "columns in both tables:\t", len(col), "\n")
    
    # subset tables
    tbl1 = tbl1.loc[ idx, col ]
    tbl2 = tbl2.loc[ idx, col ]

    print(tbl1.shape, tbl2.shape)
    return tbl1, tbl2