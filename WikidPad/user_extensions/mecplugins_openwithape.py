#!/usr/bin/env python
# -*- coding: utf-8 -*-
##########################################################################
#   ____                              _ _   _                      ______
#  / __ \                            (_) | | |         /\         |  ____|
# | |  | |_ __   ___ _ __   __      ___| |_| |__      /  \   _ __ | |__
# | |  | | '_ \ / _ \ '_ \  \ \ /\ / / | __| '_ \    / /\ \ | '_ \|  __|
# | |__| | |_) |  __/ | | |  \ V  V /| | |_| | | |  / ____ \| |_) | |____
#  \____/| .__/ \___|_| |_|   \_/\_/ |_|\__|_| |_| /_/    \_\ .__/|______|
#        | |                                                | |
#        |_|                                                |_|
##########################################################################
# -*- coding: latin-1 -*-
## http://209.85.135.132/search?q=cache:kIj5Feoa3o0J:docs.python.org/library/tempfile.html+python+make+temp+file&cd=1&hl=en&ct=clnk&gl=pt
## http://blog.doughellmann.com/2008/02/pymotw-tempfile.html

#WIKIDPAD_PLUGIN = (("MenuFunctions",1),)
WIKIDPAD_PLUGIN = (("MenuFunctions",1), ("ToolbarFunctions",1))
#from . import mecplugins_ini
import codecs
import tempfile
import sys
import os
import subprocess
from .mecplugins.parse_string import parse_seqs

#from mecplugins_settings.open_with_ape import *

def describeMenuItems(wiki):
    return((openwithape, _("mecplugins|DNA Sequence Tools|Open selection with ApE"), _("ApE")),
          )

def describeToolbarItems(wiki):
    return ((openwithape, _("open selection with ApE"), _("ApE"), "mec_ape"),)

def openwithape(wiki, evt):
    cont = wiki.getActiveEditor().GetSelectedText()
    if not cont:
        cursorline = wiki.getActiveEditor().GetCurrentLine()
        textlines  = wiki.getActiveEditor().GetText().split("\n")
        line = cursorline
        foundstart = True
        while not (textlines[line].startswith("LOCUS") or textlines[line].startswith(">")):
            if line == 0:
                foundstart = False
                break
            line=line-1
        if foundstart:
            cont = "\n".join(textlines[line:])

    settings={}
    exec(wiki.getWikiDocument().getWikiPage("mecplugins_settings").getContent().encode(), globals(), settings)
    for k,v in settings.items():
        globals()[k]=v
        print(k,"--->", v)
        
    if sys.platform.startswith('linux'):
        path_to_ape = path_to_ape_lin

    if sys.platform == 'win32':
        path_to_ape = path_to_ape_win

    if sys.platform == 'darwin':
        path_to_ape = path_to_ape_mac

    if cont:
        path = os.path.join(tempfile.gettempdir(),"WikidPad","sequences")
        try:
            os.makedirs(path)
        except OSError:
            pass
        path = tempfile.mkdtemp(dir=path)
        seqs = parse_seqs(cont)
        if not seqs:
            seqs = parse_seqs(">sequence_"+str(len(cont))+"bp\n" + cont)
        pathstofiles=[]
        for seq in seqs:
            filename = "{0}.{1}".format(seq.id, seq.original_format)
            pathtofile = os.path.join(path,filename)
            f = open(pathtofile,"w")
            f.write(seq.format("genbank"))
            f.close()
            pathstofiles.append(pathtofile)
        p = subprocess.Popen(path_to_ape + ' ' + ' '.join(pathstofiles), shell=True)

    else: # no selection, open empty window
        p = subprocess.Popen(path_to_ape, shell=True)


