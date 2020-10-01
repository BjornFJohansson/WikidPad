import sys
print(sys.version)

print("mecplugins_wikidpad_archiver_nautilus_nemo_extension.py")

# debug by running
#
# nautilus -q
# nautilus --no-desktop
#
# or
# nemo -q
# nemo --no-desktop


import os
import time
import locale
import shutil
import datetime

from urllib.parse import unquote_plus
from urllib.parse import urlsplit

import gi

try:
    gi.require_version('Nemo', '3.0')
    print("gi.require_version('Nemo', '3.0')")
except ValueError:
    gi.require_version('Nautilus', '3.0')
    print("gi.require_version('Nautilus', '3.0')")

from gi.repository import GObject

try:
    from gi.repository import Nemo     as Verne
    fm = "Nemo"
except ImportError:
    from gi.repository import Nautilus as Verne
    fm = "Nautilus"

print(fm)

locale.setlocale(locale.LC_ALL, '')
#locale.setlocale(locale.LC_ALL, "pt_PT")

class ColumnExtension(GObject.GObject, Verne.MenuProvider):

    def __init__(self):
        pass

    def get_file_items(self, window, files):
        item = Verne.MenuItem(name=  f"{fm}::wikidpad",
                              label= "Save to WikidPad {}".format(datetime.date.today()),
                              tip=   "wikidpad",
                              icon=  ''
                                 )
        item.connect('activate', self.menu_activate_cb, files)
        return item,

    def menu_activate_cb(self, menu, files):
        today = str(datetime.date.today())
        print(today)
        today_dir = os.path.join("/home/bjorn/files/ARCHIVE/", today)
        print(today_dir)
        try:
            os.makedirs(today_dir)
        except OSError:
            pass

        links= "\n"

        files = [f for f in files if not f.is_gone()]
        print()
        for file_ in files:
            uri = unquote_plus(file_.get_uri())
            print(uri)
            src = urlsplit(uri).path
            print(src)
            name = os.path.split(src)[-1]
            print(name)
            dst = os.path.join(today_dir, name)
            print(dst)
            shutil.move(src, dst)
            link = "[file:{}]\n".format(dst)
            print(link)
            links+=link
            print()


        wikipage = os.path.join("/home/bjorn/Dropbox/wikidata/", f"{today}.md") #<-- ugly!

        header = ""
        if not os.path.exists(wikipage):
            header = time.strftime("## %Y-%m-%d|%A %B %d|Week %W [alias: %d %B %Y] [now] [someday] [todo_todo]\nhttps://calendar.google.com/calendar/r/week/%Y/%m/%d\n\n\n") #.encode()  # locale.getlocale()[1]
            print(header)
        else:
            print("no header")

        with open(wikipage, "a") as f:
            f.write(header)
            f.write(links)


        print( "File size ", os.stat(wikipage)[6] )

