#!/usr/bin/env python
# -*- coding: utf-8 -*-
WIKIDPAD_PLUGIN = (("MenuFunctions",1),)


def describeMenuItems(wiki):
    return ((version, _("mecplugins|about mec plugins"), _("about mec plugins")),)

def version(wiki, evt):

    from WikidPad.Consts import VERSION_STRING
    import os
    import wx
    import platform
    import sys
    
    try:
        import Bio
    except ImportError:
        class Bio:
            pass
        Bio.__version__ = "not available"
        
        

    message = "wikidPad version: {}\nPython version: {}\nwx versionx: {}\nBioPython version: {}\nPlatform: {}".format( VERSION_STRING,
                                                                                                                       sys.version,
                                                                                                                       wx.version(),
                                                                                                                       Bio.__version__,
                                                                                                                       platform.platform() )
    del Bio,sys,os,platform, VERSION_STRING

    slask = wiki.stdDialog("o", "Installed version of mec plugins",message, " ".join(message.splitlines()))

