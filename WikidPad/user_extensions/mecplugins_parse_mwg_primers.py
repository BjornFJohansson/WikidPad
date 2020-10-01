#!/usr/bin/env python
# -*- coding: utf-8 -*-
################################################################################################
#                              __  ____          _______              _
#                             |  \/  \ \        / / ____|            (_)
#  _ __   __ _ _ __ ___  ___  | \  / |\ \  /\  / / |  __   _ __  _ __ _ _ __ ___   ___ _ __ ___
# | '_ \ / _` | '__/ __|/ _ \ | |\/| | \ \/  \/ /| | |_ | | '_ \| '__| | '_ ` _ \ / _ \ '__/ __|
# | |_) | (_| | |  \__ \  __/ | |  | |  \  /\  / | |__| | | |_) | |  | | | | | | |  __/ |  \__ \
# | .__/ \__,_|_|  |___/\___| |_|  |_|   \/  \/   \_____| | .__/|_|  |_|_| |_| |_|\___|_|  |___/
# | |                                                     | |
# |_|                                                     |_|
################################################################################################

WIKIDPAD_PLUGIN = (("MenuFunctions",1), ("ToolbarFunctions",1))

from Bio                            import SeqIO
from os                             import linesep
from io                             import StringIO
from Bio.Seq                        import Seq
from Bio.SeqRecord                  import SeqRecord

def describeMenuItems(wiki):
    return (
            (mwgtofasta,_("mecplugins|DNA Sequence Tools|MWG primers to fasta format") +  "\t", _("mwgtofasta")),
            (addtolist,_("mecplugins|DNA Sequence Tools|add primers to list") +  "\t", _("addtolist")),
            )
def empty(wiki, evt):
    pass

def describeToolbarItems(wiki):
    return ()

def mwgtofasta(wiki, evt):

    from pyparsing import Word, Literal, printables, LineStart, SkipTo, Combine

    raw_string = wiki.getActiveEditor().GetSelectedText()
    start, end = wiki.getActiveEditor().GetSelection()

    dataStart = end - start

    wiki.getActiveEditor().SetSelectionByCharPos(start, start+dataStart)

    name        =  Word(printables).setResultsName("name")
    seq_start   =  Literal("5'").suppress()
    seq_stop    =  Literal("3'").suppress()
    sequence    =  Combine(seq_start + SkipTo(seq_stop)).setResultsName("seq")
    mwg_primer  =  LineStart() + name + SkipTo(LineStart()) + sequence

    result = mwg_primer.scanString(raw_string)

    seqlist = [data for data,dataStart,dataEnd in result]

    fasta_string = ''

    for data in seqlist:
        s=data.seq.strip("-").replace("\n","").replace(" ","")
        fasta_string+=">{name} ({length}-mer)\n{seq}\n\n".format(name=data.name,length=len(s),seq=s)

    wiki.getActiveEditor().ReplaceSelection(fasta_string)
    wiki.getActiveEditor().SetSelectionByCharPos(start, start+len(fasta_string))

def addtolist(wiki, evt):

    raw_string = wiki.getActiveEditor().GetSelectedText()
    start, end = wiki.getActiveEditor().GetSelection()

    dataStart = end - start

    wiki.getActiveEditor().SetSelectionByCharPos(start,start+dataStart)

    from .mecplugins.parse_string import parse_seqs

    seqs = parse_seqs(raw_string)

    last = seqs[-1]

    seqs = seqs[:-1]

    from pyparsing import Word, Literal, Combine, nums

    fastaheader = Combine(Literal('>').suppress()+Word(nums).setResultsName("number")+Literal('_').suppress())

    data, dataStart, dataEnd = next(fastaheader.scanString(last.format("fasta")))

    number = int(data.number)

    fasta_string = ""

    for s in seqs[::-1]:
        number+=1
        s.id=(str(number)+"_"+s.id).strip()
        s.name=""
        s.description = "({length}-mer)".format(length = len(s))
        fasta_string = s.format("fasta")+"\n"+fasta_string

    fasta_string = fasta_string+last.format("fasta") + "\n"

    wiki.getActiveEditor().ReplaceSelection(fasta_string)
    wiki.getActiveEditor().SetSelectionByCharPos(start, start+len(fasta_string))




def mwgtofasta__OLD(wiki, evt):

    from pyparsing import Word, Literal, printables, LineStart, SkipTo, Combine, nums

    raw_string = wiki.getActiveEditor().GetSelectedText()
    start, end = wiki.getActiveEditor().GetSelection()

    fastaheader = Combine(Literal('>').suppress()+Word(nums).setResultsName("number")+\
                  Literal('_').suppress())
    try:
        data, dataStart, dataEnd = next(fastaheader.scanString(raw_string))
    except StopIteration:
        number = 1
        dataStart = end - start
    else:
        number = int(data.number)+1

    wiki.getActiveEditor().SetSelectionByCharPos(start,start+dataStart)

    name        =  Word(printables).setResultsName("name")
    seq_start   =  Literal("5'").suppress()
    seq_stop    =  Literal("3'").suppress()
    sequence    =  Combine(seq_start + SkipTo(seq_stop)).setResultsName("seq")
    mwg_primer  =  LineStart() + name + SkipTo(LineStart()) + sequence

    result = mwg_primer.scanString(raw_string)

    seqlist = [data for data,dataStart,dataEnd in result]

    number+=len(seqlist)

    fasta_string = ''

    for data in seqlist:
        number-=1
        s=data.seq.strip("-").replace("\n","").replace(" ","")
        fasta_string+=">{number}_{name} ({length}-mer)\n{seq}\n\n".format(number=number,name=data.name,length=len(s),seq=s)

    wiki.getActiveEditor().ReplaceSelection(fasta_string)
    wiki.getActiveEditor().SetSelectionByCharPos(start, start+len(fasta_string))
