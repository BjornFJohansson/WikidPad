def seq1(seq):
    """Turn a three letter code protein sequence into one with one letter code.

    The single input argument 'seq' should be a protein sequence using single
    letter codes, as a python string.

    This function returns the amino acid sequence as a string using the one
    letter amino acid codes. Output follows the IUPAC standard (including
    ambiguous characters B for "Asx", J for "Xle" and X for "Xaa", and also U
    for "Sel" and O for "Pyl") plus "Ter" for a terminator given as an asterisk.

    Any unknown
    character (including possible gap characters), is changed into 'Xaa'.

    e.g.
    >>> from Bio.SeqUtils import seq3
    >>> seq3("MAIVMGRWKGAR*")
    'MetAlaIleValMetGlyArgTrpLysGlyAlaArgTer'

    This function was inspired by BioPerl's seq3.
    """
    threecode = {'Ala':'A', 'Asx':'B', 'Cys':'C', 'Asp':'D',
                 'Glu':'E', 'Phe':'F', 'Gly':'G', 'His':'H',
                 'Ile':'I', 'Lys':'K', 'Leu':'L', 'Met':'M',
                 'Asn':'N', 'Pro':'P', 'Gln':'Q', 'Arg':'R',
                 'Ser':'S', 'Thr':'T', 'Val':'V', 'Trp':'W',
                 'Tyr':'Y', 'Glx':'Z', 'Xaa':'X', 'Ter':'*',
                 'Sel':'U', 'Pyl':'O', 'Xle':'J'
                 }

    nr_of_codons = int(len(seq)/3)
    sequence = [seq[i*3:i*3+3].title() for i in range(nr_of_codons)]
    padding = " "*2
    return padding.join([threecode.get(aa,'X') for aa in sequence])


if __name__=="__main__":
    print("MAIVMGRWKGAR*")
    print(seq1("MetAlaIleValMetGlyArgTrpLysGlyAlaArgTer"))
    print(seq1("METALAILEVALMETGLYARGTRPLYSGLYALAARGTER"))

