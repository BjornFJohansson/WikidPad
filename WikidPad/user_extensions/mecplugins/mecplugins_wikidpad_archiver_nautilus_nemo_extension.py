#!/usr/bin/python3
# -*- coding: utf-8 -*-

import sys
print(sys.version)

import os
import time
import locale
import shutil
import datetime

try:
    from urllib.parse import unquote_plus
    from urllib.parse import urlsplit
except ImportError:
     from urllib import unquote_plus
     from urlparse import urlsplit

import gi

try: 
    gi.require_version('Nautilus', '3.0')
except ValueError:
    gi.require_version('Nemo', '3.0')

from gi.repository import GObject

try:
    from gi.repository import Nautilus as Verne
    fm = "Verne"
except ImportError:
    from gi.repository import Nemo     as Verne
    fm = "Nemo"

locale.setlocale(locale.LC_ALL, '')

class ColumnExtension(GObject.GObject, Verne.MenuProvider):

    def __init__(self):
        pass

    def menu_activate_cb(self, menu, files):
        today = str(datetime.date.today())
        today_dir = os.path.join("/home/bjorn/files/ARCHIVE/", today)

        try:
            os.makedirs(today_dir)
        except OSError:
            pass

        links= "\n\n" #"\n[file://{}]\n".format(today_dir)

        files = [f for f in files if not f.is_gone()]
        
        for file_ in files:
            uri = unquote_plus(file_.get_uri())
            src = urlsplit(uri).path
            name = os.path.split(src)[-1]
            dst = os.path.join(today_dir, name)
            shutil.move(src, dst)
            links+="[file:{}]\n".format(dst)

        wikipage = os.path.join("/home/bjorn/Dropbox/wikidata/", "{}.md".format(today)) #<-- ugly!

        if not os.path.exists(wikipage):
            header = time.strftime("## %Y-%m-%d|%A %B %d|Week %W\n[alias: %d %B %Y] [now]").decode(locale.getlocale()[1])

        else:
            header = ""

        with open(wikipage, "a") as myfile:
            myfile.write(header)
            myfile.write(links)


    def get_file_items(self, window, files):
        item = Verne.MenuItem(name=  "{}::wikidpad".format(fm),
                              label= "Save to WikidPad today {}".format(datetime.date.today()),
                              tip=   "wikidpad"
                                 )
        item.connect('activate', self.menu_activate_cb, files)
        return item,