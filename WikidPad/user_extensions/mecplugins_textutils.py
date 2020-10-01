#!/usr/bin/env python
# -*- coding: utf-8 -*-
###########################################
#  _______         _   _    _ _   _ _
# |__   __|       | | | |  | | | (_) |
#    | | _____  __| |_| |  | | |_ _| |___
#    | |/ _ \ \/ /| __| |  | | __| | / __|
#    | |  __/>  < | |_| |__| | |_| | \__ \
#    |_|\___/_/\_\ \__|\____/ \__|_|_|___/
###########################################
WIKIDPAD_PLUGIN = (("MenuFunctions",1),("ToolbarFunctions",1))
#WIKIDPAD_PLUGIN = (("MenuFunctions",1),)

def describeMenuItems(wiki):
    kb = wiki.getKeyBindings()
    return (	(dewrap, 	 _(u"mecplugins|Text utils|Dewrap selected text")+ u"\t" + kb.Plugin_dewrap , _(u"dewrap selection")),
                (expandtabs, _(u"mecplugins|Text utils|Expand tabs to spaces for selected text")     , _(u"expand tabs")),
                (togglecase, _(u"mecplugins|Text utils|Toggle case\tCtrl-U") , _(u"toggle case")),
                (wordcount,  _(u"mecplugins|Text utils|Count words in page") , _(u"count words")),
                )

def describeToolbarItems(wiki):
    return (    #(wordcount, 		_(u"Count words in page"), 	_(u"Count words in page"),	u"count"),
                #(togglecase, 		_(u"toggle case"), 		_(u"toggle case"), 		u"swap_case"),
		 (dewrap, 		_(u"dewrap"), 			_(u"dewrap"), 			u"mec_dewrap"),
                )


def expandtabs(wiki, evt):
    if wiki.getCurrentWikiWord() is None:
        return
    content = wiki.getActiveEditor().GetSelectedText()
    if not content:
        content = wiki.getActiveEditor().GetText()
    defaulttabsize=4
    tabsize=int(wiki.stdDialog("text", "Expand tabs", "use tab size:", additional=str(defaulttabsize)))
    #print tabsize
    expanded_content=content.expandtabs(tabsize)
    wiki.getActiveEditor().ReplaceSelection(expanded_content)

def dewrap(wiki, evt):
    start, end = wiki.getActiveEditor().GetSelection()
    if wiki.getCurrentWikiWord() is None:
        return
    content = wiki.getActiveEditor().GetSelectedText()+"\n\n"
    if not content:
        return
    dewrapped_content = []
    for p in content.split("\n\n"):
        if p.lstrip().rstrip().find(" ")!=-1:
            dewrapped_content.append(p.replace("\n"," "))
        else:
            dewrapped_content.append(p.replace("\n",""))
    dewrapped_content = "\n\n".join(dewrapped_content)
    wiki.getActiveEditor().ReplaceSelection(dewrapped_content)
    wiki.getActiveEditor().GotoPos(start)
    return

def togglecase(wiki, evt):
    start, end = wiki.getActiveEditor().GetSelection()
    if wiki.getCurrentWikiWord() is None:
        return
    content = wiki.getActiveEditor().GetSelectedText()
    if not content:
        content = wiki.getActiveEditor().GetText()

    if content.isupper():
        content=content.title()

    elif content.istitle():
        content=content.lower()

    elif content.islower():
        content=content.upper()

    else:
        content=content.lower()
    wiki.getActiveEditor().ReplaceSelection(content)
    wiki.getActiveEditor().SetSelection(start, end)
    return

def getCount(data):
    """
    Counts lines, words, chars in data
    """
    # count some stuff
    lines = len(data.split("\n"))
    words = len(data.split())
    chars = len(data)-lines+1
    blanks = data.count(" ")

    return lines, words, chars, blanks

def wordcount(wiki, evt):
    if wiki.getCurrentWikiWord() is None:
        return

    content = wiki.getActiveEditor().GetSelectedText()

    if not content:
        content = wiki.getActiveEditor().GetText()

    lines, words, chars, blanks = getCount(content)

    wiki.displayMessage("Wordcount",
                        "Lines\t\t\t\t: %s\n"
                        "Words\t\t\t\t: %s\n"
                        "Chars inc blanks\t\t: %s\n"
                        "Chars w/o blanks\t\t: %s\n" % (lines, words, chars, chars-blanks))
