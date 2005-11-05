import ConfigParser
import os
from os.path import *
from time import localtime, time

from wxPython.wx import *
from wxPython.stc import *
from wxPython.html import *

from WikiData import *
from WikiTxtCtrl import *
from WikiTreeCtrl import *
from WikiPreview import *
from Exporters import *
import WikiFormatting
import Crypt
from Config import *

class PersonalWikiFrame(wxFrame):
    def __init__(self, parent, id, title, wikiToOpen, wikiWordToOpen):
        wxFrame.__init__(self, parent, -1, title, size = (700, 550),
                         style=wxDEFAULT_FRAME_STYLE|wxNO_FULL_REPAINT_ON_RESIZE)

        # where is the WikidPad.config file
        globalConfigDir = None
        self.wikiAppDir = None
        
        try:            
            self.wikiAppDir = dirname(abspath(sys.argv[0]))
            if not self.wikiAppDir:
                self.wikiAppDir = "C:\Program Files\WikidPad"
            
            homeDir = os.environ.get("HOME")
            if homeDir and exists(homeDir):
                globalConfigDir = homeDir
            else:
                user = os.environ.get("USERNAME")
                if user:
                    homeDir = "c:\Documents And Settings\%s" % user
                    if homeDir and exists(homeDir):
                        globalConfigDir = homeDir                
        except Exception, e:
            self.displayErrorMessage("Error initializing environment", e)

        if not globalConfigDir:
            globalConfigDir = self.wikiAppDir

        if not globalConfigDir or not exists(globalConfigDir):
            globalConfigDir = "C:\Windows"

        if not globalConfigDir or not exists(globalConfigDir):
            self.displayErrorMessage("Error initializing environment, couldn't locate global config directory", "Shutting Down")
            self.Close()
            
        # initialize some variables
        self.globalConfigDir = globalConfigDir
        self.globalConfigLoc = join(globalConfigDir, "WikidPad.config")
        self.globalConfig = ConfigParser.ConfigParser()
        self.wikiPadHelp = join(self.wikiAppDir, 'WikidPadHelp', 'WikidPadHelp.wiki')

        # defaults
        self.config = None
        self.wikiData = None
        self.wikiConfigFile = None
        self.currentWikiWord = None
        self.currentWikiPage = None
        self.historyPosition = 0
        self.wikiWordHistory = []
        self.lastCursorPositionInPage = {}
        self.iconLookup = {}
        self.wikiHistory = []

        # load extensions
        self.loadExtensions()

        # initialize the wiki syntax
        WikiFormatting.initialize(self.wikiSyntax)

        # trigger hook            
        self.wikidPadHooks.startup(self)

        # if it already exists read it in
        if (exists(self.globalConfigLoc)):            
            self.globalConfig.read(self.globalConfigLoc)
        else:
            self.createDefaultGlobalConfig()

        # wiki history
        if (self.globalConfig.has_option("main", "wiki_history")):
            self.wikiHistory = self.globalConfig.get("main", "wiki_history").split(";")

        # resize the window to the last position/size
        screenX = wxSystemSettings_GetMetric(wxSYS_SCREEN_X)
        screenY = wxSystemSettings_GetMetric(wxSYS_SCREEN_Y)

        sizeX = int(self.globalConfig.get("main", "size_x"))
        sizeY = int(self.globalConfig.get("main", "size_y"))

        # don't let the window be > than the size of the screen
        if sizeX > screenX:
            sizeX = screenX-20
        if sizeY > screenY:
            currentY = screenY-20

        # set the size
        self.SetSize(wxSize(sizeX, sizeY))

        currentX = int(self.globalConfig.get("main", "pos_x"))
        currentY = int(self.globalConfig.get("main", "pos_y"))

        # fix any crazy screen positions
        if currentX < 0:
            currentX = 10
        if currentY < 0:
            currentY = 10
        if currentX > screenX:
            currentX = screenX-100
        if currentY > screenY:
            currentY = screenY-100
        
        self.SetPosition(wxPoint(currentX, currentY))

        # get the wrap mode setting
        self.wrapMode = True
        if (self.globalConfig.has_option("main", "wrap_mode")):
            self.wrapMode = self.globalConfig.getboolean("main", "wrap_mode")

        # get the position of the splitter
        self.lastSplitterPos = 170
        if (self.globalConfig.has_option("main", "splitter_pos")):
            self.lastSplitterPos = int(self.globalConfig.get("main", "splitter_pos"))

        # is autosave on
        self.autoSave = True
        if (self.globalConfig.has_option("main", "auto_save")):
            self.autoSave = self.globalConfig.getboolean("main", "auto_save")

        # are indentationGuides enabled
        self.indentationGuides = True
        if (self.globalConfig.has_option("main", "indentation_guides")):
            self.indentationGuides = self.globalConfig.getboolean("main", "indentation_guides")
        
        # set the locale
        locale = wxLocale()
        self.locale = locale.GetCanonicalName()

        # initialize the GUI
        self.initializeGui()

        # get the default font for the editor
        self.defaultEditorFont = faces["mono"]
        if (self.globalConfig.has_option("main", "font")):
            self.defaultEditorFont = self.globalConfig.get("main", "font")

        # this will keep track of the last font used in the editor
        self.lastEditorFont = None

        # should WikiWords be enabled or not for the current wiki
        self.wikiWordsEnabled = True

        # if a wiki to open wasn't passed in used the last_wiki from the global config
        if not wikiToOpen:
            if self.globalConfig.has_option("main", "last_wiki"):
                wikiToOpen = self.globalConfig.get("main", "last_wiki")

        # if a wiki to open is set open it
        if wikiToOpen:
            if exists(wikiToOpen):
                self.openWiki(wikiToOpen, wikiWordToOpen)
            else:
                self.statusBar.SetStatusText("Couldn't open last wiki: %s" % wikiToOpen, 0)

        # check for expiration
        self.checkForRegistration()

        # set the focus to the editor
        if self.vertSplitter.GetSashPosition() < 2:
            self.editor.SetFocus()
        
    def checkForRegistration(self):
        "Checks that this wiki pad is registered"

        if self.globalConfig.has_section("registration"):
            if self.globalConfig.has_option("registration", "code"):
                code = self.globalConfig.get("registration", "code")
                if code == REGISTRATION_CODE:
                    print "Registration code valid"
                    return

        # check if the old method of registration verification should be used
        if self.globalConfig.has_section("registration"):
            if self.globalConfig.has_option("registration", "expires"):
                self.oldCheckForRegistration()
                return

        # if the expiration date is not in the config add it
        if not self.globalConfig.has_section("registration"):
            self.globalConfig.add_section("registration")
        if not self.globalConfig.has_option("registration", "expireson"):
            expiresTime = int(time()) + 2592000 # add 30 days
            expires = Crypt.Encrypt(str(expiresTime), "4319")
            self.globalConfig.set("registration", "expireson", expires)

        today = time()
        expiresOn = today
        
        expiresStr = self.globalConfig.get("registration", "expireson")
        try:
            expiresStr = Crypt.Decrypt(expiresStr, "4319")
            expiresOn = int(expiresStr)
        except:
            self.displayErrorMessage("Error reading config file, expiration date may have been tampered with")
            self.Close()
                    
        if today >= expiresOn:
            self.showRegistrationDialog(expired=True)
        else:
            daysLeft = int(round((expiresOn - today) / 86400))
            dlg_m = wxMessageDialog(self, "You have %s evaluation days left." % daysLeft, "%s evaluation days left" % daysLeft, wxOK)
            dlg_m.ShowModal()
            dlg_m.Destroy()


    def oldCheckForRegistration(self):
        "Checks that this wiki pad is registered"

        if self.globalConfig.has_section("registration"):
            if self.globalConfig.has_option("registration", "code"):
                code = self.globalConfig.get("registration", "code")
                if code == REGISTRATION_CODE:
                    print "Registration code valid"
                    return

        # if the expiration date is not in the config add it
        if not self.globalConfig.has_section("registration"):
            self.globalConfig.add_section("registration")
        if not self.globalConfig.has_option("registration", "expires"):
            currentDayOfYear = localtime().tm_yday + 30
            expires = Crypt.Encrypt(str(currentDayOfYear), "4318")
            self.globalConfig.set("registration", "expires", expires)

        today = localtime().tm_yday
        expiresOn = today
        
        expiresStr = self.globalConfig.get("registration", "expires")
        try:
            expiresStr = Crypt.Decrypt(expiresStr, "4318")
            expiresOn = int(expiresStr)
        except:
            self.displayErrorMessage("Error reading config file, expiration date may have been tampered with")
            self.Close()
                    

        # can't get the expiration date without a database
        currentDayOfYear = localtime().tm_yday

        if currentDayOfYear >= expiresOn:
            self.showRegistrationDialog(expired=True)
        else:
            daysLeft = expiresOn - currentDayOfYear
            dlg_m = wxMessageDialog(self, "You have %s evaluation days left." % daysLeft, "%s evaluation days left" % daysLeft, wxOK)
            dlg_m.ShowModal()
            dlg_m.Destroy()


    def loadExtensions(self):
        self.wikidPadHooks = self.getExtension('WikidPadHooks', 'WikidPadHooks.py')
        self.keyBindings = self.getExtension('KeyBindings', 'KeyBindings.py')
        self.evalLib = self.getExtension('EvalLibrary', 'EvalLibrary.py')
        self.wikiSyntax = self.getExtension('SyntaxLibrary', 'WikiSyntax.py')

    def getExtension(self, extensionName, fileName):
        extensionFileName = join(self.wikiAppDir, 'user_extensions', fileName)
        if not exists(extensionFileName):
            extensionFileName = join(self.wikiAppDir, 'extensions', fileName)
        extensionFile = open(extensionFileName)
        return importCode(extensionFile, extensionName)        

    def createDefaultGlobalConfig(self):
        self.globalConfig.add_section("main")
        self.globalConfig.set("main", "wiki_history", self.wikiPadHelp)
        self.globalConfig.set("main", "last_wiki", self.wikiPadHelp)
        curSize = self.GetSize()
        self.globalConfig.set("main", "size_x", str(curSize.x))
        self.globalConfig.set("main", "size_y", str(curSize.y))
        curPos = self.GetPosition()
        self.globalConfig.set("main", "pos_x", str(curPos.x))
        self.globalConfig.set("main", "pos_y", str(curPos.y))
        self.globalConfig.set("main", "splitter_pos", '170')
        self.globalConfig.set("main", "zoom", '0')
        self.globalConfig.set("main", "last_active_dir", os.getcwd())
        self.globalConfig.set("main", "font", "Courier New")
        self.globalConfig.set("main", "wrap_mode", "0")
        self.globalConfig.set("main", "auto_save", "1")
        self.globalConfig.set("main", "indentation_guides", "1")
                
    def initializeGui(self):
        "initializes the gui environment"
        
        # ------------------------------------------------------------------------------------
        # load the icons the program will use
        # ------------------------------------------------------------------------------------

        # add the gif handler for gif icon support
        wxImage_AddHandler(wxGIFHandler())        
        # create the image icon list
        iconList = wxImageList(16, 16)
        # default icon is page.gif
        icons = ['page.gif']
        # add the rest of the icons        
        icons.extend([file for file in os.listdir(join(self.wikiAppDir, "icons"))
                      if file.endswith('.gif') and file != 'page.gif'])
                      
        for icon in icons:
            iconFile = join(self.wikiAppDir, "icons", icon)
            bitmap = wxBitmap(iconFile, wxBITMAP_TYPE_GIF)
            try:
                id = iconList.Add(bitmap, wxNullBitmap)
                if id >= 0:
                    self.iconLookup[icon.replace('.gif', '')] = (id, bitmap)
                else:                    
                    sys.stderr.write("couldn't load icon %s\n" % iconFile)
            except Exception, e:
                sys.stderr.write("couldn't load icon %s\n" % iconFile)

        # ------------------------------------------------------------------------------------
        # Set up menu bar for the program.
        # ------------------------------------------------------------------------------------
        self.mainmenu = wxMenuBar()   # Create menu bar.

        wikiMenu=wxMenu()                                

        menuID=wxNewId()
        wikiMenu.Append(menuID, '&New\t' + self.keyBindings.NewWiki, 'New Wiki')
        EVT_MENU(self, menuID, self.OnWikiNew)

        menuID=wxNewId()                             
        wikiMenu.Append(menuID, '&Open\t' + self.keyBindings.OpenWiki, 'Open Wiki')
        EVT_MENU(self, menuID, self.OnWikiOpen)

        self.recentWikisMenu = wxMenu()
        wikiMenu.AppendMenu(wxNewId(), '&Recent', self.recentWikisMenu)

        # init the list of items
        for wiki in self.wikiHistory:
            menuID=wxNewId()
            self.recentWikisMenu.Append(menuID, wiki)
            EVT_MENU(self, menuID, self.OnSelectRecentWiki)

        wikiMenu.AppendSeparator()

        menuID=wxNewId()
        menuItem = wxMenuItem(wikiMenu, menuID, '&Search Wiki\t' + self.keyBindings.SearchWiki, 'Search Wiki')
        (id, bitmap) = self.iconLookup["tb_lens"]
        menuItem.SetBitmap(bitmap)
        wikiMenu.AppendItem(menuItem)
        EVT_MENU(self, menuID, lambda evt: self.showSearchDialog())

        menuID=wxNewId()                              
        wikiMenu.Append(menuID, '&View Saved Searches', 'View Saved Searches')
        EVT_MENU(self, menuID, lambda evt: self.showSavedSearchesDialog())

        menuID=wxNewId()
        wikiMenu.Append(menuID, '&View Bookmarks\t' + self.keyBindings.ViewBookmarks, 'View Bookmarks')
        EVT_MENU(self, menuID, lambda evt: self.viewBookmarks())

        wikiMenu.AppendSeparator()

        menuID=wxNewId()
        showTreeCtrlMenuItem = wxMenuItem(wikiMenu, menuID, "&Show Tree Control\t" + self.keyBindings.ShowTreeControl, "Show Tree Control", wxITEM_CHECK)            
        wikiMenu.AppendItem(showTreeCtrlMenuItem)
        EVT_MENU(self, menuID, lambda evt: self.setShowTreeControl(showTreeCtrlMenuItem.IsChecked()))

        menuID=wxNewId()
        autoSaveMenuItem = wxMenuItem(wikiMenu, menuID, "Auto Save Enabled", "Auto Save Enabled", wxITEM_CHECK)            
        wikiMenu.AppendItem(autoSaveMenuItem)
        EVT_MENU(self, menuID, lambda evt: self.setAutoSave(autoSaveMenuItem.IsChecked()))

        wikiMenu.AppendSeparator()

        exportWikisMenu = wxMenu()
        wikiMenu.AppendMenu(wxNewId(), 'Export', exportWikisMenu)

        menuID=wxNewId()
        exportWikisMenu.Append(menuID, 'Export Wiki as Single HTML Page', 'Export As Single HTML Page')
        EVT_MENU(self, menuID, lambda evt: self.exportWiki(ExportTypes.WikiToSingleHtmlPage))

        menuID=wxNewId()
        exportWikisMenu.Append(menuID, 'Export Wiki as Set of HTML Pages', 'Export Wiki As Set of HTML Pages')
        EVT_MENU(self, menuID, lambda evt: self.exportWiki(ExportTypes.WikiToSetOfHtmlPages))

        menuID=wxNewId()
        exportWikisMenu.Append(menuID, 'Export Current Wiki Word as HTML Page', 'Export Current Wiki Word as HTML Page')
        EVT_MENU(self, menuID, lambda evt: self.exportWiki(ExportTypes.WikiWordToHtmlPage))

        menuID=wxNewId()
        exportWikisMenu.Append(menuID, 'Export Sub-Tree as Single HTML Page', 'Export Sub-Tree as Single HTML Page')
        EVT_MENU(self, menuID, lambda evt: self.exportWiki(ExportTypes.WikiSubTreeToSingleHtmlPage))

        menuID=wxNewId()
        exportWikisMenu.Append(menuID, 'Export Sub-Tree as Set of HTML Pages', 'Export Sub-Tree as Set of HTML Pages')
        EVT_MENU(self, menuID, lambda evt: self.exportWiki(ExportTypes.WikiSubTreeToSetOfHtmlPages))

        menuID=wxNewId()
        exportWikisMenu.Append(menuID, 'Export Wiki as XML', 'Export Wiki as XML')
        EVT_MENU(self, menuID, lambda evt: self.exportWiki(ExportTypes.WikiToXml))

        menuID=wxNewId()
        wikiMenu.Append(menuID, '&Rebuild Wiki', 'Rebuild this wiki')
        EVT_MENU(self, menuID, lambda evt: self.rebuildWiki())

        wikiMenu.AppendSeparator()

        menuID=wxNewId()
        wikiMenu.Append(menuID, 'E&xit', 'Exit')
        EVT_MENU(self, menuID, lambda evt: self.Close())

        wikiWordMenu=wxMenu()                                

        menuID=wxNewId()                              
        menuItem = wxMenuItem(wikiWordMenu, menuID, '&Open\t' + self.keyBindings.OpenWikiWord, 'Open Wiki Word')
        (id, bitmap) = self.iconLookup["tb_doc"]
        menuItem.SetBitmap(bitmap)
        wikiWordMenu.AppendItem(menuItem)
        EVT_MENU(self, menuID, lambda evt: self.showWikiWordOpenDialog())

        menuID=wxNewId()                              
        menuItem = wxMenuItem(wikiWordMenu, menuID, '&Save\t' + self.keyBindings.Save, 'Save Current Wiki Word')
        (id, bitmap) = self.iconLookup["tb_save"]
        menuItem.SetBitmap(bitmap)
        wikiWordMenu.AppendItem(menuItem)
        EVT_MENU(self, menuID, lambda evt: self.saveCurrentWikiPage())

        menuID=wxNewId()                              
        menuItem = wxMenuItem(wikiWordMenu, menuID, '&Rename\t' + self.keyBindings.Rename, 'Rename Current Wiki Word')
        (id, bitmap) = self.iconLookup["tb_rename"]
        menuItem.SetBitmap(bitmap)
        wikiWordMenu.AppendItem(menuItem)
        EVT_MENU(self, menuID, lambda evt: self.showWikiWordRenameDialog())

        menuID=wxNewId()                              
        menuItem = wxMenuItem(wikiWordMenu, menuID, '&Delete\t' + self.keyBindings.Delete, 'Delete Wiki Word')
        (id, bitmap) = self.iconLookup["tb_delete"]
        menuItem.SetBitmap(bitmap)
        wikiWordMenu.AppendItem(menuItem)
        EVT_MENU(self, menuID, lambda evt: self.showWikiWordDeleteDialog())

        menuID=wxNewId()                              
        menuItem = wxMenuItem(wikiWordMenu, menuID, 'Add Bookmark\t' + self.keyBindings.AddBookmark, 'Add Bookmark to Page')
        (id, bitmap) = self.iconLookup["pin"]
        menuItem.SetBitmap(bitmap)
        wikiWordMenu.AppendItem(menuItem)
        EVT_MENU(self, menuID, lambda evt: self.insertAttribute("bookmarked", "true"))

        wikiWordMenu.AppendSeparator()

        menuID=wxNewId()
        wikiWordMenu.Append(menuID, '&Activate Link/Word\t' + self.keyBindings.ActivateLink, 'Activate Link/Word')
        EVT_MENU(self, menuID, lambda evt: self.editor.activateLink())

        menuID=wxNewId()
        wikiWordMenu.Append(menuID, '&View Parents\t' + self.keyBindings.ViewParents, 'View Parents Of Current Wiki Word')
        EVT_MENU(self, menuID, lambda evt: self.viewParents(self.currentWikiWord))

        menuID=wxNewId()
        wikiWordMenu.Append(menuID, '&View Parentless Nodes\t' + self.keyBindings.ViewParentless, 'View nodes with no parent relations')
        EVT_MENU(self, menuID, lambda evt: self.viewParentLess())

        menuID=wxNewId()
        wikiWordMenu.Append(menuID, '&View Children\t' + self.keyBindings.ViewChildren, 'View Children Of Current Wiki Word')
        EVT_MENU(self, menuID, lambda evt: self.viewChildren(self.currentWikiWord))

        menuID=wxNewId()
        menuItem = wxMenuItem(wikiWordMenu, menuID, 'Synchronize with tree', 'Find the current wiki word in the tree')
        (id, bitmap) = self.iconLookup["tb_cycle"]
        menuItem.SetBitmap(bitmap)
        wikiWordMenu.AppendItem(menuItem)
        EVT_MENU(self, menuID, lambda evt: self.findCurrentWordInTree())

        historyMenu=wxMenu()                                

        menuID=wxNewId()
        historyMenu.Append(menuID, '&View History\t' + self.keyBindings.ViewHistory, 'View History')
        EVT_MENU(self, menuID, lambda evt: self.viewHistory())

        menuID=wxNewId()
        historyMenu.Append(menuID, '&Up History\t' + self.keyBindings.UpHistory, 'Up History')
        EVT_MENU(self, menuID, lambda evt: self.viewHistory(-1))

        menuID=wxNewId()
        historyMenu.Append(menuID, '&Down History\t' + self.keyBindings.DownHistory, 'Down History')
        EVT_MENU(self, menuID, lambda evt: self.viewHistory(1))

        menuID=wxNewId()
        menuItem = wxMenuItem(historyMenu, menuID, '&Back\t' + self.keyBindings.GoBack, 'Go Back')
        (id, bitmap) = self.iconLookup["tb_back"]
        menuItem.SetBitmap(bitmap)
        historyMenu.AppendItem(menuItem)
        EVT_MENU(self, menuID, lambda evt: self.goInHistory(-1))

        menuID=wxNewId()
        menuItem = wxMenuItem(historyMenu, menuID, '&Forward\t' + self.keyBindings.GoForward, 'Go Forward')
        (id, bitmap) = self.iconLookup["tb_forward"]
        menuItem.SetBitmap(bitmap)
        historyMenu.AppendItem(menuItem)
        EVT_MENU(self, menuID, lambda evt: self.goInHistory(1))

        formattingMenu=wxMenu()                                

        menuID=wxNewId()
        menuItem = wxMenuItem(formattingMenu, menuID, '&Bold\t' + self.keyBindings.Bold, 'Bold')
        (id, bitmap) = self.iconLookup["tb_bold"]
        menuItem.SetBitmap(bitmap)
        formattingMenu.AppendItem(menuItem)
        EVT_MENU(self, menuID, lambda evt: self.keyBindings.makeBold(self.editor))

        menuID=wxNewId()
        menuItem = wxMenuItem(formattingMenu, menuID, '&Italic\t' + self.keyBindings.Italic, 'Italic')
        (id, bitmap) = self.iconLookup["tb_italic"]
        menuItem.SetBitmap(bitmap)
        formattingMenu.AppendItem(menuItem)
        EVT_MENU(self, menuID, lambda evt: self.keyBindings.makeItalic(self.editor))

        menuID=wxNewId()
        menuItem = wxMenuItem(formattingMenu, menuID, '&Heading\t' + self.keyBindings.Heading, 'Add Heading')
        (id, bitmap) = self.iconLookup["tb_heading"]
        menuItem.SetBitmap(bitmap)
        formattingMenu.AppendItem(menuItem)
        EVT_MENU(self, menuID, lambda evt: self.keyBindings.addHeading(self.editor))

        menuID=wxNewId()
        menuItem = wxMenuItem(formattingMenu, menuID, 'Insert Date\t' + self.keyBindings.InsertDate, 'Insert Date')
        (id, bitmap) = self.iconLookup["date"]
        menuItem.SetBitmap(bitmap)
        formattingMenu.AppendItem(menuItem)
        EVT_MENU(self, menuID, lambda evt: self.editor.AddText(self.evalLib.now()))

        formattingMenu.AppendSeparator()

        menuID=wxNewId()
        menuItem = wxMenuItem(formattingMenu, menuID, 'Cu&t\t' + self.keyBindings.Cut, 'Cut')
        (id, bitmap) = self.iconLookup["tb_cut"]
        menuItem.SetBitmap(bitmap)
        formattingMenu.AppendItem(menuItem)
        EVT_MENU(self, menuID, lambda evt: self.editor.CmdKeyExecute(wxSTC_CMD_CUT))

        menuID=wxNewId()
        menuItem = wxMenuItem(formattingMenu, menuID, '&Copy\t' + self.keyBindings.Copy, 'Copy')
        (id, bitmap) = self.iconLookup["tb_copy"]
        menuItem.SetBitmap(bitmap)
        formattingMenu.AppendItem(menuItem)
        EVT_MENU(self, menuID, lambda evt: self.editor.CmdKeyExecute(wxSTC_CMD_COPY))

        menuID=wxNewId()
        menuItem = wxMenuItem(formattingMenu, menuID, 'Copy to &ScratchPad\t' + self.keyBindings.CopyToScratchPad, 'Copy Text to ScratchPad')
        (id, bitmap) = self.iconLookup["tb_copy"]
        menuItem.SetBitmap(bitmap)
        formattingMenu.AppendItem(menuItem)
        EVT_MENU(self, menuID, lambda evt: self.editor.snip())

        menuID=wxNewId()
        menuItem = wxMenuItem(formattingMenu, menuID, '&Paste\t' + self.keyBindings.Paste, 'Paste')
        (id, bitmap) = self.iconLookup["tb_paste"]
        menuItem.SetBitmap(bitmap)
        formattingMenu.AppendItem(menuItem)
        EVT_MENU(self, menuID, lambda evt: self.editor.CmdKeyExecute(wxSTC_CMD_PASTE))

        formattingMenu.AppendSeparator()

        menuID=wxNewId()
        menuItem = wxMenuItem(formattingMenu, menuID, '&Undo\t' + self.keyBindings.Undo, 'Undo')
        formattingMenu.AppendItem(menuItem)
        EVT_MENU(self, menuID, lambda evt: self.editor.CmdKeyExecute(wxSTC_CMD_UNDO))

        menuID=wxNewId()
        menuItem = wxMenuItem(formattingMenu, menuID, '&Redo\t' + self.keyBindings.Redo, 'Redo')
        formattingMenu.AppendItem(menuItem)
        EVT_MENU(self, menuID, lambda evt: self.editor.CmdKeyExecute(wxSTC_CMD_REDO))

        formattingMenu.AppendSeparator()

        attributesMenu = wxMenu()
        formattingMenu.AppendMenu(wxNewId(), 'Attributes', attributesMenu)

        menuID=wxNewId()
        menuItem = wxMenuItem(attributesMenu, menuID, 'importance: high')
        attributesMenu.AppendItem(menuItem)
        EVT_MENU(self, menuID, lambda evt: self.insertAttribute('importance', 'high'))

        menuID=wxNewId()
        menuItem = wxMenuItem(attributesMenu, menuID, 'importance: low')
        attributesMenu.AppendItem(menuItem)
        EVT_MENU(self, menuID, lambda evt: self.insertAttribute('importance', 'low'))

        menuID=wxNewId()
        menuItem = wxMenuItem(attributesMenu, menuID, 'tree_position: 0')
        attributesMenu.AppendItem(menuItem)
        EVT_MENU(self, menuID, lambda evt: self.insertAttribute('tree_position', '0'))

        menuID=wxNewId()
        menuItem = wxMenuItem(attributesMenu, menuID, 'wrap: 80')
        attributesMenu.AppendItem(menuItem)
        EVT_MENU(self, menuID, lambda evt: self.insertAttribute('wrap', '80'))

        iconsMenu = wxMenu()
        attributesMenu.AppendMenu(wxNewId(), 'icons', iconsMenu)

        iconsMenu1 = wxMenu()
        iconsMenu.AppendMenu(wxNewId(), 'A-C', iconsMenu1)
        iconsMenu2 = wxMenu()
        iconsMenu.AppendMenu(wxNewId(), 'D-F', iconsMenu2)
        iconsMenu3 = wxMenu()
        iconsMenu.AppendMenu(wxNewId(), 'H-L', iconsMenu3)
        iconsMenu4 = wxMenu()
        iconsMenu.AppendMenu(wxNewId(), 'M-P', iconsMenu4)
        iconsMenu5 = wxMenu()
        iconsMenu.AppendMenu(wxNewId(), 'Q-S', iconsMenu5)
        iconsMenu6 = wxMenu()
        iconsMenu.AppendMenu(wxNewId(), 'T-Z', iconsMenu6)

        icons = self.iconLookup.keys();
        icons.sort(lambda a, b: cmp(a, b))
        for id in icons:
            if id.startswith("tb_"):
                continue
            iconsSubMenu = None   
            if id[0] <= 'c':
                iconsSubMenu = iconsMenu1
            elif id[0] <= 'f':
                iconsSubMenu = iconsMenu2
            elif id[0] <= 'l':
                iconsSubMenu = iconsMenu3
            elif id[0] <= 'p':
                iconsSubMenu = iconsMenu4
            elif id[0] <= 's':
                iconsSubMenu = iconsMenu5
            elif id[0] <= 'z':
                iconsSubMenu = iconsMenu6

            menuID=wxNewId()
            menuItem = wxMenuItem(iconsSubMenu, menuID, id, id)
            (id2, bitmap) = self.iconLookup[id]
            menuItem.SetBitmap(bitmap)
            iconsSubMenu.AppendItem(menuItem)
            def insertIconAttribute(evt, iconId=id):
                self.insertAttribute("icon", iconId)
            EVT_MENU(self, menuID, insertIconAttribute)

        formattingMenu.AppendSeparator()

        menuID=wxNewId()
        menuItem = wxMenuItem(formattingMenu, menuID, '&Zoom In\t' + self.keyBindings.ZoomIn, 'Zoom In')
        (id, bitmap) = self.iconLookup["tb_zoomin"]
        menuItem.SetBitmap(bitmap)
        formattingMenu.AppendItem(menuItem)
        EVT_MENU(self, menuID, lambda evt: self.editor.CmdKeyExecute(wxSTC_CMD_ZOOMIN))

        menuID=wxNewId()
        menuItem = wxMenuItem(formattingMenu, menuID, 'Zoo&m Out\t' + self.keyBindings.ZoomOut, 'Zoom Out')
        (id, bitmap) = self.iconLookup["tb_zoomout"]
        menuItem.SetBitmap(bitmap)
        formattingMenu.AppendItem(menuItem)
        EVT_MENU(self, menuID, lambda evt: self.editor.CmdKeyExecute(wxSTC_CMD_ZOOMOUT))

        formattingMenu.AppendSeparator()

        menuID=wxNewId()
        formattingMenu.Append(menuID, '&Find and Replace\t' + self.keyBindings.FindAndReplace, 'Find and Replace')
        EVT_MENU(self, menuID, lambda evt: self.showFindReplaceDialog())

        formattingMenu.AppendSeparator()

        menuID=wxNewId()
        formattingMenu.Append(menuID, '&Rewrap Text\t' + self.keyBindings.RewrapText, 'Rewrap Text')
        EVT_MENU(self, menuID, lambda evt: self.editor.rewrapText())

        menuID=wxNewId()
        wrapModeMenuItem = wxMenuItem(formattingMenu, menuID, "&Wrap Mode", "Set wrap mode", wxITEM_CHECK)            
        formattingMenu.AppendItem(wrapModeMenuItem)
        EVT_MENU(self, menuID, lambda evt: self.setWrapMode(wrapModeMenuItem.IsChecked()))

        menuID=wxNewId()
        indentGuidesMenuItem = wxMenuItem(formattingMenu, menuID, "&View Indentation Guides", "View Indentation Guides", wxITEM_CHECK)            
        formattingMenu.AppendItem(indentGuidesMenuItem)
        EVT_MENU(self, menuID, lambda evt: self.setIndentationGuides(indentGuidesMenuItem.IsChecked()))

        formattingMenu.AppendSeparator()

        menuID=wxNewId()
        formattingMenu.Append(menuID, '&Eval\t' + self.keyBindings.Eval, 'Eval Script Blocks')
        EVT_MENU(self, menuID, lambda evt: self.editor.evalScriptBlocks())

        menuID=wxNewId()
        formattingMenu.Append(menuID, '&Eval Function 1\tCtrl-1', 'Eval Script Function 1')
        EVT_MENU(self, menuID, lambda evt: self.editor.evalScriptBlocks(1))

        menuID=wxNewId()
        formattingMenu.Append(menuID, '&Eval Function 2\tCtrl-2', 'Eval Script Function 2')
        EVT_MENU(self, menuID, lambda evt: self.editor.evalScriptBlocks(2))

        menuID=wxNewId()
        formattingMenu.Append(menuID, '&Eval Function 3\tCtrl-3', 'Eval Script Function 3')
        EVT_MENU(self, menuID, lambda evt: self.editor.evalScriptBlocks(3))

        menuID=wxNewId()
        formattingMenu.Append(menuID, '&Eval Function 4\tCtrl-4', 'Eval Script Function 4')
        EVT_MENU(self, menuID, lambda evt: self.editor.evalScriptBlocks(4))

        menuID=wxNewId()
        formattingMenu.Append(menuID, '&Eval Function 5\tCtrl-5', 'Eval Script Function 5')
        EVT_MENU(self, menuID, lambda evt: self.editor.evalScriptBlocks(5))

        menuID=wxNewId()
        formattingMenu.Append(menuID, '&Eval Function 6\tCtrl-6', 'Eval Script Function 6')
        EVT_MENU(self, menuID, lambda evt: self.editor.evalScriptBlocks(6))

        helpMenu=wxMenu()

        def openHelp(evt):
            os.startfile(self.wikiPadHelp)
        
        menuID=wxNewId()
        helpMenu.Append(menuID, '&Open WikidPadHelp', 'Open WikidPadHelp')
        EVT_MENU(self, menuID, openHelp)

        helpMenu.AppendSeparator()

        menuID=wxNewId()
        helpMenu.Append(menuID, '&Visit wikidPad Homepage', 'Visit Homepage')
        EVT_MENU(self, menuID, lambda evt: os.startfile('http://www.jhorman.org/wikidPad/'))

        helpMenu.AppendSeparator()

        menuID=wxNewId()
        helpMenu.Append(menuID, 'View &License', 'View License')
        EVT_MENU(self, menuID, lambda evt: os.startfile(join(self.wikiAppDir, 'license.txt')))

        menuID=wxNewId()
        helpMenu.Append(menuID, 'Enter Registration Code', 'Enter Registration Code')
        EVT_MENU(self, menuID, lambda evt: self.showRegistrationDialog())

        helpMenu.AppendSeparator()

        menuID=wxNewId()
        helpMenu.Append(menuID, '&About', 'About WikidPad')
        EVT_MENU(self, menuID, lambda evt: self.showAboutDialog())

        self.mainmenu.Append(wikiMenu, 'W&iki')
        self.mainmenu.Append(wikiWordMenu, '&Wiki Words')
        self.mainmenu.Append(historyMenu, '&History')
        self.mainmenu.Append(formattingMenu, '&Editor')
        self.mainmenu.Append(helpMenu, 'He&lp')
        
        self.SetMenuBar(self.mainmenu)
        self.mainmenu.EnableTop(1, 0)
        self.mainmenu.EnableTop(2, 0)
        self.mainmenu.EnableTop(3, 0)

        # turn on or off the wrap mode menu item. this must be done here,
        # after the menus are added to the menu bar
        if self.wrapMode:
            wrapModeMenuItem.Check(1)

        # turn on or off auto-save
        if self.autoSave:
            autoSaveMenuItem.Check(1)

        # turn on or off auto-save
        if self.indentationGuides:
            indentGuidesMenuItem.Check(1)

        # ------------------------------------------------------------------------------------
        # Create the toolbar
        # ------------------------------------------------------------------------------------

        tb = self.CreateToolBar(wxTB_HORIZONTAL | wxNO_BORDER | wxTB_FLAT | wxTB_TEXT)
        (index, seperator) = self.iconLookup["tb_seperator"]

        (index, icon) = self.iconLookup["tb_back"]
        tbID = wxNewId()
        tb.AddSimpleTool(tbID, icon, "Back (Ctrl-Alt-Back)", "Back")
        EVT_TOOL(self, tbID, lambda evt: self.goInHistory(-1))

        (index, icon) = self.iconLookup["tb_forward"]
        tbID = wxNewId()
        tb.AddSimpleTool(tbID, icon, "Forward (Ctrl-Alt-Forward)", "Forward")
        EVT_TOOL(self, tbID, lambda evt: self.goInHistory(1))

        (index, icon) = self.iconLookup["tb_home"]
        tbID = wxNewId()
        tb.AddSimpleTool(tbID, icon, "Wiki Root", "Wiki Root")
        EVT_TOOL(self, tbID, lambda evt: self.openWikiPage(self.wikiName, forceTreeSyncFromRoot=True))

        (index, icon) = self.iconLookup["tb_doc"]
        tbID = wxNewId()
        tb.AddSimpleTool(tbID, icon, "Open Wiki Word  (Ctrl-O)", "Open Wiki Word")
        EVT_TOOL(self, tbID, lambda evt: self.showWikiWordOpenDialog())

        (index, icon) = self.iconLookup["tb_lens"]
        tbID = wxNewId()
        tb.AddSimpleTool(tbID, icon, "Search  (Ctrl-Alt-F)", "Search")
        EVT_TOOL(self, tbID, lambda evt: self.showSearchDialog())

        (index, icon) = self.iconLookup["tb_cycle"]
        tbID = wxNewId()
        tb.AddSimpleTool(tbID, icon, "Find current word in tree", "Find current word in tree")
        EVT_TOOL(self, tbID, lambda evt: self.findCurrentWordInTree())

        tb.AddSimpleTool(wxNewId(), seperator, "Separator", "Separator")

        (index, icon) = self.iconLookup["tb_save"]
        tbID = wxNewId()
        tb.AddSimpleTool(tbID, icon, "Save Wiki Word (Ctrl-S)", "Save Wiki Word")
        EVT_TOOL(self, tbID, lambda evt: self.saveCurrentWikiPage())

        (index, icon) = self.iconLookup["tb_rename"]
        tbID = wxNewId()
        tb.AddSimpleTool(tbID, icon, "Rename Wiki Word (Ctrl-Alt-R)", "Rename Wiki Word")
        EVT_TOOL(self, tbID, lambda evt: self.showWikiWordRenameDialog())

        (index, icon) = self.iconLookup["tb_delete"]
        tbID = wxNewId()
        tb.AddSimpleTool(tbID, icon, "Delete (Ctrl-D)", "Delete Wiki Word")
        EVT_TOOL(self, tbID, lambda evt: self.showWikiWordDeleteDialog())
        
        tb.AddSimpleTool(wxNewId(), seperator, "Separator", "Separator")

        (index, icon) = self.iconLookup["tb_heading"]
        tbID = wxNewId()
        tb.AddSimpleTool(tbID, icon, "Heading (Ctrl-Alt-H)", "Heading")
        EVT_TOOL(self, tbID, lambda evt: self.keyBindings.addHeading(self.editor))

        (index, icon) = self.iconLookup["tb_bold"]
        tbID = wxNewId()
        tb.AddSimpleTool(tbID, icon, "Bold (Ctrl-B)", "Bold")
        EVT_TOOL(self, tbID, lambda evt: self.keyBindings.makeBold(self.editor))

        (index, icon) = self.iconLookup["tb_italic"]
        tbID = wxNewId()
        tb.AddSimpleTool(tbID, icon, "Italic (Ctrl-I)", "Italic")
        EVT_TOOL(self, tbID, lambda evt: self.keyBindings.makeItalic(self.editor))

        tb.AddSimpleTool(wxNewId(), seperator, "Separator", "Separator")

        (index, icon) = self.iconLookup["tb_zoomin"]
        tbID = wxNewId()
        tb.AddSimpleTool(tbID, icon, "Zoom In", "Zoom In")
        EVT_TOOL(self, tbID, lambda evt: self.editor.CmdKeyExecute(wxSTC_CMD_ZOOMIN))

        (index, icon) = self.iconLookup["tb_zoomout"]
        tbID = wxNewId()
        tb.AddSimpleTool(tbID, icon, "Zoom Out", "Zoom Out")
        EVT_TOOL(self, tbID, lambda evt: self.editor.CmdKeyExecute(wxSTC_CMD_ZOOMOUT))

        tb.Realize()

        # ------------------------------------------------------------------------------------
        # Create the left-right splitter window.
        # ------------------------------------------------------------------------------------
        self.vertSplitter = wxSplitterWindow(self, -1, style=wxSP_NOBORDER)        
        self.vertSplitter.SetMinimumPaneSize(0)

        # ------------------------------------------------------------------------------------
        # Create the tree on the left.
        # ------------------------------------------------------------------------------------
        self.tree = WikiTreeCtrl(self, self.vertSplitter, -1)
                
        # assign the image list
        try:
            self.tree.AssignImageList(iconList)
        except Exception, e:
            self.displayErrorMessage('There was an error loading the icons for the tree control.', e)
        
        # ------------------------------------------------------------------------------------
        # Create the tabs for preview and edit
        # ------------------------------------------------------------------------------------
        self.editPreviewNotebook = wxNotebook(self.vertSplitter, -1)

        # ------------------------------------------------------------------------------------
        # Create the editor
        # ------------------------------------------------------------------------------------
        self.createEditor()
        self.editPreviewNotebook.AddPage(self.editor, "Edit")

        # ------------------------------------------------------------------------------------
        # Create the preview pane
        # ------------------------------------------------------------------------------------
        self.createPreviewPane()
        self.editPreviewNotebook.AddPage(self.previewPane, "Preview")

        # ------------------------------------------------------------------------------------
        # Split the tree and the editor
        # ------------------------------------------------------------------------------------
        self.vertSplitter.SplitVertically(self.tree, self.editPreviewNotebook, self.lastSplitterPos)

        # ------------------------------------------------------------------------------------
        # Find and replace events
        # ------------------------------------------------------------------------------------
        EVT_COMMAND_FIND(self, -1, self.OnFind)
        EVT_COMMAND_FIND_NEXT(self, -1, lambda evt: self.OnFind(evt, next=True))
        EVT_COMMAND_FIND_REPLACE(self, -1, lambda evt: self.OnFind(evt, replace=True))
        EVT_COMMAND_FIND_REPLACE_ALL(self, -1, lambda evt: self.OnFind(evt, replaceAll=True))
        EVT_COMMAND_FIND_CLOSE(self, -1, self.OnFindClose)

        # ------------------------------------------------------------------------------------
        # Create the status bar
        # ------------------------------------------------------------------------------------
        self.statusBar = wxStatusBar(self, -1)
        self.statusBar.SetFieldsCount(2)
        self.SetStatusBar(self.statusBar)

        # Register the App IDLE handler
        EVT_IDLE(self, self.OnIdle)

        # Register the App close handler
        EVT_CLOSE(self, self.OnWikiExit)

        # display the window
        self.Show(True)
        
        # turn on the tree control check box
        if self.vertSplitter.GetSashPosition() > 1:
            showTreeCtrlMenuItem.Check(1)
        else:
            self.tree.Hide()

        # setup the notebook tab selection listener
        EVT_NOTEBOOK_PAGE_CHANGED(self, -1, lambda evt: self.refreshPreview())


    def createEditor(self):    
        self.editor = WikiTxtCtrl(self, self.editPreviewNotebook, -1)
        self.editor.evalScope = { 'editor' : self.editor, 'pwiki' : self, 'lib': self.evalLib}

        # enable and zoom the editor
        self.editor.Enable(0)
        if (self.globalConfig.has_option("main", "zoom")):
            self.editor.SetZoom(int(self.globalConfig.get("main", "zoom")))

        # set the wrap mode of the editor
        self.setWrapMode(self.wrapMode)
        if self.indentationGuides:
            self.editor.SetIndentationGuides(1)
        

    def createPreviewPane(self):
        self.previewPane = WikiPreview(self, self.editPreviewNotebook, -1)


    def refreshPreview(self):
        if self.currentWikiWord and self.previewPane.IsShown():
            (saveDirty, updateDirty) = self.currentWikiPage.getDirty()
            if updateDirty:
                self.updateRelationships()
            self.previewPane.setWikiPage(self.currentWikiPage, self.editor.GetText())


    def resetGui(self):
        # delete everything in the current tree
        self.tree.DeleteAllItems()
        
        # reset the editor
        self.editor.SetText("")
        self.editor.SetSelection(-1, -1)
        self.editor.EmptyUndoBuffer()
        self.editor.Disable()
        

    def newWiki(self, wikiName, wikiDir):
        "creates a new wiki"

        self.wikidPadHooks.newWiki(self, wikiName, wikiDir)
        
        wikiName = string.replace(wikiName, " ", "")
        wikiDir = join(wikiDir, wikiName)
        configFileLoc = join(wikiDir, "%s.wiki" % wikiName)
        
        self.statusBar.SetStatusText("Creating Wiki: %s" % wikiName, 0)

        createIt = True;
        if (exists(wikiDir)):
            dlg=wxMessageDialog(self, "A wiki already exists in '%s', overwrite?" % wikiDir,
                               'Warning', wxYES_NO)
            result = dlg.ShowModal()
            if result == wxID_YES:
                os.rmdir(wikiDir)
                createIt = True
            elif result == wxID_NO:
                createIt = False
            dlg.Destroy()        

        if (createIt):
            # create the new dir for the wiki
            os.mkdir(wikiDir)
            
            # create a new config file for the new wiki
            config = ConfigParser.ConfigParser()
            config.add_section("main")
            config.add_section("wiki_db")
            config.set("main", "wiki_name", wikiName)
            config.set("main", "last_wiki_word", wikiName)
            config.set("wiki_db", "data_dir", "data")
            allIsWell = True
    
            dataDir = join(wikiDir, "data")

            # create the data directory for the data files
            try:
                createWikiDB(wikiName, dataDir, false)
            except WikiDBExistsException:
                # The DB exists, should it be overwritten
                dlg=wxMessageDialog(self, 'A wiki database already exists in this location, overwrite?',
                                    'Wiki DB Exists', wxYES_NO)
                result = dlg.ShowModal()
                if result == wxID_YES:
                    createWikiDB(wikiName, dataDir, true)
                else:
                    allIsWell = False
                    
                dlg.Destroy()
            except Exception, e:
                self.displayErrorMessage('There was an error creating the wiki database.', e)
                allIsWell = False
                
            if (allIsWell):
                # everything is ok, write out the config file
                configFile = open(configFileLoc, 'w')
                config.write(configFile)
                configFile.close()

                self.statusBar.SetStatusText("Created Wiki: %s" % wikiName, 0)

                # open the new wiki
                self.openWiki(configFileLoc)
                self.editor.GotoPos(self.editor.GetLength())                
                self.editor.AddText("\n\n\t* WikiSettings\n")

                # create the WikiSettings page
                self.openWikiPage("WikiSettings", False, False)
                self.editor.GotoPos(self.editor.GetLength())
                self.editor.AddText("\n\nThese are your default global settings.\n\n")
                self.editor.AddText("[global.importance.low.color: grey]\n")
                self.editor.AddText("[global.importance.high.bold: true]\n")
                self.editor.AddText("[global.contact.icon: contact]\n")                
                self.editor.AddText("[global.todo.bold: true]\n")
                self.editor.AddText("[global.todo.icon: pin]\n")
                self.editor.AddText("[global.wrap: 70]\n")
                self.editor.AddText("\n[icon: cog]\n")

                # trigger hook            
                self.wikidPadHooks.createdWiki(self, wikiName, wikiDir)

                # reopen the root
                self.openWikiPage(self.wikiName, False, False)
                

    def openWiki(self, wikiConfigFile, wikiWordToOpen=None):
        "opens up a wiki"

        self.wikidPadHooks.openWiki(self, wikiConfigFile)

        # Save the state of the currently open wiki, if there was one open
        # if the new config is the same as the old, don't resave state since
        # this could be a wiki overwrite from newWiki. We don't want to overwrite
        # the new config with the old one.
        if self.wikiConfigFile != wikiConfigFile:
            self.closeWiki()

        # status
        self.statusBar.SetStatusText("Opening Wiki: %s" % wikiConfigFile, 0)

        # make sure the config exists
        if (not exists(wikiConfigFile)):
            self.displayErrorMessage("Wiki configuration file '%s' not found" % wikiConfigFile)
            if wikiConfigFile in self.wikiHistory:
                self.wikiHistory.remove(wikiConfigFile)
            return False
        
        # read in the config file        
        config = ConfigParser.ConfigParser()
        try:
            config.read(wikiConfigFile)
        except Exception, e:
            # try to recover by checking if the parent dir contains the real wiki file
            # if it does the current wiki file must be a wiki word file, so open the
            # real wiki to the wiki word.
            try:
                parentDir = dirname(dirname(wikiConfigFile))
                if parentDir:
                    wikiFiles = [file for file in os.listdir(parentDir) if file.endswith(".wiki")]
                    if len(wikiFiles) > 0:
                        wikiWord = basename(wikiConfigFile)
                        wikiWord = wikiWord[0:len(wikiWord)-5]

                        # if this is win95 or < the file name could be a 8.3 alias, file~1 for example
                        windows83Marker = wikiWord.find("~")
                        if windows83Marker != -1:
                            wikiWord = wikiWord[0:windows83Marker]
                            matchingFiles = [file for file in wikiFiles if file.lower().startswith(wikiWord)]
                            if matchingFiles:
                                wikiWord = matchingFiles[0]
                        self.openWiki(join(parentDir, wikiFiles[0]), wikiWord)
                        return                
            except Exception, ne:            
                self.displayErrorMessage("Error reading config file '%s'" % wikiConfigFile, e)
                print ne
                return False
        
        # config variables
        try:
            wikiName = config.get("main", "wiki_name")
            dataDir = config.get("wiki_db", "data_dir")
        except Exception, e:
            self.displayErrorMessage("Wiki configuration file is corrupt", e)
            return False
        
        # absolutize the path to data dir if it's not already
        if not isabs(dataDir):
            dataDir = join(dirname(wikiConfigFile), dataDir)
            
        # create the db interface to the wiki data
        wikiData = None
        try:
            wikiData = WikiData(self, dataDir)
        except Exception, e:
            self.displayErrorMessage("Error connecting to database in '%s'" % dataDir, e)
            return False
            
        # what was the last wiki word opened
        lastWikiWord = wikiWordToOpen
        if not lastWikiWord and config.has_option("main", "last_wiki_word"):
            lastWikiWord = config.get("main", "last_wiki_word")

        # OK, things look good
        
        # Reset some of the members
        self.currentWikiWord = None
        self.currentWikiPage = None
        self.historyPosition = 0
        self.wikiWordHistory = []

        # set the member variables.
        self.wikiConfigFile = wikiConfigFile
        self.config = config
        self.wikiName = wikiName
        self.dataDir = dataDir
        self.wikiData = wikiData

        # reset the gui
        self.resetGui()

        # enable the top level menus        
        self.mainmenu.EnableTop(1, 1)
        self.mainmenu.EnableTop(2, 1)
        self.mainmenu.EnableTop(3, 1)

        # add the root node to the tree
        self.treeRoot = self.tree.AddRoot(self.wikiName)
        self.tree.SetPyData(self.treeRoot, (self.wikiName,None,None))
        self.tree.SetItemBold(self.treeRoot, True)
        self.tree.SelectItem(self.treeRoot)

        # open the root
        self.openWikiPage(self.wikiName)

        # make sure the root has a relationship to the ScratchPad
        self.currentWikiPage.addChildRelationship("ScratchPad")

        # set the root tree node as having children if it does
        if len(self.currentWikiPage.childRelations) > 0:
            self.tree.SetItemHasChildren(self.treeRoot, 1)
            self.tree.Expand(self.treeRoot)

        # set status
        self.statusBar.SetStatusText("Opened wiki '%s'" % self.wikiName, 0)

        # now try and open the last wiki page
        if lastWikiWord and lastWikiWord != self.wikiName:
            # if the word is not a wiki word see if a word that starts with the word can be found
            if not self.wikiData.isWikiWord(lastWikiWord):
                wordsStartingWith = self.wikiData.getWikiWordsStartingWith(lastWikiWord, True)
                if wordsStartingWith:
                    lastWikiWord = wordsStartingWith[0]
            self.openWikiPage(lastWikiWord)
            self.findCurrentWordInTree()

        # enable the editor control whether or not the wiki root was found
        self.editor.Enable(1)
        
        # update the last accessed wiki config var
        self.lastAccessedWiki(self.wikiConfigFile)

        # trigger hook
        self.wikidPadHooks.openedWiki(self, self.wikiName, wikiConfigFile)

        # return that the wiki was opened successfully
        return True

    
    def closeWiki(self, saveState=True):
        if self.wikiConfigFile:
            if saveState:
                self.saveCurrentWikiState()
            if self.wikiData:
                self.wikiData.close()
            self.wikiConfigFile = None
            
             
    def saveCurrentWikiState(self):
        # write out the current config
        if self.config:
            self.writeCurrentConfig()

        # save the current wiki page if it is dirty
        if self.currentWikiPage:
            (saveDirty, updateDirty) = self.currentWikiPage.getDirty()
            if saveDirty:
                self.saveCurrentWikiPage()            

        # database commits
        if self.wikiData:
            self.wikiData.commit()
        

    def openWikiPage(self, wikiWord, addToHistory=True, forceTreeSyncFromRoot=False):

        self.statusBar.SetStatusText("Opening wiki word '%s'" % wikiWord, 0)

        # make sure this is a valid wiki word
        if not WikiFormatting.isWikiWord(wikiWord):
            self.displayErrorMessage("'%s' is an invalid wiki word." % wikiWord)

        # don't reopen the currently open page
        if (wikiWord == self.currentWikiWord):
            self.tree.buildTreeForWord(self.currentWikiWord)
            self.statusBar.SetStatusText("Wiki word '%s' already open" % wikiWord, 0)
            return

        # save the current page if it is dirty
        if self.currentWikiPage:
            (saveDirty, updateDirty) = self.currentWikiPage.getDirty()
            if saveDirty:
                self.saveCurrentWikiPage()

            # save the cursor position of the current page so that if 
            # the user comes back we can put the cursor in the right spot.
            self.lastCursorPositionInPage[self.currentWikiWord] = self.editor.GetCurrentPos();

        # trigger hook
        self.wikidPadHooks.openWikiWord(self, wikiWord)

        # check if this is an alias
        if (self.wikiData.isAlias(wikiWord)):
            aliasesWikiWord = self.wikiData.getAliasesWikiWord(wikiWord)
            if aliasesWikiWord:
                wikiWord = aliasesWikiWord

        # set the current wikiword
        self.currentWikiWord = wikiWord

        # fetch the page info from the database
        try:        
            self.currentWikiPage = self.wikiData.getPage(wikiWord)
        except WikiWordNotFoundException, e:
            self.currentWikiPage = self.wikiData.createPage(wikiWord)
            self.wikidPadHooks.newWikiWord(self, wikiWord)

        # set the editor text
        content = ""
        
        try:
            content = self.currentWikiPage.getContent()
            self.statusBar.SetStatusText("Opened wiki word '%s'" % self.currentWikiWord, 0)
        except WikiFileNotFoundException, e:
            self.statusBar.SetStatusText("Wiki page not found, a new page will be created", 0)
            title = self.getWikiPageTitle(self.currentWikiWord)
            content = "++ %s\n\n" % title

        # get the properties that need to be checked for options
        pageProps = self.currentWikiPage.props
        globalProps = self.wikiData.getGlobalProperties()

        # get the font that should be used in the editor
        font = self.defaultEditorFont
        if pageProps.has_key("font"):
            font = pageProps["font"][0]
        elif globalProps.has_key("global.font"):
            font = globalProps["global.font"]

        # set the styles in the editor to the font                
        if self.lastEditorFont != font:
            faces["mono"] = font
            self.editor.SetStyles(faces)
            self.lastEditorFont = font

        # now fill the text into the editor
        self.editor.SetText(content)

        # see if there is a saved position for this page        
        lastPos = self.lastCursorPositionInPage.get(wikiWord)
        if lastPos:
            self.editor.GotoPos(lastPos)
        else:
            self.editor.GotoPos(0)

        # if the preview pane is showing refresh it
        self.refreshPreview()

        # get the font that should be used in the editor
        wikiWordsEnabled = True
        if pageProps.has_key("camelCaseWordsEnabled"):
            if pageProps["camelCaseWordsEnabled"][0] == "false":
                wikiWordsEnabled = False
        elif globalProps.has_key("global.camelCaseWordsEnabled"):
            if globalProps["global.camelCaseWordsEnabled"] == "false":
                wikiWordsEnabled = False

        self.wikiWordsEnabled = wikiWordsEnabled
        self.editor.wikiWordsEnabled = wikiWordsEnabled

        # set the title and add the word to the history        
        self.SetTitle("Wiki: %s - %s" % (self.wikiName, self.currentWikiWord))        
        if addToHistory: self.addToHistory(wikiWord)
        self.config.set("main", "last_wiki_word", wikiWord)

        # sync the tree
        if forceTreeSyncFromRoot:
            self.findCurrentWordInTree()

        # trigger hook
        self.wikidPadHooks.openedWikiWord(self, wikiWord)        


    def findCurrentWordInTree(self):
        try:
            self.tree.buildTreeForWord(self.currentWikiWord, selectNode=True)
        except Exception, e:
            sys.stderr.write("%s\n" % e)
            

    def viewParents(self, ofWord):
        parents = self.wikiData.getParentRelationships(ofWord)

        dlg = wxSingleChoiceDialog(self,
                                    "Parent nodes of '%s'" % ofWord,
                                    "Parent nodes of '%s'" % ofWord,
                                    parents,
                                    wxOK|wxCANCEL)

        if dlg.ShowModal() == wxID_OK:
            wikiWord = dlg.GetStringSelection()
            if len(wikiWord) > 0:
                self.openWikiPage(wikiWord, forceTreeSyncFromRoot=True)
        dlg.Destroy()


    def viewParentLess(self):
        parentLess = self.wikiData.getParentLessWords()
        dlg = wxSingleChoiceDialog(self,
                                   "Parentless nodes",
                                   "Parentless nodes",
                                   parentLess,
                                   wxOK|wxCANCEL)
        
        if dlg.ShowModal() == wxID_OK:
            wikiWord = dlg.GetStringSelection()
            if len(wikiWord) > 0:
                self.openWikiPage(wikiWord, forceTreeSyncFromRoot=True)
        dlg.Destroy()


    def viewChildren(self, ofWord):
        children = self.wikiData.getChildRelationships(ofWord)
        dlg = wxSingleChoiceDialog(self,
                                   "Child nodes of '%s'" % ofWord,
                                   "Child nodes of '%s'" % ofWord,
                                   children,
                                   wxOK|wxCANCEL)
        
        if dlg.ShowModal() == wxID_OK:
            wikiWord = dlg.GetStringSelection()
            if len(wikiWord) > 0:
                self.openWikiPage(wikiWord, forceTreeSyncFromRoot=True)
        dlg.Destroy()


    def addToHistory(self, wikiWord):
        if wikiWord == self.getCurrentWikiWordFromHistory():
            return
        
        # if the pointer is on the middle of the array right now
        # slice the array at the pointer and then add
        if self.historyPosition < len(self.wikiWordHistory)-1:
            self.wikiWordHistory = self.wikiWordHistory[0:self.historyPosition+1]

        # add the item to history            
        self.wikiWordHistory.append(wikiWord)

        # only keep 25 items
        if len(self.wikiWordHistory) > 25:
            self.wikiWordHistory.pop(0)

        # set the position of the history pointer
        self.historyPosition = len(self.wikiWordHistory)-1


    def goInHistory(self, posDelta=0):
        if (posDelta < 0 and self.historyPosition > 0) or (posDelta > 0 and self.historyPosition < (len(self.wikiWordHistory)-1)):
            self.historyPosition = self.historyPosition + posDelta
        wikiWord = self.wikiWordHistory[self.historyPosition]
        self.openWikiPage(wikiWord, False)


    def goBackInHistory(self, howMany=1):
        if self.historyPosition > 0:
            self.historyPosition = self.historyPosition - howMany
            wikiWord = self.wikiWordHistory[self.historyPosition]
            self.openWikiPage(wikiWord, False)
    

    def goForwardInHistory(self):
        if self.historyPosition < len(self.wikiWordHistory)-1:
            self.historyPosition = self.historyPosition + 1
            wikiWord = self.wikiWordHistory[self.historyPosition]
            self.openWikiPage(wikiWord, False)


    def getCurrentWikiWordFromHistory(self):
        if len(self.wikiWordHistory) > 0:
            return self.wikiWordHistory[self.historyPosition]
        else:
            return None


    def viewHistory(self, posDelta=0):    
        dlg = wxSingleChoiceDialog(self,
                                   "History",
                                   "History",
                                   self.wikiWordHistory,
                                   wxOK|wxCANCEL)

        historyLen = len(self.wikiWordHistory)
        position = self.historyPosition+posDelta
        if (position < 0):
            position = 0
        elif (position >= historyLen):
            position = historyLen-1
        
        dlg.SetSelection(position)
        if dlg.ShowModal() == wxID_OK:
            self.goInHistory(dlg.GetSelection() - self.historyPosition)
            self.findCurrentWordInTree()
        dlg.Destroy()


    def viewBookmarks(self):        
        dlg = wxSingleChoiceDialog(self,
                                   "Bookmarks",
                                   "Bookmarks",
                                   self.wikiData.getWordsWithPropertyValue("bookmarked", "true"),
                                   wxOK|wxCANCEL)
        
        if dlg.ShowModal() == wxID_OK:
            wikiWord = dlg.GetStringSelection()
            if len(wikiWord) > 0:
                self.openWikiPage(wikiWord, forceTreeSyncFromRoot=True)
        dlg.Destroy()

    
    def saveCurrentWikiPage(self):
        self.statusBar.SetStatusText("Saving WikiPage", 0)
        self.wikidPadHooks.savingWikiWord(self, self.currentWikiWord)

        error = False
        while 1:
            try:
                self.currentWikiPage.save(self.editor.GetText())
                error = False
                break
            except Exception, e:
                error = True
                dlg=wxMessageDialog(self, 'There was an error saving the contents of wiki page "%s".\n%s\n\nWould you like to try and save this document again?' % (self.currentWikiWord, e),
                                    'Error Saving!', wxYES_NO)
                result = dlg.ShowModal()
                dlg.Destroy()                
                if result == wxID_NO:
                    break

        if not error:        
            self.statusBar.SetStatusText("", 0)
            self.editor.SetSavePoint()
            self.wikidPadHooks.savedWikiWord(self, self.currentWikiWord)

            # if saving the root open it in the tree
            if (self.currentWikiWord == self.wikiName):
                self.findCurrentWordInTree()


    def updateRelationships(self):
        self.statusBar.SetStatusText("Updating relationships", 0)
        self.currentWikiPage.update(self.editor.GetText())
        self.statusBar.SetStatusText("", 0)        


    def lastAccessedWiki(self, wikiConfigFile):
        "writes to the global config the location of the last accessed wiki"
        # create a new config file for the new wiki
        self.globalConfig.set("main", "last_wiki", wikiConfigFile)
        if wikiConfigFile not in self.wikiHistory:
            self.wikiHistory.append(wikiConfigFile)

            # only keep 5 items
            if len(self.wikiWordHistory) > 5:
                self.wikiWordHistory.pop(0)

            # add the item to the menu
            menuID=wxNewId()
            self.recentWikisMenu.Append(menuID, wikiConfigFile)
            EVT_MENU(self, menuID, self.OnSelectRecentWiki)

        self.globalConfig.set("main", "last_active_dir", dirname(wikiConfigFile))
        self.writeGlobalConfig()

    def setWrapMode(self, onOrOff):
        self.wrapMode = onOrOff
        self.globalConfig.set("main", "wrap_mode", self.wrapMode)
        self.editor.setWrap(self.wrapMode)

    def setAutoSave(self, onOrOff):
        self.autoSave = onOrOff
        self.globalConfig.set("main", "auto_save", self.autoSave)

    def setIndentationGuides(self, onOrOff):
        self.indentationGuides = onOrOff
        self.globalConfig.set("main", "indentation_guides", self.indentationGuides)
        if onOrOff:
            self.editor.SetIndentationGuides(1)
        else:
            self.editor.SetIndentationGuides(0)

    def setShowTreeControl(self, onOrOff):
        if onOrOff:
            if self.lastSplitterPos < 50:
                self.lastSplitterPos = 185
            self.vertSplitter.SetSashPosition(self.lastSplitterPos)
            self.tree.Show()
        else:
            self.lastSplitterPos = self.vertSplitter.GetSashPosition()
            self.vertSplitter.SetSashPosition(1)
            self.tree.Hide()
            
        
    def writeGlobalConfig(self):
        "writes out the global config file"
        try:
            configFile = open(self.globalConfigLoc, 'w')
            self.globalConfig.write(configFile)
            configFile.close()
        except Exception, e:
            self.displayErrorMessage("Error saving global configuration", e)


    def writeCurrentConfig(self):
        "writes out the current config file"
        if (self.config):
            try:
                configFile = open(self.wikiConfigFile, 'w')
                self.config.write(configFile)
                configFile.close()        
            except Exception, e:
                self.displayErrorMessage("Error saving current configuration", e)


    def showWikiWordOpenDialog(self):
        dlg = OpenWikiWordDialog(self, -1)
        dlg.CenterOnParent(wxBOTH)
        if dlg.ShowModal() == wxID_OK:
            wikiWord = dlg.GetValue()
            if wikiWord:
                dlg.Destroy()
                self.openWikiPage(wikiWord, forceTreeSyncFromRoot=True)                
        dlg.Destroy()
        

    def showWikiWordRenameDialog(self, wikiWord=None, toWikiWord=None):
        dlg = wxTextEntryDialog (self, "Rename '%s' to:" % self.currentWikiWord,
                                 "Rename Wiki Word", "", wxOK | wxCANCEL)        
        if dlg.ShowModal() == wxID_OK:
            wikiWord = dlg.GetValue()
            self.showWikiWordRenameConfirmDialog(self.currentWikiWord, wikiWord)
        dlg.Destroy()


    def showWikiWordRenameConfirmDialog(self, wikiWord, toWikiWord):
        if not toWikiWord or len(toWikiWord) == 0:
            return False

        if wikiWord == toWikiWord:
            return False

        if wikiWord == "ScratchPad":
            self.displayErrorMessage("The scratch pad cannot be renamed.")
            return False

        if not WikiFormatting.isWikiWord(toWikiWord):
            toWikiWord = "[%s]" % toWikiWord
        if not WikiFormatting.isWikiWord(toWikiWord):
            self.displayErrorMessage("'%s' is an invalid WikiWord" % toWikiWord)
            return False
        
        dlg=wxMessageDialog(self, "Are you sure you want to rename wiki word '%s' to '%s'?" % (wikiWord, toWikiWord),
                            'Rename Wiki Word', wxYES_NO)
        
        renamed = False
        result = dlg.ShowModal()
        if result == wxID_YES:
            try:
                self.saveCurrentWikiPage()
                self.wikiData.renameWord(wikiWord, toWikiWord)

                # if the root was renamed we have a little more to do
                if wikiWord == self.wikiName:
                    self.config.set("main", "wiki_name", toWikiWord)
                    self.config.set("main", "last_wiki_word", toWikiWord)
                    self.saveCurrentWikiState()
                    self.wikiHistory.remove(self.wikiConfigFile)
                    renamedConfigFile = join(dirname(self.wikiConfigFile), "%s.wiki" % toWikiWord)
                    os.rename(self.wikiConfigFile, renamedConfigFile)
                    self.wikiConfigFile = None
                    self.openWiki(renamedConfigFile)
                    
                self.wikidPadHooks.renamedWikiWord(self, wikiWord, toWikiWord)
                self.tree.collapse()
                self.openWikiPage(toWikiWord, forceTreeSyncFromRoot=True)
                self.findCurrentWordInTree()
                renamed = True
            except WikiDataException, e:
                self.displayErrorMessage(str(e))
                
        dlg.Destroy()        
        return renamed


    def showSearchDialog(self):
        dlg = SearchDialog(self, -1)
        dlg.CenterOnParent(wxBOTH)
        if dlg.ShowModal() == wxID_OK:
            (wikiWord, searchedFor) = dlg.GetValue()
            if wikiWord:
                dlg.Destroy()
                self.openWikiPage(wikiWord, forceTreeSyncFromRoot=True)
                self.editor.executeSearch(searchedFor, 0)
        dlg.Destroy()


    def showSavedSearchesDialog(self):
        dlg = SavedSearchesDialog(self, -1)
        dlg.CenterOnParent(wxBOTH)
        if dlg.ShowModal() == wxID_OK:
            wikiWord = dlg.GetValue()
            if wikiWord:
                dlg.Destroy()
                self.openWikiPage(wikiWord, forceTreeSyncFromRoot=True)
        dlg.Destroy()


    def showWikiWordDeleteDialog(self, wikiWord=None):
        if not wikiWord:
            wikiWord = self.currentWikiWord

        if wikiWord == "ScratchPad":
            self.displayErrorMessage("The scratch pad cannot be deleted")
            return
        
        dlg=wxMessageDialog(self, "Are you sure you want to delete wiki word '%s'?" % wikiWord,
                            'Delete Wiki Word', wxYES_NO)
        result = dlg.ShowModal()
        if result == wxID_YES:
            self.saveCurrentWikiPage()
            try:
                self.wikiData.deleteWord(wikiWord)
                self.wikidPadHooks.deletedWikiWord(self, wikiWord)
                if wikiWord == self.currentWikiWord:
                    self.tree.collapse()
                    if self.wikiWordHistory[self.historyPosition-1] != self.currentWikiWord:
                        self.goInHistory(-1)
                    else:
                        self.openWikiPage(self.wikiName)
                    self.findCurrentWordInTree()
            except WikiDataException, e:
                self.displayErrorMessage(str(e))
                
        dlg.Destroy()        


    def showFindReplaceDialog(self):
        self.lastFindPos = -1
        data = wxFindReplaceData()
        dlg = wxFindReplaceDialog(self, data, "Find and Replace", wxFR_REPLACEDIALOG)
        dlg.data = data
        dlg.Show(True)


    def exportWiki(self, type):
        dlg = wxDirDialog(self, "Select Export Directory", self.getLastActiveDir(), style=wxDD_DEFAULT_STYLE|wxDD_NEW_DIR_BUTTON)
        if dlg.ShowModal() == wxID_OK:
            exporter = HtmlExporter(self)
            dir = dlg.GetPath()
            exporter.export(type, dir)
            self.globalConfig.set("main", "last_active_dir", dir)


    def rebuildWiki(self):
        dlg=wxMessageDialog(self, "Are you sure you want to rebuild this wiki? You may want to backup your data first!",
                            'Rebuild wiki', wxYES_NO)
        result = dlg.ShowModal()
        if result == wxID_YES:
            # get all of the wikiWords
            wikiWords = self.wikiData.getAllWikiWordsFromDisk()
            # get the saved searches
            searches = self.wikiData.getSavedSearches()

            # close nulls the wikiConfigFile var, so save it
            wikiConfigFile = self.wikiConfigFile
            # first close the existing wiki
            self.closeWiki()
    
            progress = wxProgressDialog("Rebuilding wiki", "Rebuilding wiki",
                                        len(wikiWords) + len(searches) + 1, self, wxPD_APP_MODAL)

            try:
                step = 1
                # recreate the db    
                progress.Update(step, "Recreating database")
                createWikiDB(self.wikiName, self.dataDir, True)
                # reopen the wiki
                wikiData = WikiData(self, self.dataDir)
                # re-save all of the pages
                for wikiWord in wikiWords:
                    progress.Update(step, "Rebuilding %s" % wikiWord)
                    wikiPage = wikiData.createPage(wikiWord)
                    wikiPage.update(wikiPage.getContent(), False)
                    step = step + 1

                # resave searches
                for search in searches:
                    progress.Update(step, "Readding search %s" % search)
                    wikiData.saveSearch(search)
                    
                wikiData.close()
                progress.Destroy()

            except Exception, e:
                self.displayErrorMessage("Error rebuilding wiki", e)
            
            self.openWiki(wikiConfigFile)
        

    def insertAttribute(self, name, value):
        pos = self.editor.GetCurrentPos()
        self.editor.GotoPos(self.editor.GetLength())
        self.editor.AddText("\n\n[%s=%s]" % (name, value))
        self.editor.GotoPos(pos)
        self.saveCurrentWikiPage()


    def getLastActiveDir(self):
        if self.globalConfig.has_option("main", "last_active_dir"):
            return self.globalConfig.get("main", "last_active_dir")
        else:
            return os.getcwd()
    

    def displayMessage(self, title, str):
        "pops up a dialog box"
        dlg_m = wxMessageDialog(self, "%s" % str, title, wxOK)
        dlg_m.ShowModal()
        dlg_m.Destroy()


    def displayErrorMessage(self, errorStr, e=""):
        "pops up a error dialog box"
        dlg_m = wxMessageDialog(self, "%s. %s." % (errorStr, e), 'Error!', wxOK)
        dlg_m.ShowModal()
        dlg_m.Destroy()
        try:
            self.statusBar.SetStatusText(errorStr, 0)
        except:
            pass
        

    def showAboutDialog(self):
        dlg = AboutDialog(self)
        dlg.ShowModal()
        dlg.Destroy()
        
        
    def getWikiPageTitle(self, wikiWord):
        title = re.sub(r'([A-Z\xc0-\xde]{2,})([a-z\xdf-\xff])', r'\1 \2', wikiWord)
        title = re.sub(r'([a-z\xdf-\xff])([A-Z\xc0-\xde])', r'\1 \2', title)
        if title.startswith("["):
            title = title[1:len(title)-1]
        return title


    def isLocaleEnglish(self):
        return self.locale.startswith('en_')

    # ----------------------------------------------------------------------------------------
    # Event handlers from here on out.
    # ----------------------------------------------------------------------------------------

    def OnWikiOpen(self, event):
        dlg = wxFileDialog(self, "Choose a Wiki to open", self.getLastActiveDir(), "", "*.wiki", wxOPEN)
        if dlg.ShowModal() == wxID_OK:
            self.openWiki(abspath(dlg.GetPath()))
        dlg.Destroy()


    def OnWikiNew(self, event):
        dlg = wxTextEntryDialog (self, "Name for new wiki (must be in the form of a WikiWord):",
                                 "Create New Wiki", "MyWiki", wxOK | wxCANCEL)
        
        if dlg.ShowModal() == wxID_OK:
            wikiName = dlg.GetValue()

            # make sure this is a valid wiki word
            if wikiName.find(' ') == -1 and WikiFormatting.isWikiWord(wikiName):
                dlg = wxDirDialog(self, "Directory to store new wiki", self.getLastActiveDir(), style=wxDD_DEFAULT_STYLE|wxDD_NEW_DIR_BUTTON)
                if dlg.ShowModal() == wxID_OK:
                    try:
                        self.newWiki(wikiName, dlg.GetPath())
                    except IOError, e:
                        self.displayErrorMessage('There was an creating your new Wiki.', e)
            else:
                self.displayErrorMessage("'%s' is an invalid WikiWord. There must be no spaces and mixed caps" % wikiName)

        dlg.Destroy()


    def OnSelectRecentWiki(self, event):
        recentItem = self.recentWikisMenu.FindItemById(event.GetId())
        if not self.openWiki(recentItem.GetText()):
            self.recentWikisMenu.Remove(event.GetId())


    def OnWikiPageUpdate(self, wikiPage):
        self.tree.buildTreeForWord(self.currentWikiWord)


    def OnFind(self, evt, next=False, replace=False, replaceAll=False):
        matchWholeWord = False
        matchCase = False
        
        et = evt.GetEventType()
        flags = evt.GetFlags()

        if flags == 3 or flags == 7:
            matchWholeWord = True
        if flags == 5 or flags == 7:
            matchCase = True

        findString = evt.GetFindString()
        if matchWholeWord:
            findString = "\\b%s\\b" % findString

        if et == wxEVT_COMMAND_FIND:
            self.editor.executeSearch(findString, caseSensitive=matchCase)
        elif et == wxEVT_COMMAND_FIND_NEXT:
            self.editor.executeSearch(findString, next=True, caseSensitive=matchCase)
        elif et == wxEVT_COMMAND_FIND_REPLACE:
            self.lastFindPos = self.editor.executeSearch(findString, self.lastFindPos, self.lastFindPos > -1, replacement=evt.GetReplaceString(), caseSensitive=matchCase)
        elif et == wxEVT_COMMAND_FIND_REPLACE_ALL:
            lastReplacePos = -1
            while(1):                
                lastReplacePos = self.editor.executeSearch(findString, lastReplacePos,
                                                           replacement=evt.GetReplaceString(),
                                                           caseSensitive=matchCase,
                                                           cycleToStart=False)
                if lastReplacePos == -1:
                    break


    def OnFindClose(self, evt, next=False, replace=False, replaceAll=False):
        evt.GetDialog().Destroy()


    def OnIdle(self, evt):
        if not self.autoSave:
            return
        # check if the current wiki page needs to be saved
        if self.currentWikiPage:
            (saveDirty, updateDirty) = self.currentWikiPage.getDirty()
            if saveDirty or updateDirty:
                currentTime = time()
                # only try and save if the user stops typing
                if (currentTime - self.editor.lastKeyPressed) > 3:
                    if saveDirty:
                        if (currentTime - self.currentWikiPage.lastSave) > 15:
                            self.saveCurrentWikiPage()
                    elif updateDirty:
                        if (currentTime - self.currentWikiPage.lastUpdate) > 5:
                            self.updateRelationships()
                

    def OnWikiExit(self, evt):
        # if the frame is not minimized 
        # update the size/pos of the global config
        if not self.IsIconized():
            curSize = self.GetSize()
            self.globalConfig.set("main", "size_x", str(curSize.x))
            self.globalConfig.set("main", "size_y", str(curSize.y))
            curPos = self.GetPosition()
            self.globalConfig.set("main", "pos_x", str(curPos.x))
            self.globalConfig.set("main", "pos_y", str(curPos.y))

        splitterPos = self.vertSplitter.GetSashPosition()
        if splitterPos == 0:
            splitterPos = self.lastSplitterPos
        self.globalConfig.set("main", "splitter_pos", str(splitterPos))
        self.globalConfig.set("main", "zoom", str(self.editor.GetZoom()))
        self.globalConfig.set("main", "wiki_history", ";".join(self.wikiHistory))
        self.writeGlobalConfig()

        # save the current wiki state
        self.saveCurrentWikiState()

        # trigger hook            
        self.wikidPadHooks.exit(self)

        wxTheClipboard.Flush()
        self.Destroy()


    def showRegistrationDialog(self, expired=False):
        dlg = None
        existingCode = ""

        if self.globalConfig.has_section("registration"):
            if self.globalConfig.has_option("registration", "code"):
                existingCode = self.globalConfig.get("registration", "code")

        if expired:
            dlg = wxTextEntryDialog (self, "You wikidPad evaluation period has expired. Please enter registration code:",
                                 "Enter Registration Code", existingCode, wxOK | wxCANCEL)
        else:
            dlg = wxTextEntryDialog (self, "Please enter registration code:",
                                 "Enter Registration Code", existingCode, wxOK | wxCANCEL)
            
        if dlg.ShowModal() == wxID_OK:
            code = dlg.GetValue()
            if code == REGISTRATION_CODE:
                if not self.globalConfig.has_section("registration"):
                    self.globalConfig.add_section("registration")                
                self.globalConfig.set("registration", "code", code)
                expired = False

                dlg_m = wxMessageDialog(self, "Thank you for purchasing wikidPad.", "Thank you", wxOK)
                dlg_m.ShowModal()
                dlg_m.Destroy()

            else:
                self.displayErrorMessage("Invalid registration code. Please visit http://www.jhorman.org/wikidPad/ to attain a valid code")

        # if the eval period has expired close down wikidPad                
        if expired:
            self.Close()

        dlg.Destroy()


class OpenWikiWordDialog(wxDialog):
    def __init__(self, pWiki, ID, title="Open Wiki Word",
                 pos=wxDefaultPosition, size=wxDefaultSize,
                 style=wxNO_3D):
        wxDialog.__init__(self, pWiki, ID, title, pos, size, style)
        self.pWiki = pWiki
        
        # Now continue with the normal construction of the dialog
        # contents
        sizer = wxBoxSizer(wxVERTICAL)

        label = wxStaticText(self, -1, "Open Wiki Word")
        sizer.Add(label, 0, wxALIGN_CENTRE|wxALL, 5)

        box = wxBoxSizer(wxVERTICAL)

        self.text = wxTextCtrl(self, -1, "", size=wxSize(145, -1))
        box.Add(self.text, 0, wxALIGN_CENTRE|wxALL, 5)

        self.lb = wxListBox(self, -1, wxDefaultPosition, wxSize(145, 200), [], wxLB_SINGLE)
        box.Add(self.lb, 1, wxALIGN_CENTRE|wxALL, 5)

        sizer.Add(box, 0, wxGROW|wxALIGN_CENTER_VERTICAL|wxALL, 5)

        line = wxStaticLine(self, -1, size=(20,-1), style=wxLI_HORIZONTAL)
        sizer.Add(line, 0, wxGROW|wxALIGN_CENTER_VERTICAL|wxRIGHT|wxTOP, 5)

        box = wxBoxSizer(wxHORIZONTAL)

        btn = wxButton(self, wxID_OK, " OK ")
        btn.SetDefault()
        box.Add(btn, 0, wxALIGN_CENTRE|wxALL, 5)

        btn = wxButton(self, wxID_CANCEL, " Cancel ")
        box.Add(btn, 0, wxALIGN_CENTRE|wxALL, 5)

        sizer.Add(box, 0, wxALIGN_CENTER_VERTICAL|wxALL, 5)

        self.SetSizer(sizer)
        self.SetAutoLayout(True)
        sizer.Fit(self)

        self.value = None

        EVT_TEXT(self, ID, self.OnText)
        EVT_LISTBOX(self, ID, self.OnListBox)

    def GetValue(self):
        if self.pWiki.wikiData.isWikiWord(self.value):
            return self.value
        else:
            words = self.pWiki.wikiData.getWikiWordsWith(self.value.lower())
            if len(words) > 0:
                return words[0]
            else:
                self.pWiki.displayErrorMessage("'%s' is not an existing wikiword" % self.value)
                return None

    def OnText(self, evt):
        self.value = evt.GetString()
        self.lb.Clear()
        if len(self.value) > 0:
            words = self.pWiki.wikiData.getWikiWordsWith(self.value.lower())
            for word in words:
                self.lb.Append(word)

    def OnListBox(self, evt):
        self.value = evt.GetString()


class SearchDialog(wxDialog):
    def __init__(self, pWiki, ID, title="Search Wiki",
                 pos=wxDefaultPosition, size=wxDefaultSize,
                 style=wxNO_3D):
        wxDialog.__init__(self, pWiki, ID, title, pos, size, style)
        self.pWiki = pWiki
        
        # Now continue with the normal construction of the dialog
        # contents
        sizer = wxBoxSizer(wxVERTICAL)

        label = wxStaticText(self, -1, "Wiki Search (regex supported)")
        sizer.Add(label, 0, wxALIGN_CENTRE|wxALL, 5)

        box = wxBoxSizer(wxVERTICAL)

        self.text = wxTextCtrl(self, -1, "", size=wxSize(165, -1))
        box.Add(self.text, 0, wxALIGN_CENTRE|wxALL, 5)

        btn = wxButton(self, wxID_FIND, " Search ")
        btn.SetDefault()
        box.Add(btn, 0, wxALIGN_CENTRE|wxALL, 5)

        self.lb = wxListBox(self, -1, wxDefaultPosition, wxSize(165, 200), [], wxLB_SINGLE)
        box.Add(self.lb, 1, wxALIGN_CENTRE|wxALL, 5)

        sizer.AddSizer(box, 0, wxGROW|wxALIGN_CENTER_VERTICAL|wxALL, 5)

        line = wxStaticLine(self, -1, size=(20,-1), style=wxLI_HORIZONTAL)
        sizer.Add(line, 0, wxGROW|wxALIGN_CENTER_VERTICAL|wxRIGHT|wxTOP, 5)

        box = wxBoxSizer(wxHORIZONTAL)

        btn = wxButton(self, wxID_OK, " OK ")
        box.Add(btn, 0, wxALIGN_CENTRE|wxALL, 5)

        btn = wxButton(self, wxID_SAVE, " Save Search ")
        box.Add(btn, 0, wxALIGN_CENTRE|wxALL, 5)

        btn = wxButton(self, wxID_CANCEL, " Cancel ")
        box.Add(btn, 0, wxALIGN_CENTRE|wxALL, 5)

        sizer.AddSizer(box, 0, wxALIGN_CENTER_VERTICAL|wxALL, 5)

        self.SetSizer(sizer)
        self.SetAutoLayout(True)
        sizer.Fit(self)

        self.value = None

        EVT_BUTTON(self, wxID_FIND, self.OnSearch)
        EVT_BUTTON(self, wxID_SAVE, self.OnSave)
        EVT_LISTBOX(self, ID, self.OnListBox)
        EVT_LISTBOX_DCLICK(self, ID, self.OnListBoxDClick)
        
    def GetValue(self):
        if self.value:
            return (self.value, self.text.GetValue())
        elif self.lb.GetCount() > 0:
            return (self.lb.GetString(0), self.text.GetValue())

    def OnSearch(self, evt):
        forStr = self.text.GetValue()
        self.lb.Clear()
        if len(forStr) > 0:
            for word in self.pWiki.wikiData.search(forStr):
                self.lb.Append(word)

    def OnSave(self, evt):
        forStr = self.text.GetValue()
        if len(forStr) > 0:
            self.pWiki.wikiData.saveSearch(forStr)
            self.EndModal(wxID_CANCEL)
        else:
            self.pWiki.displayErrorMessage("Invalid search string, can't save as view")

    def OnListBox(self, evt):
        self.value = evt.GetString()

    def OnListBoxDClick(self, evt):
        self.EndModal(wxID_OK)


class SavedSearchesDialog(wxDialog):
    def __init__(self, pWiki, ID, title="Saved Searches",
                 pos=wxDefaultPosition, size=wxDefaultSize,
                 style=wxNO_3D):
        wxDialog.__init__(self, pWiki, ID, title, pos, size, style)
        self.pWiki = pWiki
        
        # Now continue with the normal construction of the dialog
        # contents
        sizer = wxBoxSizer(wxVERTICAL)

        label = wxStaticText(self, -1, "Saved Searches")
        sizer.Add(label, 0, wxALIGN_CENTRE|wxALL, 5)

        label = wxStaticText(self, -1, "(to execute a saved search select")
        sizer.Add(label, 0, wxALIGN_CENTRE, 5)

        label = wxStaticText(self, -1, "searches under 'Views' in the tree)")
        sizer.Add(label, 0, wxALIGN_CENTRE, 5)

        box = wxBoxSizer(wxVERTICAL)

        self.lb = wxListBox(self, -1, wxDefaultPosition, wxSize(165, 200), [], wxLB_SINGLE)

        # fill in the listbox
        for search in self.pWiki.wikiData.getSavedSearches():
            self.lb.Append(search)

        box.Add(self.lb, 1, wxALIGN_CENTRE|wxALL, 5)

        sizer.AddSizer(box, 0, wxGROW|wxALIGN_CENTER_VERTICAL|wxALL, 5)

        line = wxStaticLine(self, -1, size=(20,-1), style=wxLI_HORIZONTAL)
        sizer.Add(line, 0, wxGROW|wxALIGN_CENTER_VERTICAL|wxRIGHT|wxTOP, 5)

        box = wxBoxSizer(wxHORIZONTAL)

        btn = wxButton(self, wxID_CLEAR, " Delete ")
        box.Add(btn, 0, wxALIGN_CENTRE|wxALL, 5)

        btn = wxButton(self, wxID_CANCEL, " Cancel ")
        box.Add(btn, 0, wxALIGN_CENTRE|wxALL, 5)

        sizer.AddSizer(box, 0, wxALIGN_CENTER_VERTICAL|wxALL, 5)

        self.SetSizer(sizer)
        self.SetAutoLayout(True)
        sizer.Fit(self)

        self.value = None

        EVT_BUTTON(self, wxID_CLEAR, self.OnDelete)
        EVT_LISTBOX(self, ID, self.OnListBox)
        
    def OnDelete(self, evt):
        if self.value:
            self.pWiki.wikiData.deleteSavedSearch(self.value)
            self.EndModal(wxID_CANCEL)            

    def OnListBox(self, evt):
        self.value = evt.GetString()


class AboutDialog(wxDialog):
    """ An about box that uses an HTML window """

    text = '''
<html>
<body bgcolor="#FFFFFF">
    <center>
        <table bgcolor="#CCCCCC" width="100%" cellspacing="0" cellpadding="0" border="1">
            <tr>
                <td align="center"><h2>wikidPad 1.16</h2></td>
            </tr>
        </table>

        <p>
wikidPad is a Wiki-like notebook for storing your thoughts, ideas, todo lists, contacts, or anything else you can think of to write down.
What makes wikidPad different from other notepad applications is the ease with which you can cross-link your information.        </p>        
        <br><br>

        <table border=0 cellpadding=1 cellspacing=0>            
            <tr><td width="30%" align="right"><font size="3"><b>Author:</b></font></td><td nowrap><font size="3">Jason Horman</font></td></tr>
            <tr><td width="30%" align="right"><font size="3"><b>Email:</b></font></td><td nowrap><font size="3">wikidpad@jhorman.org</font></td></tr>
            <tr><td width="30%" align="right"><font size="3"><b>URL:</b></font></td><td nowrap><font size="3">http://www.jhorman.org/wikidPad/</font></td></tr>
        </table>
    </center>
</body>
</html>
'''

    def __init__(self, parent):
        wxDialog.__init__(self, parent, -1, 'About WikidPad',
                          size=(470, 330) )

        html = wxHtmlWindow(self, -1)
        html.SetPage(self.text)
        button = wxButton(self, wxID_OK, "Okay")

        # constraints for the html window
        lc = wxLayoutConstraints()
        lc.top.SameAs(self, wxTop, 5)
        lc.left.SameAs(self, wxLeft, 5)
        lc.bottom.SameAs(button, wxTop, 5)
        lc.right.SameAs(self, wxRight, 5)
        html.SetConstraints(lc)

        # constraints for the button
        lc = wxLayoutConstraints()
        lc.bottom.SameAs(self, wxBottom, 5)
        lc.centreX.SameAs(self, wxCentreX)
        lc.width.AsIs()
        lc.height.AsIs()
        button.SetConstraints(lc)

        self.SetAutoLayout(True)
        self.Layout()
        self.CentreOnParent(wxBOTH)
        

def importCode(code,name,add_to_sys_modules=0):
    """
    Import dynamically generated code as a module. code is the
    object containing the code (a string, a file handle or an
    actual compiled code object, same types as accepted by an
    exec statement). The name is the name to give to the module,
    and the final argument says wheter to add it to sys.modules
    or not. If it is added, a subsequent import statement using
    name will return this module. If it is not added to sys.modules
    import will try to load it in the normal fashion.

    import foo

    is equivalent to

    foofile = open("/path/to/foo.py")
    foo = importCode(foofile,"foo",1)

    Returns a newly generated module.
    """
    import sys,imp

    module = imp.new_module(name)

    exec code in module.__dict__
    if add_to_sys_modules:
        sys.modules[name] = module

    return module
