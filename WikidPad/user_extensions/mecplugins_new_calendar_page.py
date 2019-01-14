#!/usr/bin/env python
# -*- coding: utf-8 -*-
WIKIDPAD_PLUGIN = (("hooks", 1),)
import time
from   WikidPad.lib.pwiki.StringOps import strftimeUB
def newWikiWord(docPagePresenter, wikiWord):
    try:
        timestamp = time.mktime(time.strptime(wikiWord, "%Y-%m-%d"))
    except ValueError:
        return
    wds=["Monday","Tuesday", "Wednesday", "Thursday", "Friday", "Saturday","Sunday"]
    mns=['January','February','March','April','May','June','July','August','September','October','November', 'December']
    wd = wds[int(strftimeUB("%w",timestamp))-1]
    mn = mns[int(strftimeUB("%m",timestamp))-1]
    #newtitle = strftimeUB("%Y-%m-%d|{A} {B} %d|Week %W [alias: %d {B} %Y] [now] [someday] [todo_todo]\nhttps://calendar.google.com/calendar/r/week/%Y/%m/%d\n\ntodo:\ndone:\n\n".format(A=wd,B=mn), timestamp)
    newtitle = strftimeUB("%Y-%m-%d|{A} {B} %d|Week %W [alias: %d {B} %Y] [now] [someday] [todo_todo]\nhttps://calendar.google.com/calendar/r/week/%Y/%m/%d\n\n\n".format(A=wd,B=mn), timestamp)
    #underline = "-"*len(newtitle) + "---"
    newtitle+="\n"  #+underline
    #print(newtitle)
    docPagePresenter.getWikiDocument().createWikiPage(wikiWord,
                                                      suggNewPageTitle=newtitle)
    return


