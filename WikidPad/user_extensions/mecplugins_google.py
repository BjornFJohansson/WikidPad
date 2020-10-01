#!/usr/bin/env python
# -*- coding: utf-8 -*-

WIKIDPAD_PLUGIN = (("MenuFunctions",1), ("ToolbarFunctions",1))

def describeMenuItems(wiki):
    return ((google,	    _(u"mecplugins|www|google search")	   , _(u"google")),
                )

def describeToolbarItems(wiki):
    return ((google,       _(u"google"),       _(u"google"),       "google"),
            )

def google(wiki,evt):    

    from urllib.parse import quote
    import webbrowser
    
    query = wiki.getActiveEditor().GetSelectedText()
    
    new = 2 # not really necessary, may be default on most modern browsers
    base_url = "http://www.google.com/?#q="

    final_url = base_url + quote(query)
    webbrowser.open(final_url, new=new)
    
    return