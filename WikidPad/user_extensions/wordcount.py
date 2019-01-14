#!/usr/bin/env python
# -*- coding: utf-8 -*-

# version 0.2.4 (2008-10-18) Simple wordcount plugin by bousch <bousch@gmail.com>
# USE AT YOUR OWN RISK, NO WARRANTY WHATSOEVER.
#
# history: 
#
#   0.2.4
#       if text is selected only the selected part is counted (Bjorn Johansson)
#
#   0.2.3
#       cosmetic changes
#
#   0.2.2:
#       aliases are not counted anymore as they duplicate the original
#
#   previous:
#       2008-01-24 minor refactoring and comments
#       2008-01-23 fixed problem with aliases
#
# Installation:
# - create a folder called user_extensions below your wikidPad program folder
# - put this file in the user_extensions folder and restart wikidpad
#
# Wordcount ripped from:
# http://en.literateprograms.org/Word_count_%28Python%29
#
# Plugin based on:
# Example plugin for EditorFunctions type plugins
# The functionality was originally implemented by endura29 <endura29@gmail.com>
# Cosmetic changes by schnullibullihulli (2006-06-01)
#
WIKIDPAD_PLUGIN = (("MenuFunctions",1), ("ToolbarFunctions",1))

from WikidPad.lib.pwiki.StringOps import mbcsEnc
from WikidPad.lib.pwiki.WikiExceptions import WikiFileNotFoundException

def describeMenuItems(wiki):
    """
    wiki -- Calling PersonalWikiFrame
    Returns a sequence of tuples to describe the menu items, where each must
    contain (in this order):
        - callback function
        - menu item string
        - menu item description (string to show in status bar)
    It can contain the following additional items (in this order), each of
    them can be replaced by None:
        - icon descriptor (see below, if no icon found, it won't show one)
        - menu item id.

    The  callback function  must take 2 parameters:
        wiki - Calling PersonalWikiFrame
        evt - wxCommandEvent

    An  icon descriptor  can be one of the following:
        - a wxBitmap object
        - the filename of a bitmap (if file not found, no icon is used)
        - a tuple of filenames, first existing file is used
    """
    return ((wordcount, _("Count words in page") + "\tCtrl-Shift-W", _("Count words in page")),
            #(countWordsInTree, _(u"Count words in tree") + "\tCtrl-Alt-Shift-W", _(u"Count words in tree")),
            )


def describeToolbarItems(wiki):
    """
    wiki -- Calling PersonalWikiFrame
    Returns a sequence of tuples to describe the menu items, where each must
    contain (in this order):
        - callback function
        - tooltip string
        - tool item description (string to show in status bar)
        - icon descriptor (see below, if no icon found, a default icon
            will be used)
    It can contain the following additional items (in this order), each of
    them can be replaced by None:
        - tool id.

    The  callback function  must take 2 parameters:
        wiki - Calling PersonalWikiFrame
        evt - wxCommandEvent

    An  icon descriptor  can be one of the following:
        - a wxBitmap object
        - the filename of a bitmap (if file not found, a default icon is used)
        - a tuple of filenames, first existing file is used
    """
    return ((wordcount, _("Count words in page"), _("Count words in page"), ("count", "count")),
            #(countWordsInTree, _(u"Count words in tree"), _(u"Count words in tree"), ("count", "mec_count")),
            )

def getCount(data):
    """
    Counts lines, words, chars in data
    """
    # count some stuff
    lines = len(data.split("\n"))
    words = len(data.split())
    chars = len(data)
    return lines, words, chars

def wordcount(wiki, evt):
    if wiki.getCurrentWikiWord() is None:
        return

    content = wiki.getActiveEditor().GetSelectedText()

    if len(content)<1:
        content = wiki.getActiveEditor().GetText()
    lines, words, chars = getCount(content)
    
    wiki.displayMessage("Wordcount", 
        "Lines\t: %s\n"
        "Words\t: %s\n"
        "Chars\t: %s\n" % (lines, words, chars))


def countWordsInTree(wiki, evt):
    """
    Count words in a tree of pages. This is not optimized for speed when
    there are cyclic references in the pages.
    """
    
    node = wiki.getCurrentWikiWord()
    # Leave when we have no current page
    if node is None:
        return

    wikiData = wiki.getWikiData()
    
    def nameOf(aNode):
        """
        Gets the unaliased name of a node.
        """
        if wikiData.isAlias(aNode):
            return wikiData.getAliasesWikiWord(aNode)
        else:
            return aNode
            
        
    def childrenOf(currentnode, nodelist):
        """
        Builds a list of all children of the node.
        Recursively calls itself.
        """
        
        # Add the current node to the list
        if nameOf(currentnode) not in nodelist:
            nodelist.append(nameOf(currentnode))
        
        # Get the children of the current node
        children = wikiData.getChildRelationships(nameOf(currentnode), True)
        
        # Loop through the children
        for child in children:
            # Only add the child if not in the list
            # and call this function again for this child
            if nameOf(child) not in nodelist:
                nodelist.append(nameOf(child))
                nodelist = childrenOf(nameOf(child), nodelist)
        
        return nodelist
    
    
    # get all children
    pages = childrenOf(node, [])

    # initialize count
    total_lines = 0
    total_words = 0
    total_chars = 0
    
    # loop through the pages
    for page in pages:

        try:
            # get the content of the page
            content = mbcsEnc(wikiData.getContent(page))[0]
    
            # count some stuff
            lines, words, chars = getCount(content)
            total_lines += lines
            total_words += words
            total_chars += chars

        except WikiFileNotFoundException:
            wiki.displayMessage("Error", "An error has occured when retrieving content, "
                "the page %s might not be saved yet." % page)
            return

    # display the results
    wiki.displayMessage("Tree wordcount", 
        "Pages:\t%s\n"
        "Lines:\t%s\n"
        "Words:\t%s\n"
        "Chars:\t%s" % (len(pages), total_lines, total_words, total_chars))
