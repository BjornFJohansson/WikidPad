#!/usr/bin/env python
# -*- coding: utf-8 -*-
##########################################
#   _____         _______          _
#  / ____|       |__   __|        | |
# | (___   ___  __ _| | ___   ___ | |___
#  \___ \ / _ \/ _` | |/ _ \ / _ \| / __|
#  ____) |  __/ (_| | | (_) | (_) | \__ \
# |_____/ \___|\__, |_|\___/ \___/|_|___/
#                 | |
#                 |_|
##########################################

WIKIDPAD_PLUGIN = (("MenuFunctions",1), ("ToolbarFunctions",1))
#WIKIDPAD_PLUGIN = (("MenuFunctions",1), )

import string
import textwrap
import datetime
import re

from Bio.Seq                        import Seq
from Bio.SeqUtils                   import GC, seq3
from Bio.SeqUtils.MeltingTemp       import Tm_staluc

from Bio.SeqUtils.MeltingTemp       import Tm_Wallace
from pydna.tm                       import tmbresluc
from pydna.utils                    import seq31

from pydna.parsers                  import parse
from pydna.amplify                  import Anneal
from pydna.amplify                  import pcr

from pydna.genbankfixer import gbtext_clean
from pydna.readers import read

def describeMenuItems(wiki):
    return (
            (revcomp,           _("mecplugins|DNA Sequence Tools|Reverse complement")      + "\t",               _("revcomp")),
            (comp,              _("mecplugins|DNA Sequence Tools|Complement")              + "\t",               _("comp")),
            (translate,         _("mecplugins|DNA Sequence Tools|Translate")               + "\t",               _("pcr")),
            (tm,                _("mecplugins|DNA Sequence Tools|Melting temperature")     + "\tCtrl-Shift-T",   _("tm")),
            (toggle_format,     _("mecplugins|DNA Sequence Tools|Toggle sequence formats") + "\t",               _("toggle_format")),
            (tab,               _("mecplugins|DNA Sequence Tools|tab format")              + "\t",               _("tab")),
            (pcr_,              _("mecplugins|DNA Sequence Tools|PCR simulation")          + "\tCtrl-Shift-P",   _("pcr")),
            (reanal,            _("mecplugins|DNA Sequence Tools|Restriction analysis")    + "\t",               _("reanal")),
            (fix_gb,            _("mecplugins|DNA Sequence Tools|fix genbank")             + "\t",               _("fix_gb")),
            )

def empty(wiki, evt):
    pass

def describeToolbarItems(wiki):
    return (
            (revcomp,        "reverse complement",    "reverse complement",    "mec_reverse_com"),
            (reverse,        "reverse",               "reverse",               "mec_reverse"),
            (comp,           "complement",            "complement",            "mec_complement"),
            (translate,      "translate",             "translate",             "mec_translate"),
            (tm,             "tm",                    "tm",                    "mec_tm"),
            (toggle_format,  "Toggle format",         "Toggle format",         "mec_toggle_format"),
            (pcr_,            "PCR simulation",        "PCR simulation",        "mec_pcr"),
            (reanal,         "resctriction analysis", "resctriction analysis", "mec_digest"),
            (fix_gb,         "fix genbank",           "fix genbank",           "settings"),
           )

def revcomp(wiki, evt):
    raw_sequence = wiki.getActiveEditor().GetSelectedText()
    if not raw_sequence:
        return
    sequence = Seq(raw_sequence)
    reverse_complement = sequence.reverse_complement()
    start, end = wiki.getActiveEditor().GetSelectionCharPos()
    wiki.getActiveEditor().ReplaceSelection(str(reverse_complement))
    wiki.getActiveEditor().SetSelectionByCharPos(start, end)

def reverse(wiki, evt):
    raw_sequence = wiki.getActiveEditor().GetSelectedText()
    if not raw_sequence:
        return
    start, end = wiki.getActiveEditor().GetSelectionCharPos()
    wiki.getActiveEditor().ReplaceSelection(raw_sequence[::-1])
    wiki.getActiveEditor().SetSelectionByCharPos(start, end)

def comp(wiki, evt):
    raw_sequence = wiki.getActiveEditor().GetSelectedText()
    if not raw_sequence:
        return
    sequence = Seq(raw_sequence)
    complement = sequence.complement()
    start, end = wiki.getActiveEditor().GetSelectionCharPos()
    wiki.getActiveEditor().ReplaceSelection(str(complement))
    wiki.getActiveEditor().SetSelectionByCharPos(start, end)
    return

def translate(wiki, evt):
    raw_sequence = wiki.getActiveEditor().GetSelectedText()
    if not raw_sequence:
        return
    start, end = wiki.getActiveEditor().GetSelectionCharPos()
    raw_string = "".join([char for char in raw_sequence if char in "ACBEDGFIHKJMLONQPSRUTWVYXZacbedgfihkjmlonqpsrutwvyxz"])

    sequence = Seq(raw_string)
    protein_sequence = str(sequence.translate(to_stop=True))
    protein_sequence ="".join([i+"  " for i in protein_sequence])

    padding = len(raw_sequence)-len(protein_sequence)
    wiki.getActiveEditor().ReplaceSelection(protein_sequence+" "*padding)
    wiki.getActiveEditor().SetSelectionByCharPos(start, start+len(protein_sequence+" "*padding))
    return

def tm(wiki, evt):
    start, end = wiki.getActiveEditor().GetSelectionCharPos()
    raw_sequence = wiki.getActiveEditor().GetSelectedText()
    primer = "".join([char for char in raw_sequence if char in "ACBEDGFIHKJMLONQPSRUTWVYXZacbedgfihkjmlonqpsrutwvyxz"])

    if primer and 1<len(primer)<13:
        wiki.displayMessage("Primer melting temperature","primer 1<length<13")
        return

    temp_staluc  = round(Tm_staluc(primer),2)
    temp_bresluc = round(tmbresluc(primer,primerc=1000),2)
    temp_wallace = round(Tm_Wallace(primer),2)
    GCcontent = round(GC(primer),0)

    wiki.displayMessage(u"Primer melting temperature",
                        textwrap.dedent(
                        u'''
                        Nearest Neighbour StLucia 1998: \t{} °C
                        Bresl 1986 + StLucia 1998 1µM: \t{} °C
                        (A+T)*2+(G+C)*4: \t{} °C
                        GC: \t{}
                        length: \t{}-mer
                        '''.format(temp_staluc,temp_bresluc,temp_wallace,GCcontent,len(primer))))
    return

def tab(wiki, evt):
    raw_sequence = wiki.getActiveEditor().GetSelectedText()
    if not raw_sequence:
        return
    start, end = wiki.getActiveEditor().GetSelectionCharPos()
    new_sequences=parse(raw_sequence)
    if not new_sequences:
        return
    result_text= ''
    for seq in new_sequences:
        result_text += seq.format("tab")+"\n"
    wiki.getActiveEditor().ReplaceSelection(result_text)
    wiki.getActiveEditor().SetSelectionByCharPos(start, start+len(result_text))
    return

def fix_gb(wiki, evt):
    content = wiki.getActiveEditor().GetSelectedText()
    if not content:
        return
    gbtext, json = gbtext_clean(content)
    result_text = read(gbtext).format()
    start, end = wiki.getActiveEditor().GetSelectionCharPos()
    wiki.getActiveEditor().ReplaceSelection(result_text)
    wiki.getActiveEditor().SetSelectionByCharPos(start, start+len(result_text))
    return

def toggle_format(wiki, evt):
    content = wiki.getActiveEditor().GetSelectedText()
    if not content:
        return
    start, end = wiki.getActiveEditor().GetSelectionCharPos()
    pattern =  r"(?:>.+\n^(?:^[^>]+?)(?=\n\n|>|LOCUS|ID))|(?:(?:LOCUS|ID)(?:(?:.|\n)+?)^//)"
    rawseqs = re.findall(pattern, textwrap.dedent(content + "\n\n"), flags=re.MULTILINE)
    if rawseqs:
        rawseq = rawseqs[0]
        if rawseq.startswith(">"):
            format_ = "gb"
        else:
            format_ = "fasta"
    else:
        content = ">seq_{}bp\n{}".format(len(content), content)
        format_="fasta"

    result_text=""
    for seq in parse(content):
        if seq.id in ("","."): seq.id = seq.name
        if seq.description ==".": seq.description = ""
        if not format_ in ("genbank","embl"): seq.annotations.update({"date": datetime.date.today().strftime("%d-%b-%Y").upper() })
        result_text+= seq.format(format_)+"\n\n"

    wiki.getActiveEditor().ReplaceSelection(result_text)
    wiki.getActiveEditor().SetSelectionByCharPos(start, start+len(result_text))
    return

def pcr_(wiki, evt):
    start, end = wiki.getActiveEditor().GetSelectionCharPos()
    selected_text = wiki.getActiveEditor().GetSelectedText()
    # if nothing was selected
    if not selected_text:
        return
    #make a list of strings of selected text
    lines=selected_text.splitlines()
    #print lines
    #print
    #look for wikiwords to expand, they have to come alone, one per row
    expanded_list=[]
    for line in lines:
        # if the wikiwords are enclosed by [], this should be done better
        strippedline = line.strip("[ ]")
        if wiki.getWikiDocument().isDefinedWikiLink(strippedline):
            pagelines=("\n" + wiki.getWikiDocument().getWikiPage(strippedline).getContent() + "\n").splitlines()
            expanded_list.extend(pagelines)
        else:
            expanded_list.append(line)
    lines = expanded_list

    global homology_limit
    global cutoff_featured_template
    global cutoff_detailed_figure
    global report_header
    global report_for_each_simulation
    global report_for_each_amplicon

    # get settings
    exec(wiki.getWikiDocument().getWikiPage("mecplugins_settings").getContent().encode(), globals())

    assert homology_limit
    assert cutoff_featured_template
    assert cutoff_detailed_figure
    assert report_header
    assert report_for_each_simulation
    assert report_for_each_amplicon

    #join all text together; remove sequence records with no sequence
    sequences = [rec for rec in parse("\n\n".join(lines)+"\n\n") if rec.seq]
    #if there is no template separator, the last sequence is considered the template
    template = sequences.pop()
    primer_sequences = sequences
    # #test if there is at least one non-empty template sequence
    # if len(template_sequences)<1:
    #     message=wiki.stdDialog("o", "Error in data for ePCR", "template empty!", additional=None)
    #     return
    # #test if there is at least one non-empty primer sequence
    # if len(primer_sequences)<1:
    #     message=wiki.stdDialog("o", "Error in data for ePCR", "No primers!", additional=None)
    #     return
    # # prepare report

    result_text=''

    message_template = report_header

    if template.circular:
        topology = "circular"
    else:
        topology = "linear"

    ann = Anneal( primer_sequences,
                  template,
                  limit=homology_limit)

    result_text=""

    number_of_products = len(ann.forward_primers) * len(ann.reverse_primers)

    if number_of_products==0:
        result_text="\n"+ann.report()
    elif 1<=number_of_products<=cutoff_detailed_figure:
        message_template += report_for_each_simulation
        for amplicon in ann.products:
            message_template += report_for_each_amplicon
            result_text+=message_template.format(
                anneal_primers                = ann,
                forward_primer_name           = amplicon.forward_primer.name,
                forward_primer_sequence       = amplicon.forward_primer.seq,
                reverse_primer_name           = amplicon.reverse_primer.name,
                reverse_primer_sequence       = amplicon.reverse_primer.seq,
                product_name                  = amplicon.name,
                product_sequence              = amplicon.seq,
                template_name                 = ann.template.name,
                template_sequence             = ann.template.seq,
                figure                        = amplicon.figure())

            message_template=''

    elif  number_of_products>cutoff_featured_template:
        print("ann:", ann)
        result_text+="\n"+ann.template.format("gb")


    wiki.getActiveEditor().gotoCharPos(end)
    wiki.getActiveEditor().AddText(result_text)
    wiki.getActiveEditor().SetSelectionByCharPos(end, end+len(result_text))
    return

def reanal(wiki, evt):
    raw_sequence = wiki.getActiveEditor().GetSelectedText()
    start, end = wiki.getActiveEditor().GetSelectionCharPos()
    if not raw_sequence:
        return
    sequences=parse(raw_sequence)
    if not sequences:
        return

    if len(sequences) == 1:

        seq = sequences[0]

        nocutters = seq.no_cutters()
        unique    = seq.unique_cutters()
        twoormore = seq.cutters() - unique

        result_text = textwrap.dedent('''

        Restriction analysis of a single sequence
        -----------------------------------------
        The following enzymes are absent:

        {nocutters}

        The following enzymes cut once:

        {unique}

        The following enzymes cut twice or more:

        {twoormore}'''.format(nocutters = " ".join([str(e) for e in nocutters]),
                              unique    = " ".join([str(e) for e in unique]),
                              twoormore = " ".join([str(e) for e in twoormore])   ))
    else:

        nocutters    = set.intersection(*[s.no_cutters() for s in sequences])
        unique       = set.intersection(*[s.unique_cutters() for s in sequences])
        cutinlast    = set.intersection(*[s.no_cutters() for s in sequences[:-1]])
        cutinlast    = cutinlast & sequences[-1].cutters()

        result_text = textwrap.dedent('''

        Restriction analysis of {numberofsequences} sequences
        ------------------------------------
        The following enzymes are absent from all sequences:

        {nocutters}

        The following enzymes cut once in each sequence:

        {unique}

        The following enzymes cut in the last sequence and are absent in the preceding sequence(s):

        {cutinlast}'''.format( numberofsequences=len(sequences),
                               unique        = " ".join([str(e) for e in unique]),
                               nocutters     = " ".join([str(e) for e in nocutters]),
                               cutinlast     = " ".join([str(e) for e in cutinlast])))

    wiki.getActiveEditor().GotoPos(end)
    wiki.getActiveEditor().AddText(result_text)
    wiki.getActiveEditor().SetSelectionByCharPos(end+1, end+len(result_text))
    #wiki.getActiveEditor().GotoPos(start)
    return
