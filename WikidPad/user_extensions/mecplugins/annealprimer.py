#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
docstring
'''

import re
import itertools

__author__       ="Björn Johansson"
__date__         = ""
__copyright__    = "Copyright 2012, Björn Johansson"
__credits__      = ["Björn Johansson"]
__license__      = "BSD"
__version__      = "0.01"
__maintainer__   = "Björn Johansson"
__email__        = "bjorn_johansson@bio.uminho.pt"
__status__       = "Development" # "Production" #"Prototype" # "Production"


def annealing_positions(primer, template, limit):
    if len(primer)<limit:
        return []
    head = primer[-limit:]
    positions = [m.start() for m in re.finditer('(?={0})'.format(head), template, re.I)]
    if positions:
        tail = primer[:-limit]
        length = len(tail)
        revtail = tail[::-1]
        results = []
        for match_start in positions:
            tm = template[max(0,match_start-length):match_start][::-1]
            footprint = "".join(reversed([b for a,b in itertools.takewhile(lambda x: x[0].lower()==x[1].lower(),list(zip(revtail, tm)))])) + template[match_start:match_start+limit]
            results.append((match_start+limit-1, footprint))
        return results
    return []

if __name__=="__main__":

    p="GTGCcatctgtgcagacaaacgcatcagg"
    t= "CGCCATCTGTGCAGACAAACGCATCAGgaaaa"
    #   0123456789012345678901234567
    print(annealing_positions(p,t, 13))
    print(t[27])
