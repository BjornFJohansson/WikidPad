#!/usr/bin/env python
# -*- coding: utf-8 -*-
WIKIDPAD_PLUGIN = (("MenuFunctions",1),)


def describeMenuItems(wiki):
    return ((version, _("mecplugins|about mec plugins"), _("about mec plugins")),)

def version(wiki, evt):
    from WikidPad.Consts import VERSION_STRING
    message = ''
    import os
    from . import mecplugins_ini

    try:
        f=open(os.path.join(mecplugins_ini.mecplugins_dir,"mecplugins_licenses","mecplugins_installation_log.txt"),'r')
        lines = f.read().splitlines()
        message += lines[-1]+"\n"
        f.close()

    except IOError:
        pass
    
    import wx
    import platform
    import sys
    
    try:
        import Bio
    except ImportError:
        class Bio:
            pass
        Bio.__version__ = "not available"
        
        

    message += "wikidPad version: {}\nPython version: {}\nwx versionx: {}\nBioPython version: {}\nPlatform: {}".format( VERSION_STRING,
                                                                                                                                 sys.version, 
                                                                                                                                 wx.version(),
                                                                                                                                 Bio.__version__,
                                                                                                                                 platform.platform() )
#    import sys
#    message += "Python version: "+sys.version+"\n"
#    import Bio
#    message +="BioPython version: "+Bio.__version__+"\n"
#    import platform
#    message +="Platform: "+platform.platform()+"\n"
    del Bio,sys, mecplugins_ini,os,platform, VERSION_STRING

    slask = wiki.stdDialog("o", "Installed version of mec plugins",message, " ".join(message.splitlines()))

