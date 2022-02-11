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

    query = wiki.getActiveEditor().GetSelectedText() or wiki.getCurrentWikiWord()

    query = ' '.join(query.split())

    new = 2 # not really necessary, may be default on most modern browsers
    base_url = "http://www.google.com/search?q="

    final_url = base_url + quote(query)

    # print(final_url)

    # https://www.google.com/search?q=%22Stack+Exchange%22+OR+StackOverflow
    # http://www.google.com/search?q=%22Stack+Exchange%22+OR+StackOverflow
    # http://www.google.com/search?q=%22Stack%2BExchange%22%2BOR%2BStackOverflow
    # http://www.google.com/search?q=%22Stack%20Exchange%22%20OR%20StackOverflow

    webbrowser.open(final_url, new=new)

    return