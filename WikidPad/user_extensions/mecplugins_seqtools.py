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

#from . import mecplugins_ini

import string
import textwrap
import datetime

from Bio.Seq                        import Seq
from Bio.SeqUtils                   import GC, seq3
from Bio.SeqUtils.MeltingTemp       import Tm_staluc

from Bio.Alphabet.IUPAC             import extended_protein
from Bio.Alphabet.IUPAC             import protein
from Bio.Alphabet.IUPAC             import ambiguous_dna
from Bio.Alphabet.IUPAC             import unambiguous_dna
from Bio.Alphabet.IUPAC             import extended_dna
from Bio.Alphabet.IUPAC             import ambiguous_rna
from Bio.Alphabet.IUPAC             import unambiguous_rna

from .mecplugins.oligo_melting_temp             import basictm, tmbresluc
from .mecplugins.seq31                          import seq1
from .mecplugins.parse_string                   import parse_seqs, guess_alphabet
from .mecplugins.pcr                            import Anneal
from .mecplugins.analysis                       import restrictionanalyserecords

#from mecplugins_settings.PCR import *

def describeMenuItems(wiki):
    return (
            (revcomp,           _("mecplugins|DNA Sequence Tools|Reverse complement")             + "\t",               _("revcomp")),
            (comp,              _("mecplugins|DNA Sequence Tools|Complement")                     + "\t",               _("comp")),
            (translate,         _("mecplugins|DNA Sequence Tools|Translate")                      + "\t",               _("pcr")),
            (tm,                _("mecplugins|DNA Sequence Tools|Melting temperature")            + "\tCtrl-Shift-T",   _("tm")),
            (toggle_format,     _("mecplugins|DNA Sequence Tools|Toggle sequence formats")        + "\t",               _("toggle_format")),
            (fasta_tab,         _("mecplugins|DNA Sequence Tools|fasta->tab format")              + "\t",               _("fasta_tab")),
            (pcr,               _("mecplugins|DNA Sequence Tools|PCR simulation")                 + "\tCtrl-Shift-P",   _("pcr")),
            (reanal,            _("mecplugins|DNA Sequence Tools|Restriction analysis")           + "\t",               _("reanal")),
            )

def empty(wiki, evt):
    pass

def describeToolbarItems(wiki):
    return (
            (revcomp, "reverse complement", "reverse complement", "mec_reverse_com"),
            (comp, "complement", "complement", "mec_complement"),
            (translate, "translate", "translate", "mec_translate"),
            (tm, "tm", "tm", "tm"),
            (toggle_format,"Toggle format","Toggle format","mec_toggle_format"),
            (pcr, "PCR simulation", "PCR simulation", "mec_pcr"),
            (reanal, "resctriction analysis", "resctriction analysis", "mec_digest"),
           )

def revcomp(wiki, evt):
    raw_sequence = wiki.getActiveEditor().GetSelectedText()
    if not raw_sequence:
        return
    sequence = Seq(raw_sequence, ambiguous_dna)
    reverse_complement = sequence.reverse_complement()
    start, end = wiki.getActiveEditor().GetSelectionCharPos()
    wiki.getActiveEditor().ReplaceSelection(str(reverse_complement))
    wiki.getActiveEditor().SetSelectionByCharPos(start, end)

def comp(wiki, evt):
    raw_sequence = wiki.getActiveEditor().GetSelectedText()
    if not raw_sequence:
        return
    sequence = Seq(raw_sequence, ambiguous_dna)
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
    alphabet = guess_alphabet(raw_string)
    #print alphabet
    if alphabet==ambiguous_dna or alphabet==unambiguous_dna or alphabet==extended_dna or alphabet==unambiguous_rna or alphabet==ambiguous_rna:
        sequence = Seq(raw_string, alphabet)
        protein_sequence = str(sequence.translate(to_stop=True))
        protein_sequence ="".join([i+"  " for i in protein_sequence])
    if alphabet==protein or alphabet == extended_protein:
        protein_sequence = seq3(raw_string)
    if alphabet=="three letter code":
        protein_sequence = seq1(raw_string)
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

    length = len(primer)

    if not primer:

        tm_optimal=53
        length=1

        maxlength = len(wiki.getActiveEditor().GetText())

        while True:
            wiki.getActiveEditor().SetSelectionByCharPos(start,start+length)
            print(start,length)
            primer = "".join([char for char in wiki.getActiveEditor().GetSelectedText() if char in "ACBEDGFIHKJMLONQPSRUTWVYXZacbedgfihkjmlonqpsrutwvyxz"])
            t=Tm_staluc(primer)
            if t<tm_optimal:
                length+=1
                if length>maxlength:
                    break
            else:
                if int(round(GC(primer)))>45 or length>29:
                    start+=1
                    length=1
                else:
                    break

    wiki.getActiveEditor().SetSelectionByCharPos(start,end)
    #wiki.getActiveEditor().GotoPos(start)


    temp_staluc  = round(Tm_staluc(primer),2)
    temp_bresluc = round(tmbresluc(primer,primerc=1000),2)
    temp_wallace = round(basictm(primer),2)
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

def fasta_tab(wiki, evt):
    raw_sequence = wiki.getActiveEditor().GetSelectedText()
    if not raw_sequence:
        return
    start, end = wiki.getActiveEditor().GetSelectionCharPos()
    new_sequences=parse_seqs(raw_sequence)
    if not new_sequences:
        return
    result_text= ''
    for seq in new_sequences:
        result_text += seq.format("tab")

    wiki.getActiveEditor().ReplaceSelection(result_text)
    wiki.getActiveEditor().SetSelectionByCharPos(start, start+len(result_text))
    return

def toggle_format(wiki, evt):
    content = wiki.getActiveEditor().GetSelectedText()
    if not content:
        return
    start, end = wiki.getActiveEditor().GetSelectionCharPos()
    new_sequences = parse_seqs(content)
    result_text = ""
    if not new_sequences:
        new_sequences = parse_seqs(">sequence_{0}_bp\n".format(len(content)) + content)
    for seq in new_sequences:
        if seq.original_format == "raw":
            format = "fasta"
        elif seq.original_format == "embl":
            format = "genbank"
        elif seq.original_format == "fasta":
            format = "genbank"
        elif seq.original_format == "tab":
            format = "fasta"
        elif seq.original_format == "genbank":
            format = "fasta"
            if seq.id in ("","."):
                seq.id = seq.name
            if seq.description ==".":
                seq.description = ""
        else:
            format = "fasta"
        if not seq.format in ("genbank","embl"):
            seq.annotations.update({"date": datetime.date.today().strftime("%d-%b-%Y").upper() })

        result_text += seq.format(format)
    wiki.getActiveEditor().ReplaceSelection(result_text)
    wiki.getActiveEditor().SetSelectionByCharPos(start, start+len(result_text))
    return

def pcr(wiki, evt):
    #print "ePCR:"
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
    
    # get settings
    settings={}
    exec(wiki.getWikiDocument().getWikiPage("mecplugins_settings").getContent().encode(), globals(), settings)
    for k,v in settings.items():
        globals()[k]=v
        
    if lines.count(template_separator)>1:
        message=wiki.stdDialog("o", "Error in data for ePCR", "too many template separators ({0})in the data".format(template_separator), additional=None)
        return
    elif lines.count(template_separator)==1:
        index=lines.index(template_separator)
        primertext = "\n".join(lines[:index])+"\n"
        primer_sequences = parse_seqs(primertext)
        #remove sequence records with no sequence
        primer_sequences = [rec for rec in primer_sequences if rec.seq]
        templatetext="\n".join(lines[index+1:])+"\n"
        template_sequences = parse_seqs(templatetext)
        #remove sequence records with no sequence
        template_sequences = [rec for rec in template_sequences if rec.seq]
    else:
        #No separator, join all text together
        primer_and_templatetext="\n".join(lines)+"\n"
        #print primer_and_templatetext
        all_sequences = parse_seqs(primer_and_templatetext)
        #remove sequence records with no sequence
        all_sequences = [rec for rec in all_sequences if rec.seq]
        #if there is no template separator, the last sequence is considered the template
        template_sequences = [all_sequences.pop()]
        primer_sequences = all_sequences
    #test if there is at least one non-empty template sequence
    if len(template_sequences)<1:
        message=wiki.stdDialog("o", "Error in data for ePCR", "template empty!", additional=None)
        return
    #test if there is at least one non-empty primer sequence
    if len(primer_sequences)<1:
        message=wiki.stdDialog("o", "Error in data for ePCR", "No primers!", additional=None)
        return
    # prepare report


    result_text=''
    message_template = report_header

    for template in template_sequences:
        if template.circular:
            topology = "circular"
        else:
            topology = "linear"

        anneal_primers = Anneal( primer_sequences,
                                 template,
                                 topology,
                                 homology_limit,
                                 max_product_size)

        if anneal_primers.number_of_products==0:
            result_text="\n"+anneal_primers.report()

        elif 1<=anneal_primers.number_of_products<=cutoff_detailed_figure:
            message_template += report_for_each_simulation
            for amplicon in anneal_primers.amplicons:
                message_template += report_for_each_amplicon
                result_text+="\n"+string.Template(message_template).safe_substitute(
                    anneal_primers                = anneal_primers,
                    forward_primer_name           = amplicon.forward_primer.primer.name,
                    forward_primer_sequence       = amplicon.forward_primer.primer.seq,
                    reverse_primer_name           = amplicon.reverse_primer.primer.name,
                    reverse_primer_sequence       = amplicon.reverse_primer.primer.seq,
                    product_name                  = amplicon.pcr_product().id,
                    product_sequence              = amplicon.pcr_product().seq,
                    template_name                 = anneal_primers.template.name,
                    template_sequence             = anneal_primers.template.seq,
                    upstream_flanking_sequence    = amplicon.flankup(),
                    downstream_flanking_sequence  = amplicon.flankdn(),
                    figure                        = amplicon.detailed_figure(),
                    pcr_program                   = amplicon.pcr_program() 
                    )
     
                    
                message_template=''

        elif anneal_primers.number_of_products>cutoff_featured_template:
            result_text+="\n"+anneal_primers.featured_template().format("gb")

    wiki.getActiveEditor().gotoCharPos(end)
    wiki.getActiveEditor().AddText(result_text)
    wiki.getActiveEditor().SetSelectionByCharPos(end, end+len(result_text))
    return

def reanal(wiki, evt):
    raw_sequence = wiki.getActiveEditor().GetSelectedText()
    start, end = wiki.getActiveEditor().GetSelectionCharPos()
    if not raw_sequence:
        return
    new_sequences=parse_seqs(raw_sequence)
    if not new_sequences:
        return
    result_text=restrictionanalyserecords(new_sequences)
    wiki.getActiveEditor().GotoPos(end)
    wiki.getActiveEditor().AddText(result_text)
    wiki.getActiveEditor().SetSelectionByCharPos(end+1, end+len(result_text))
    #wiki.getActiveEditor().GotoPos(start)
    return
