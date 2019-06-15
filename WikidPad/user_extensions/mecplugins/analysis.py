# http://biopython.org/DIST/docs/cookbook/Restriction.html#mozTocId343319
# This will create a RestrictionBatch with the all enzymes which possess a supplier ['A','E','G','I','K','J','M','N','S','R','U'].

import sys
import io
from Bio.Seq            import Seq
from Bio.Alphabet.IUPAC import IUPACAmbiguousDNA
from Bio.Restriction    import *
from Bio.SeqRecord      import SeqRecord
from functools import reduce

def restrictionanalyserecords(sequencerecords,rb=RestrictionBatch(first=[],suppliers=['E','I','K','J','M','N','S','R'])):
    
    import textwrap
    
    analistnocut  = []
    analistunique = []
    analistcut = []
    analisttwice = []

    for formatseq in sequencerecords:

        sequence = formatseq.seq

        ana = Analysis(rb, sequence, linear=True)

        analistnocut.append(    RestrictionBatch(   ana.without_site()     ))
        analistunique.append(   RestrictionBatch(   ana.with_N_sites(1)    ))
        analisttwice.append(    RestrictionBatch(   ana.with_N_sites(2)    ))
        analistcut.append(      RestrictionBatch(   ana.with_sites()       ))

    numberofsequences = len(sequencerecords)

    nocutinanybatch       = reduce(lambda x,y:x&y,analistnocut)
    uniqueinallbatch      = reduce(lambda x,y:x&y,analistunique)
    twooinanybatch        = reduce(lambda x,y:x&y,analisttwice)
    cutsinanybatch        = reduce(lambda x,y:x&y,analistcut)

    unique = nocutters = ''

    for e in nocutinanybatch.elements():        nocutters+=e+' '
    for e in uniqueinallbatch.elements():       unique+=e+' '

    if  numberofsequences>1:

        uniqueinlast = twiceinlast = ''

        uniqueinlastbatch     = reduce(lambda x,y:x&y,analistnocut[:-1])&analistunique[-1]
        twiceinlastbatch      = reduce(lambda x,y:x&y,analistnocut[:-1])&analisttwice[-1]


        for e in uniqueinlastbatch.elements():
            uniqueinlast+=e+' '
        for e in twiceinlastbatch.elements():
            twiceinlast+=e+' '

        result_text = textwrap.dedent('''
                                      
        Restriction analysis of %s sequences
        ------------------------------------
        The following enzymes cut once in each sequence:
        
        %s
        
        The following enzymes do not cut in any sequence:
        
        %s
        
        The following enzymes cuts once in the last sequence and are absent in the preceding sequence(s):
        
        %s
        
        The following enzymes cut twice in the last sequence and are absent in the preceding sequence(s):
        
        %s''' % ( numberofsequences,unique,nocutters,uniqueinlast,twiceinlast))

    else:

        twoormore = ''

        bat = cutsinanybatch - uniqueinallbatch

        for e in bat.elements(): 
            twoormore +=e+' '
            
        result_text = textwrap.dedent('''
                                      
        Restriction analysis of a single sequence
        -----------------------------------------
        The following enzymes cut once:
        
        %s
        
        The following enzymes are absent:
        
        %s
        
        The following enzymes cut twice or more:
        
        %s''' % (unique, nocutters, twoormore))


    return result_text

if __name__=="__main__":

    from .parse_string import parse_seqs
    string='''
    
    LOCUS       ScCYC1                   330 bp    DNA              UNK 01-JAN-1980
    DEFINITION  ScCYC1
    ACCESSION   ScCYC1
    VERSION     ScCYC1
    KEYWORDS    .
    SOURCE      .
      ORGANISM  .
                .
    FEATURES             Location/Qualifiers
    ORIGIN
            1 ATGACTGAAT TCAAGGCCGG TTCTGCTAAG AAAGGTGCTA CACTTTTCAA GACTAGATGT
           61 CTACAATGCC ACACCGTGGA AAAGGGTGGC CCACATAAGG TTGGTCCAAA CTTGCATGGT
          121 ATCTTTGGCA GACACTCTGG TCAAGCTGAA GGGTATTCGT ACACAGATGC CAATATCAAG
          181 AAAAACGTGT TGTGGGACGA AAATAACATG TCAGAGTACT TGACTAACCC AAAGAAATAT
          241 ATTCCTGGTA CCAAGATGGC CTTTGGTGGG TTGAAGAAGG AAAAAGACAG AAACGACTTA
          301 ATTACCTACT TGAAAAAAGC CTGTGAGTAA
    //
    
    '''

    new_sequences = parse_seqs(string)

    print(restrictionanalyserecords(new_sequences))