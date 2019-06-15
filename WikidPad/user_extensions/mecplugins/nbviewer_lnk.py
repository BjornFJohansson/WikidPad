#!/usr/bin/env python2
import os
from urllib.parse import unquote_plus
import urllib.parse as parse  #from urllib import parse

import gi
gi.require_version('Gtk', '3.0')
gi.require_version('Gdk', '3.0')
gi.require_version('Nautilus', '3.0')
from gi.repository import GObject
from gi.repository import Gtk
from gi.repository import Gdk

try:
    from gi.repository import Nautilus as Verne
    fm = "Nautilus"
except ImportError:
    from gi.repository import Nemo     as Verne
    fm = "Nemo"

phead = "http://nbviewer.ipython.org/urls/dl.dropboxusercontent.com/u/1263722/"
lhead = "/home/bjorn/Dropbox/Public/"

class NBviewerExtension(GObject.GObject, Verne.MenuProvider):

    def __init__(self):
        pass

    def menu_activate_cb(self, menu, files):
        files = [f for f in files if not f.is_gone() and f.get_uri().endswith(".ipynb") and "/Public/" in os.path.realpath(parse.urlparse(f.get_uri()).path)]
        if not files:
            return
        clipboard = Gtk.Clipboard.get(Gdk.SELECTION_CLIPBOARD)
        text = ""
        for file_ in files:
            text+= phead + os.path.realpath(parse.urlparse( unquote_plus(file_.get_uri()) ).path).split(lhead)[1]+"\n"
        clipboard.set_text(text, -1)

    def get_file_items(self, window, files):

        item = Verne.MenuItem(name='{}::nbviewer_link'.format(fm),
                                 label='Copy NBviewer link',
                                 tip='copy link to nbviewer')
        item.connect('activate', self.menu_activate_cb, files)

        return item,


        
        
        
        
        #https://dl.dropboxusercontent.com/u/1263722/pydna-DNA-assembly/constructs/pCAPs_E_AgTEFt.py
        #http://nbviewer.ipython.org/urls/dl.dropboxusercontent.com/u/1263722/pydna-DNA-assembly/pydna-DNA-Assembly.ipynb
        #file:///home/bjorn/Dropbox/Public/pydna-DNA-assembly/pydna-DNA-Assembly.ipynb

        # SUPPORTED_FORMATS = 'image/jpeg', 'image/png'
        # We're only going to put ourselves on images context menus
        #if not file.get_mime_type() in SUPPORTED_FORMATS:
        #    return
        # Gnome can only handle file:
        # In the future we might want to copy the file locally
        # if file.get_uri_scheme() != 'file':

