#!/usr/bin/env python
# -*- coding: latin-1 -*-
'''
docstring
'''
import re
import sys
import copy
import string
import textwrap
import datetime
import io

from Bio                    import Alphabet
from Bio                    import SeqIO
from Bio.Seq                import Seq
from Bio.SeqRecord          import SeqRecord
from Bio.SeqUtils.CheckSum  import seguid

__author__       ="Björn Johansson"
__date__         = ""
__copyright__    = "Copyright 2012, Björn Johansson"
__credits__      = ["Björn Johansson"]
__license__      = "BSD"
__version__      = "0.01"
__maintainer__   = "Björn Johansson"
__email__        = "bjorn_johansson@bio.uminho.pt"
__status__       = "Production" # "Prototype" # "Development" # "Production"

class FormattedRecord(SeqRecord):
    '''
    FormattedRecord(self,
                     record,
                     original_format="not defined",
                     raw_string="not set",
                     stamp = False,
                     circular = False,
                     *args, **kwargs):
    '''
    __version__="0.02"
    def __init__(self,
                 record,
                 original_format        = "not defined",
                 raw_string             = "not set",
                 stamp                  = False,
                 circular               = False,
                 filter                 = True,
                 *args, **kwargs):

        self.raw = raw_string.strip()
        self.original_format = original_format
        self.circular = circular
        self.warnings =""

        if isinstance(record, str):
            SeqRecord.__init__(self, Seq(record), *args, **kwargs)
        elif isinstance(record, Seq):
            SeqRecord.__init__(self, record, *args, **kwargs)
        elif isinstance(record, SeqRecord):
            for key, value in list(record.__dict__.items()):
                setattr(self, key, value )
        else:
            raise TypeError("the record property needs to be a string, a Seq object or a SeqRecord object")

        if not 'date' in self.annotations:
            self.annotations.update({"date": datetime.date.today().strftime("%d-%b-%Y").upper()})
        if filter:
            IUPAC_single_alphabet_letters = "ACBEDGFIHKJMLONQPSRUTWVYXZacbedgfihkjmlonqpsrutwvyxz"

            filtered_out = "".join([c for c in self.seq.tostring() if c not in IUPAC_single_alphabet_letters])

            if filtered_out:
                filtered = "".join([c for c in self.seq.tostring() if c in IUPAC_single_alphabet_letters])
                self.seq = Seq(filtered, self.seq.alphabet)
                self.filtered = filtered_out
                self.warnings += "non-permitted chars {0} were filtered from the sequence!\n".format(filtered_out)
            else:
                self.filtered = None

        if not isinstance(self.seq.alphabet, (Alphabet.ProteinAlphabet,Alphabet.DNAAlphabet,Alphabet.RNAAlphabet)):
            self.seq.alphabet = guess_alphabet(self.seq)
            self.guessed_alphabet = True
            self.warnings += str(self.seq.alphabet) + "alphabet guessed from sequence"
        else:
            self.guessed_alphabet = False

        pattern = "SEGUID\s(?P<SEGUID>\S{27})(?:\s|\n)TISTMP\s(?P<TISTMP>\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}\.\d*)"

        if stamp:
            try:
                parsed_seguid, parsed_timestamp = re.search(pattern, self.raw).group('SEGUID','TISTMP')
            except AttributeError:
                timestamp = " SEGUID %s\nTISTMP %s" % (seguid(self.seq), datetime.datetime.now().isoformat())
            else:
                timestamp = " SEGUID %s\nTISTMP %s" % (parsed_seguid, parsed_timestamp)


            if not self.description:
                self.description = timestamp
            elif not re.search(pattern, self.description):
                self.description += timestamp

        if self.id in ("","."):
            self.id = self.name

        if self.description ==".":
            self.description = ""

    def format(self,f):
        if f == "genbank" or f=="gb":
            s = SeqRecord.format(self,f)
            if self.circular:
                return s[:55]+"circular"+s[63:]
            else:
                return s[:55]+"linear"+s[61:]
        else:
            return SeqRecord.format(self,f)


    def verify(self):
        current_seguid = seguid(self.seq)
        parsed_seguid  = re.search("SEGUID\s(?P<SEGUID>\S{27})", self.description).group('SEGUID')
        if current_seguid != parsed_seguid:
            return False
        return True

    def __str__(self):
        lines =[]
        lines.append("Circular: {0}".format(self.circular))
        return "\n".join(lines)+"\n"+SeqRecord.__str__(self)

    def __add__(self,other):
        answer = FormattedRecord(SeqRecord.__add__(self,other))
        return answer

    def __radd__(self,other):
        answer = FormattedRecord(SeqRecord.__radd__(self,other))
        return answer
def parse_seqs(rawstring, stamp = False, filter = True):
    '''
    parse_seqs(rawstring, stamp = False)

    rawstring is a string containing one or more
    sequences in EMBL, GENBANK, or FASTA format
    mixed formats are allowed.

    The function returns a list of FormattedRecord objects
    '''
    from Bio.GenBank import RecordParser
    pattern =  r"(?:>.+\n^(?:^[^>]+?)(?=\n\n|>|LOCUS|ID))|(?:(?:LOCUS|ID)(?:(?:.|\n)+?)^//)"
    rawseqs = re.findall(pattern,textwrap.dedent(rawstring+"\n\n"),re.MULTILINE)
    sequences=[]

    while rawseqs:
        circular = False
        rawseq = rawseqs.pop(0)
        handle = io.StringIO(rawseq)
        try:
            parsed = next(SeqIO.parse(handle, "embl"))
            original_format = "embl"
            if "circular" in rawseq.splitlines()[0]:
                circular = True
        except StopIteration:
            handle.seek(0)
            try:
                parsed = next(SeqIO.parse(handle, "genbank"))
                original_format = "genbank"
                handle.seek(0)
                parser = RecordParser()
                residue_type = parser.parse(handle).residue_type
                if "circular" in residue_type:
                    circular = True
            except StopIteration:
                handle.seek(0)
                try:
                    parsed = next(SeqIO.parse(handle, "fasta"))
                    original_format = "fasta"
                    if "circular" in rawseq.splitlines()[0]:
                        circular = True
                except StopIteration:
                    continue
        sequences.append(FormattedRecord(  parsed,
                                           original_format      = original_format,
                                           raw_string           = rawseq,
                                           stamp                = stamp,
                                           circular             = circular,
                                           filter               = filter))
        handle.close()

    return sequences

def guess_alphabet(sequence):
    '''
    guess_alphabet(sequence)

    '''
    import string
    import warnings

    from Bio.Alphabet       import SingleLetterAlphabet
    from Bio.Alphabet       import NucleotideAlphabet
    from Bio.Alphabet       import ProteinAlphabet
    from Bio.Alphabet.IUPAC import extended_protein
    from Bio.Alphabet.IUPAC import protein
    from Bio.Alphabet.IUPAC import ambiguous_dna
    from Bio.Alphabet.IUPAC import unambiguous_dna
    from Bio.Alphabet.IUPAC import extended_dna
    from Bio.Alphabet.IUPAC import ambiguous_rna
    from Bio.Alphabet.IUPAC import unambiguous_rna

    from Bio.Seq            import Seq
    from Bio.SeqRecord      import SeqRecord

    if isinstance(sequence, Seq):
        sequence = sequence.tostring()

    elif isinstance(sequence, SeqRecord):
        sequence = sequence.seq.tostring()

    elif not isinstance(sequence, str):
        sequence = str(sequence)
        warnings.warn("Input is not string, unicode string, Seq or SeqRecord objects!")

    if len(sequence)<1:
        return SingleLetterAlphabet()

    for c in sequence:
        if c not in string.printable:
            return SingleLetterAlphabet()

    xp = set(extended_protein.letters)
    pr = set(protein.letters)

    ad = set(ambiguous_dna.letters)
    ud = set(unambiguous_dna.letters)
    ed = set(extended_dna.letters)

    ar = set(ambiguous_rna.letters)
    ur = set(unambiguous_rna.letters)

    all = xp|pr|ad|ud|ed|ar|ur

    sequence_chars = set(sequence.upper())

    if sequence_chars - all - set(string.punctuation+string.whitespace):
        return SingleLetterAlphabet()

    nucleic_count = 0

    for letter in "GATCUNgatcun":
        nucleic_count += sequence.count(letter)

    if float(nucleic_count) / float(len(sequence)) >= 0.9: # DNA or RNA
        if 'T' in sequence_chars and 'U' in sequence_chars:
            alphabet = NucleotideAlphabet()
        elif not sequence_chars-ud:
            alphabet = unambiguous_dna
        elif not sequence_chars-ad :
            alphabet = ambiguous_dna
        elif not sequence_chars-ed:
            alphabet = extended_dna
        elif not sequence_chars-ur:
            alphabet = unambiguous_rna
        elif not sequence_chars-ar:
            alphabet = extended_rna
        else:
            alphabet = NucleotideAlphabet()
    else:
        threecode = ['ALA', 'ASX', 'CYS', 'ASP','GLU', 'PHE', 'GLY', 'HIS',
                     'ILE', 'LYS', 'LEU', 'MET','ASN', 'PRO', 'GLN', 'ARG',
                     'SER', 'THR', 'VAL', 'TRP','TYR', 'GLX', 'XAA', 'TER',
                     'SEL', 'PYL', 'XLE']
        tc=set(threecode)
        three_letter_alphabet = set( [ sequence[i:i+3] for i in range(0,len(sequence),3)] )
        if not three_letter_alphabet - tc:
            alphabet = "three letter code"
        elif sequence_chars - pr:
            alphabet = protein
        elif sequence_chars - xp:
            alphabet = extended_protein
        else:
            alphabet = ProteinAlphabet()
    return alphabet

if __name__=="__main__":
    pass

    from Bio.Alphabet import DNAAlphabet

    with open('RefDataBjorn.fas', 'r') as f:
        raw = f.read()

    seqs = parse_seqs(raw, stamp=False, filter=False)
    #seqs = list(SeqIO.parse("RefDataBjorn.fas","fasta",DNAAlphabet()))

    assert len(seqs) == 771
    assert list(set([len (a) for a in seqs])) == [901]
    for i,s in enumerate(seqs):
        a = s.description
        b = a.split("|")
        c =  "|".join([b[0],b[1],b[3]])
        s.id = b[2].replace(" ","_")+"_"+str(i)
        s.description = ""
        if b[3]=="Zenion hololepis":
            s.id = b[3].replace(" ","_")+"_"+str(i)
        s.seq.alphabet = DNAAlphabet()

    SeqIO.write(seqs, "myfile1.txt", "nexus")
