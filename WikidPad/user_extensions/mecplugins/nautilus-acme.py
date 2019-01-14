from os.path import join
from gi.repository import GObject, Nautilus

class Acme(GObject.GObject, Nautilus.MenuProvider):
    def __init__(self):
        pass

    def new_empty_file(self, menu, folder):
        with open(join(folder.get_uri().replace("file://", ""), "new_file"), 'w') as f:
            f.write('')
        return

    def get_background_items(self, window, current_folder):
        AcmeMenuItem = Nautilus.MenuItem(
            name="Acme::NewEmptyFile",
            label="New empty file",
            tip="New empty file"
        )

        AcmeMenuItem.connect('activate', self.new_empty_file, current_folder)

        return [AcmeMenuItem]
