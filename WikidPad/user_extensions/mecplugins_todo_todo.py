#!/usr/bin/env python
# -*- coding: utf-8 -*-

WIKIDPAD_PLUGIN = (("MenuFunctions",1),("ToolbarFunctions",1))

def describeMenuItems(wiki):
    return ((shortcut,_(u"mecplugins|Misc|todo_todo"),_(u"todo_todo")),)

def describeToolbarItems(wiki):
    return ((shortcut, _(u"todo_todo"), _(u"todo_todo"), u"spanner"),)

def shortcut(wiki, evt):
    openpages =  wiki.getMainAreaPanel().getDocPagePresenters()
    for page in openpages:
        if page.getWikiWord()=="todo_todo":
            wiki.getMainAreaPanel().showPresenter(page)
            return
    wiki.openWikiPage("todo_todo")
    return






