#!/usr/bin/env python
# -*- coding: utf-8 -*-

WIKIDPAD_PLUGIN = (("MenuFunctions",1),)
#from . import mecplugins_ini
import wx
import time

def describeMenuItems(wiki):
    return ((here, _("mecplugins|links here"), _("links here")),)

def here(wiki,evt):
    if wiki.getCurrentWikiWord() is None:
        return
    
    langHelper = wx.GetApp().createWikiLanguageHelper( wiki.getWikiDefaultWikiLanguage() )
    
    bracketWords = langHelper.createLinkFromWikiWord
    
    #wiki.getActiveEditor().saveLoadedDocPage()

    parents = wiki.wikiData.getParentRelationships(wiki.getCurrentWikiWord())
    
    parents = [bracketWords(word,) for word in parents]
    
    wiki.getActiveEditor().AddText( "\n".join( sorted(parents) ) )
