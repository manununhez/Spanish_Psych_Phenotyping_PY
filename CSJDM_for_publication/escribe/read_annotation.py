import pandas as pd

def process_tsv_file( filename ):
    tsv_file = read_tsv(filename)

    ents_tbl_all = collect_entities_from_tsv(  tsv_file )
    ents_informa = collect_entity_information( tsv_file, ents_tbl_all )

    ents_all_info = pd.concat([ents_tbl_all, ents_informa], axis=1)

    col_order = ['entry','label','start_tk','end_tk','start_ch','end_ch','ent_id','text','tokens']

    ents_all_info = ents_all_info[col_order].sort_values(['entry','start_tk','end_tk'])
    
    return tsv_file, ents_all_info

def read_tsv( filename ):
    labels  = []
    documents = []
    document  = '' # for first document
    
    with open( filename, 'r', encoding='utf-8' ) as f:
        for l in f.readlines():
            l = l.strip("\n")

            if len(l)==0:
                continue

            elif l.startswith('#FORMAT='):
                print("File Format:", l[8:])

            elif l.startswith('#T_CH=') or l.startswith('#T_SP='):
                label = l[6:]
                label = label.split("|")[1]
                labels.append( label )

            elif l.startswith('#Text='):
                # condition for first document:
                if document != '': 
                    document.make_table()
                    documents.append( document )
                document = Document( l[6:], labels )

            else:
                l = l.strip("\t").split("\t")
                document.add_token( l )

    # Append the last document
    document.make_table()
    documents.append( document )
    print("Number of documents loaded:", len(documents))

    return documents

class Document:
    
    def __init__( self, text, labels = [] ):
        self.size = 0
        self.tokens = []
        self.posits = []

        self.text   =  text
        self.lbl_or =  labels
        self.labels = {label:[] for label in labels}

    def add_token( self, token_elements ):
        if token_elements[0].split('-')[1] == "1":
            self.zero = int( token_elements[1].split('-')[0] )
        self.posits.append( [ int(x)-self.zero for x in 
                             token_elements[1].split('-') ] ) 
        self.tokens.append(  token_elements[2] )
        for i in range(3,len(token_elements)):
            labeled = token_elements[i]
            self.labels[ self.lbl_or[i-3] ].append( labeled )
        self.size += 1
        
    def make_table( self ):
        self.table = pd.DataFrame( [ self.posits[i] + [self.tokens[i]] + 
                        [self.labels[lb][i] for lb in self.lbl_or] for i in range(self.size)], 
                                    columns= ['first','last','token']+self.lbl_or
                                 ).set_index(['first','last','token'])
        
    def __repr__( self ):
        return self.text

################################
### COLLECT CONCEPT EXAMPLES ###
################################

def collect_entities_from_column(series):
    ents, pos, hold = [], 0, '_'
    
    for label in series:

        if label == '_':
            if label != hold and hold != '_':
                ents.append( (hold, start, pos-1) )

        else:
            if '[' not in label:
                ents.append( (label, pos, pos) )
                label = '_'
            elif label != hold:
                if hold != '_':
                    ents.append( (hold, start, pos-1) )
                start = pos

        pos += 1
        hold = label

    if hold != '_':
        ents.append( (hold, start, pos-1) )

    return ents

def collect_entities_from_document_tbl( sent_tbl ):
    
    ents_sent = []
    
    for col in sent_tbl.columns:
        ents_col     = collect_entities_from_column( sent_tbl[col] )
        
        ents_col_tbl = pd.DataFrame( ents_col, columns=['ent_id','start_tk','end_tk'])
        ents_col_tbl = ents_col_tbl.assign( label=col )
        
        ents_sent.append( ents_col_tbl ) 
    
    return ents_sent

def collect_entities_from_tsv(tsv_file):
    ents_tbl_all = pd.concat( [pd.concat( 
                                  collect_entities_from_document_tbl( tsv_file[i].table ) ).assign( entry=i+1 ) 
                              for i in range(len(tsv_file))] )
    return ents_tbl_all.reset_index(drop=True)

def collect_entity_information( tsv_file, ents_tbl ):
    ent_annot = []
    
    for i in range(ents_tbl.shape[0]):
        ent = ents_tbl.loc[i]

        document = tsv_file[ent['entry']-1]
        sent_tbl = document.table.reset_index()
        ent_sect = sent_tbl.loc[ent['start_tk']:ent['end_tk']]

        first = ent_sect['first'].min()
        last  = ent_sect[ 'last'].max()

        ent_annot.append([first, last, document.text[first:last], ent_sect['token'].tolist()])

    ent_annot_tbl = pd.DataFrame( ent_annot, columns=['start_ch','end_ch','text','tokens'])
    return ent_annot_tbl

##############################
### MERGE CONCEPT EXAMPLES ###
##############################

def merge_entities_from_tsvs( maria_ents, daniel_ents, tsv_docs ):
    
    both_ents = merge_annotations(maria_ents, daniel_ents)

    both_ents_merge = both_ents.groupby(['entry','label']).apply( merge_annotations_same_label )
    both_ents_merge = both_ents_merge.reset_index().drop(columns='level_2')

    both_ents_merge_info = pd.concat([both_ents_merge, collect_entity_information( tsv_docs, both_ents_merge )], axis=1)
    both_ents_merge_info = both_ents_merge_info.sort_values(['entry','start_tk','end_tk'])

    both_ents_merge_info_ovlp = both_ents_merge_info.groupby('entry').apply( how_many_overlaps ).reset_index(drop=True)
    
    return format_concept_table( both_ents_merge_info_ovlp )


def merge_annotations( maria, daniel ):
    daniel_ = daniel.copy( deep=True ).assign( daniel='X' ).rename( columns={'ent_id':'ent_id_dan'}).drop( columns='tokens' )
    maria_  =  maria.copy( deep=True ).assign(  maria='X' ).rename( columns={'ent_id':'ent_id_mar'}).drop( columns='tokens' )

    tbl = pd.merge( maria_, daniel_, how='outer' ).fillna('')
    tbl = tbl.sort_values(['entry','start_tk','end_tk']).reset_index(drop=True)
    
    return tbl

def merge_annotations_same_label( tbl ):
    if isinstance( tbl, pd.Series ):
        return tbl[['start_tk', 'end_tk', 'daniel', 'maria', 'ent_id_dan', 'ent_id_mar']]
    
    i = 0
    ents = [i]
    final_intervals = []

    while i < tbl.shape[0]-1:
        i += 1
        if tbl.iloc[i]['start_tk'] <= tbl.iloc[i-1]['end_tk']:
            ents.append(i)
        else:
            final_intervals.append(ents)
            ents = [i]
    final_intervals.append(ents)

    result = pd.DataFrame([(tbl.iloc[interval]['start_tk'].min(),
                            tbl.iloc[interval]['end_tk'].max(),
                    ''.join(tbl.iloc[interval]['daniel']),
                    ''.join(tbl.iloc[interval]['maria']),
                   ';'.join(tbl.iloc[interval]['ent_id_dan']),
                   ';'.join(tbl.iloc[interval]['ent_id_mar'])) for interval in final_intervals],
                         columns=['start_tk', 'end_tk', 'daniel', 'maria', 'ent_id_dan', 'ent_id_mar'])
    return result

def how_many_overlaps( tb ):

    overlaps_counts = []
    for i in tb.index:
        overlaps_i = 0
        for j in tb.index:
            if i!=j:
                if   (tb.loc[j,  'end_tk'] >= tb.loc[i,'start_tk']) and (tb.loc[j,  'end_tk'] <= tb.loc[i,'end_tk']):
                    overlaps_i += 1
                elif (tb.loc[j,'start_tk'] >= tb.loc[i,'start_tk']) and (tb.loc[j,'start_tk'] <= tb.loc[i,'end_tk']):
                    overlaps_i += 1
                elif (tb.loc[j,'start_tk'] <= tb.loc[i,'start_tk']) and (tb.loc[j,  'end_tk'] >= tb.loc[i,'end_tk']):
                    overlaps_i += 1
                elif (tb.loc[j,'start_tk'] >= tb.loc[i,'start_tk']) and (tb.loc[j,  'end_tk'] <= tb.loc[i,'end_tk']):
                    overlaps_i += 1
        overlaps_counts.append( overlaps_i )
        
    return tb.assign( overlaps = overlaps_counts )

def format_concept_table(tbl):

    tbl = tbl.fillna('')
    
    tbl['literal'] = tbl['text'].str.strip().str.lower()
    
    tbl[['start_tk', 'end_tk']] = tbl[['start_tk','end_tk']].astype(int)
    
    tbl[['daniel', 'maria']] = tbl[['daniel','maria']].replace('XX','X')

    tbl['ent_id_dan'] = tbl['ent_id_dan'].str.strip(';')
    tbl['ent_id_mar'] = tbl['ent_id_mar'].str.strip(';')

    tbl = tbl[['entry','label','literal',
               'start_tk','end_tk','overlaps','daniel','maria',
               'start_ch','end_ch','ent_id_dan','ent_id_mar','text','tokens']]

    return tbl
