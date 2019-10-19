#!/usr/bin/python
# -*- coding: utf8 -*-
'''
docstring
'''

import                              math
import                              textwrap
import                              collections

from .annealprimer                   import annealing_positions


from Bio.SeqUtils.CheckSum          import seguid
from math                           import log10
from Bio.Seq                        import Seq
from Bio.SeqUtils                   import GC
from Bio.SeqUtils.MeltingTemp       import Tm_staluc
from Bio.SeqFeature                 import SeqFeature
from Bio.SeqFeature                 import FeatureLocation
from Bio.SeqFeature                 import CompoundLocation
from .oligo_melting_temp             import tmbresluc
from .parse_string                   import FormattedRecord

__author__       ="Björn Johansson"
__date__         = "2012-01-25"
__copyright__    = "Copyright 2012, Björn Johansson"
__credits__      = ["Björn Johansson","Filipa Pereira", "Gabriela Ribeiro"]
__license__      = "BSD"
__version__      = "0.04"
__maintainer__   = "Björn Johansson"
__email__        = "bjorn_johansson@bio.uminho.pt"
__status__       = "Production" # "Prototype" # "Development" # "Production"


class Amplicon:
    '''
    def __init__(self,
             forward_primer,
             reverse_primer,
             saltc=50,     saltc = monovalent cations (Na,K..) usually 50mM
             fc=1000,      primer concentration in nM (usually 1000nM = 1µM)
             rc=1000):     primer concentration in nM (usually 1000nM = 1µM)
    '''

    def __init__(self,
                 forward_primer,
                 reverse_primer,
                 middle,
                 template,
                 saltc=50,
                 fc=1000,
                 rc=1000):

        self.forward_primer             = forward_primer
        self.reverse_primer             = reverse_primer
        self.middle                     = middle
        self.fc                         = fc
        self.rc                         = rc
        self.saltc                      = saltc
        self.template                   = template
        self.product                    = None



    def pcr_product(self):
        if self.product:
            return self.product
        pcr_product_sequence = self.forward_primer.primer.seq +\
                               self.middle + \
                               self.reverse_primer.primer.seq.reverse_complement()
        self.product = FormattedRecord(
        pcr_product_sequence,
        # description = Genbank LOCUS max 16 chars
        name = "{0}bp_PCR_prod".format(len(pcr_product_sequence))[:16],
        # id = Genbank ACESSION,VERSION also
        id = "{0}bp".format(len(pcr_product_sequence))[:16]+\
             " {0} (rc) {1}".format(seguid(pcr_product_sequence),
                                  seguid(pcr_product_sequence.reverse_complement())),
        # description = Genbank DEFINITION
        description="Primers {0} {1}".format(self.forward_primer.primer.name,
                                             self.reverse_primer.primer.name))

        self.product.features.append(SeqFeature(FeatureLocation(0,len(self.forward_primer.primer)),type ="primer_bind",strand = 1, qualifiers = {"label":self.forward_primer.primer.name,"ApEinfo_fwdcolor":"green","ApEinfo_revcolor":"red"}))
        self.product.features.append(SeqFeature(FeatureLocation(len(self.product) - len(self.reverse_primer.primer),len(self.product)),type ="primer_bind",strand = -1, qualifiers = {"label":self.reverse_primer.primer.name,"ApEinfo_fwdcolor":"green","ApEinfo_revcolor":"red"}))
        return self.product

    def flankup(self,flankuplength=50):
        return self.template.seq[self.forward_primer.pos-flankuplength-len(self.forward_primer.footprint):self.forward_primer.pos-len(self.forward_primer.footprint)]

    def flankdn(self,flankdnlength=50):
        return self.template.seq[self.reverse_primer.pos+len(self.reverse_primer.footprint):self.reverse_primer.pos+flankdnlength+len(self.reverse_primer.footprint)]


    def _tm(self):
        # Tm calculations according to SantaLucia 1998
        self.tmf = Tm_staluc(str(self.forward_primer.footprint),dnac=50, saltc=self.saltc)
        self.tmr = Tm_staluc(str(self.reverse_primer.footprint),dnac=50, saltc=self.saltc)
        # Ta calculation for enzymes with dsDNA binding domains (dbd)
        # like Pfu-Sso7d, Phusion or Phire
        # https://www.finnzymes.fi/tm_determination.html
        self.tmf_dbd = tmbresluc(str(self.forward_primer.footprint),primerc=self.fc)
        self.tmr_dbd = tmbresluc(str(self.reverse_primer.footprint),primerc=self.rc)

    def detailed_figure(self):
        self._tm()
        f ='''
            5{fp}3
             {fap:>{fplength}} tm {tmf} (dbd) {tmf_dbd}
            {sp}5{faz}...{raz}3
            {sp}3{fzc}...{rzc}5
             {sp2}{rap} tm {tmr} (dbd) {tmr_dbd}
            {sp2}3{rp}5
            '''.format( fp       = self.forward_primer.primer.seq,
                        fap      = "|"*len(self.forward_primer.footprint),
                        fplength = len(self.forward_primer.primer.seq),
                        tmf      = round(self.tmf,1),
                        tmr      = round(self.tmr,1),
                        tmf_dbd  = round(self.tmf_dbd,1),
                        tmr_dbd  = round(self.tmr_dbd,1),
                        rp       = self.reverse_primer.primer.seq[::-1],
                        rap      = "|"*len(self.reverse_primer.footprint),
                        rplength = len(self.reverse_primer.primer.seq),
                        faz      = self.forward_primer.footprint,
                        raz      = self.reverse_primer.footprint.reverse_complement(),
                        fzc      = self.forward_primer.footprint.complement(),
                        rzc      = self.reverse_primer.footprint[::-1],
                        sp       = " "*(len(self.forward_primer.primer.seq)-len(self.forward_primer.footprint)),
                        sp2      = " "*(3+len(self.forward_primer.primer.seq))
                       )
        return textwrap.dedent(f)


    def pcr_program(self):
        self._tm()
        if not self.product:
            self.pcr_product()
        # Ta calculation according to
        # Rychlik, Spencer, and Rhoads, 1990, Optimization of the anneal
        # ing temperature for DNA amplification in vitro
        # http://www.ncbi.nlm.nih.gov/pubmed/2003928
        GC_prod=GC(str(self.product.seq))
        tml = min(self.tmf,self.tmr)
        #print GC(str(self.product.seq)), self.saltc/1000.0, len(self.product)
        tmp = 81.5 + 0.41*GC(str(self.product.seq)) + 16.6*log10(self.saltc/1000.0) - 675/len(self.product)
        ta = 0.3*tml+0.7*tmp-14.9
        # Fermentas recombinant taq
        taq_extension_rate = 30  # seconds/kB PCR product length
        extension_time_taq = taq_extension_rate * len(self.product) / 1000 # seconds
        f  = textwrap.dedent('''
                                Taq (rate {rate} nt/s)
                                Three-step|         30 cycles     |      |SantaLucia 1998
                                94.0°C    |94.0°C                 |      |SaltC {saltc:2}mM
                                __________|_____          72.0°C  |72.0°C|
                                04min00s  |30s  \         ________|______|
                                          |      \ {ta}°C/{0:2}min{1:2}s|10min |
                                          |       \_____/         |      |
                                          |         30s           |      |4-8°C
                              '''.format(rate    = taq_extension_rate,
                                         ta      = math.ceil(ta),
                                         saltc   = self.saltc,
                                         *divmod(extension_time_taq,60)))

        PfuSso7d_extension_rate = 15 #seconds/kB PCR product
        extension_time_PfuSso7d = PfuSso7d_extension_rate * len(self.product) / 1000  # seconds

        # Ta calculation for enzymes with dsDNA binding domains like Pfu-Sso7d
        # https://www.finnzymes.fi/tm_determination.html

        length_of_f = len(self.forward_primer.footprint)
        length_of_r = len(self.reverse_primer.footprint)

        if (length_of_f>20 and length_of_r>20 and self.tmf_dbd>=69.0 and self.tmr_dbd>=69.0) or (self.tmf_dbd>=72.0 and self.tmr_dbd>=72.0):
            f+=textwrap.dedent( '''
                                    Pfu-Sso7d (rate {rate}s/kb)
                                    Two-step|    30 cycles |      |Breslauer1986,SantaLucia1998
                                    98.0°C  |98.0C         |      |SaltC {saltc:2}mM
                                    _____ __|_____         |      |Primer1C {fc:3}µM
                                    00min30s|10s  \  72.0°C|72.0°C|Primer2C {rc:3}µM
                                            |      \_______|______|
                                            |      {0:2}min{1:2}s|10min |4-8°C
                                 '''.format(rate = PfuSso7d_extension_rate,
                                            fc = self.fc,
                                            rc = self.rc,
                                            saltc = self.saltc,
                                            *divmod(extension_time_PfuSso7d,60)))
        else:

            if (length_of_f>20 and length_of_r>20):
                ta = min(self.tmf_dbd,self.tmr_dbd)+3
            else:
                ta = min(self.tmf_dbd,self.tmr_dbd)
            f+=textwrap.dedent( '''
                                    Pfu-Sso7d (rate {rate}s/kb)
                                    Three-step|          30 cycles   |      |Breslauer1986,SantaLucia1998
                                    98.0°C    |98.0°C                |      |SaltC {saltc:2}mM
                                    __________|_____          72.0°C |72.0°C|Primer1C {fc:3}µM
                                    00min30s  |10s  \ {ta}°C ________|______|Primer2C {rc:3}µM
                                              |      \______/{0:2}min{1:2}s|10min |
                                              |        10s           |      |4-8°C
                                 '''.format(rate = PfuSso7d_extension_rate,
                                            ta   = math.ceil(ta),
                                            fc   = self.fc/1000,
                                            rc   = self.rc/1000,
                                            saltc= self.saltc,
                                            *divmod(extension_time_PfuSso7d,60)))
        return f



class Anneal:
    '''
    def __init__(self,
             primers,
             template,
             topology="linear",
             homology_limit=13,
             max_product_size=15000):
    '''

    def __init__(self,
                 primers,
                 template,
                 topology="linear",
                 homology_limit=13,
                 max_product_size=15000):

        assert type(primers) == list
        assert(template.seq) # empty template record
        for p in primers:
            assert(p.seq) # empty sequence records in primers
        self.template = template
        primer = collections.namedtuple("primer","primer pos footprint")
        self.fwd_primers = []
        self.rev_primers = []
        self.amplicons   = []
        if "c" in topology:
            self.topology = "circular"
        else:
            self.topology = "linear"
        self.homology_limit = homology_limit

        tm = str(template.seq)
        tm_rc = str(template.seq.reverse_complement)
        if self.topology == "linear":
            for p in primers:
                self.fwd_primers.extend((primer(p, pos, Seq(footprint)) for
                                         pos, footprint in annealing_positions(
                                                            str(p.seq),
                                                            tm,
                                                            homology_limit)))
                self.rev_primers.extend((primer(p,len(template)-pos, Seq(footprint))
                                         for pos, footprint in annealing_positions(
                                                            str(p.seq),
                                                            tm_rc,
                                                            homology_limit)))
        else:
            ct = 2*tm
            ct_rc = 2*tm_rc
            for p in primers:
                ann1 = annealing_positions(str(p.seq), tm, homology_limit)
                ann2 = annealing_positions(str(p.seq), ct, homology_limit)
                ann  = set(ann2) - set(ann1)
                ann  = [primer(p, pos%len(template), Seq(footprint)) for (pos, footprint) in ann]
                self.fwd_primers.extend(ann)

                ann1 = annealing_positions(str(p.seq), tm_rc, homology_limit)
                ann2 = annealing_positions(str(p.seq), ct_rc, homology_limit)
                ann  = set(ann2) - set(ann1)
                ann  = [primer(p, len(template)-pos%len(template), Seq(footprint)) for (pos, footprint) in ann]
                self.rev_primers.extend(ann)

        for fp in self.fwd_primers:
            for rp in self.rev_primers:
                if (0 < rp.pos-fp.pos < max_product_size):
                    middle_part = self.template.seq[fp.pos+1:rp.pos-1]
                    #print middle_part
                elif self.topology == "circular" and fp.pos>rp.pos and len(template)-fp.pos-rp.pos < max_product_size:
                    middle_part = self.template.seq[fp.pos+1:]+self.template.seq[:rp.pos-1]
                    #print middle_part
                else:
                    continue
                self.amplicons.append(Amplicon(fp,rp, middle_part,self.template))
        self.number_of_products = len(self.amplicons)

    def report(self):
        return self.__str__()

    def __str__(self):
        mystring = "Template {name} {size} nt ({top}):\n".format(name=self.template.name,size=len(self.template),top=self.topology)
        if self.fwd_primers:
            for primer, pos, footp in self.fwd_primers:
                mystring += "Primer "+primer.name
                mystring += " anneals at position "
                mystring += str(pos)
                mystring += "\n"
        else:
            mystring += "No forward primers anneal...\n"
        if self.rev_primers:
            for primer,pos, footp in self.rev_primers:
                mystring += "Primer "+primer.name
                mystring += " anneals reverse at position "
                mystring += str(pos)
                mystring += "\n"
        else:
             mystring += "No reverse primers anneal...\n"
        return mystring

    def products(self):
        return [a.product for a in self.amplicons]

    def featured_template(self):
        template = self.template
        for fp, pos, footprint in self.fwd_primers:
            if pos-len(footprint)>0:
                start = pos-len(footprint)
                end = pos
                template.features.append(SeqFeature(FeatureLocation(start,end+1,strand = -1),type ="primer_bind", qualifiers = {"label":fp.name,"ApEinfo_fwdcolor":"green","ApEinfo_revcolor":"red"}))
            else:
                start = len(template)-len(footprint)+pos
                end = start+len(footprint)-len(template)
                #suba = SeqFeature( FeatureLocation(start,len(template)),type ="primer_bind",strand = 1, qualifiers = {"label":fp.name,"ApEinfo_fwdcolor":"green","ApEinfo_revcolor":"red"})
                #subb = SeqFeature( FeatureLocation(0,end),              type ="primer_bind",strand = 1, qualifiers = {"label":fp.name,"ApEinfo_fwdcolor":"green","ApEinfo_revcolor":"red"})
                #template.features.append(SeqFeature(FeatureLocation(start,end),type ="primer_bind",sub_features = [suba,subb], location_operator= "join",strand = 1, qualifiers = {"label":fp.name}))
                template.features.append(SeqFeature(CompoundLocation([FeatureLocation(start,len(template), strand = 1),
                                                                      FeatureLocation(0,end, strand = 1),]),
                                                    type ="primer_bind",
                                                    location_operator= "join",                                                    
                                                    qualifiers = {"label":'"{}"'.format(fp.name),"ApEinfo_fwdcolor":"green","ApEinfo_revcolor":"red"})) 
        
        
        for rp, pos, footprint in self.rev_primers:
            if pos+len(footprint)<=len(template):
                start = pos
                end = pos + len(footprint)
                template.features.append(SeqFeature(FeatureLocation(start-1,end,strand = -1),type ="primer_bind", qualifiers = {"label":rp.name,"ApEinfo_fwdcolor":"green","ApEinfo_revcolor":"red"}))
            else:
                start = pos
                end = pos+len(footprint)-len(template)
                #suba = SeqFeature(FeatureLocation(start,len(template)),type ="primer_bind",strand = -1, qualifiers = {"label":rp.name,"ApEinfo_fwdcolor":"green","ApEinfo_revcolor":"red"})
                #subb = SeqFeature(FeatureLocation(0,end),              type ="primer_bind",strand = -1, qualifiers = {"label":rp.name,"ApEinfo_fwdcolor":"green","ApEinfo_revcolor":"red"})
                #template.features.append(SeqFeature(FeatureLocation(start,end),type ="primer_bind",sub_features = [suba,subb], location_operator= "join", strand = -1, qualifiers = {"label":rp.name}))
        
                template.features.append(SeqFeature(CompoundLocation([FeatureLocation(start,len(template),strand = -1),
                                                                      FeatureLocation(0,end,strand = -1)]),
                                                    type ="primer_bind",
                                                    location_operator= "join",                                                    
                                                    qualifiers = {"label":rp.name,"ApEinfo_fwdcolor":"green","ApEinfo_revcolor":"red"}))
            
                
                
        return template





if __name__=="__main__":


    from .parse_string import parse_seqs

    raw='''

    >pCAPsAjiIR
    GTGCcatctgtgcagacaaacgcatcagg

    >pCAPsAjiIF
    gtcggctgcaggtcactagtgagaaagtg

    >AJ001614 circular
    CACTTTCTCACTAGTGACCTGCAGCCGGCGCGCCATCTGTGCAGACAAACGCATCAGG'''

    raw='''

    >primerA
    Aatctgactatcga
    >primerB
    Tgtggtaggcatgt
    >templ
    TTTATCTGACTATCGAAACATGCCTACCACGGG
    '''



    new_sequences = parse_seqs(raw)
    template = new_sequences.pop()
    primer_sequences  = new_sequences
    topology="circular"
    homology_limit=13
    max_product_size=10000

    anneal_primers = Anneal(primer_sequences,
                            template,
                            topology,
                            homology_limit,
                            max_product_size)

    #print anneal_primers

    #print anneal_primers.featured_template().format("gb")
    #print anneal_primers.number_of_products
    if anneal_primers.number_of_products:
        for hej in anneal_primers.amplicons:
            pass
            #print hej.pcr_product().name
            print(hej.pcr_product().format("fasta"))
            #print hej.pcr_program()
            #print hej.pcr_product().annotations
            #print hej.detailed_figure()

            print(hej.flankup(10))
            print(hej.flankdn(10))

