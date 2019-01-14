#!/usr/bin/env python
# -*- coding: utf-8 -*-
##################################################
#  _______       _   _____  _             _
# |__   __|     | | |  __ \| |           (_)
#    | | ___ ___| |_| |__) | |_   _  __ _ _ _ __
#    | |/ _ | __| __|  ___/| | | | |/ _` | | '_ \
#    | |  __|__ \ |_| |    | | |_| | (_| | | | | |
#    |_|\___|___/\__|_|    |_|\__,_|\__, |_|_| |_|
#                                    __/ |
#                                   |___/
##################################################

WIKIDPAD_PLUGIN = (("MenuFunctions",1),)
#from . import mecplugins_ini
import wx
import time

def describeMenuItems(wiki):
    return ((test, _("test") + "\tCtrl-Shift-T", _("test")),)

def test(wiki,evt):
    if wiki.getCurrentWikiWord() is None:
        return
    
    langHelper = wx.GetApp().createWikiLanguageHelper( wiki.getWikiDefaultWikiLanguage() )
    
    bracketWords = langHelper.createLinkFromWikiWord
    
    parents = wiki.wikiData.getParentRelationships(wiki.getCurrentWikiWord())
    
    parents = [bracketWords(word, wikiPage=wiki.getWikiDocument().getWikiPage(wiki.getCurrentWikiWord())) for word in parents]
    
    wiki.getActiveEditor().AddText( "\n".join( sorted(parents) ) )
