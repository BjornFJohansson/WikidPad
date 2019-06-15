#!/usr/bin/env python
# -*- coding: utf-8 -*-
WIKIDPAD_PLUGIN = (("MenuFunctions",1),)
def describeMenuItems(wiki):
    global nextNumber
    return ((rd, _("RELOAD"), _("RELOAD")),)
def rd(wiki, evt):
    wiki.reloadMenuPlugins()
    print("menu plugins reloaded\n")