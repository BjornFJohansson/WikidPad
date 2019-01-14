#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Insert Symbols 2, Wikidpad plugin
# by alessandro orsi
# v1.1, 12 Mar 2011, license GPL


import wx
import sys

from WikidPad.lib.pwiki.SystemInfo import isWindows
from WikidPad.Consts import VERSION_STRING

   
WIKIDPAD_VERSION = VERSION_STRING[9:12]




# ////////////////////   
#   Helper functions
# \\\\\\\\\\\\\\\\\\\\

def str_to_bool(string):

    """ Converts a True/False string to the corresponding boolean value """
       
    return string.lower() in ('true', 'yes', '1')


def wrong_wikidpad_version():

    """ Checks if we are running on Wikidpad 1.9 """

    if WIKIDPAD_VERSION == '1.9':
    
        dlg = wx.MessageDialog(None, 'This version of Insert Symbols plugin is not compatible with Wikidpad 1.9\n\nPlease, download version 0.3.3 instead.', 'Insert Symbols', style=wx.OK | wx.ICON_EXCLAMATION)

        dlg.ShowModal()
        
        return(True)

    

def get_wikidpad_font(pwikiframe, font_size):
            
    """ Retrieve the global font face used in the editor view for the current wiki
        If no global font face is set, revert to the default one (monospaced)  """
         
        
    # We have to check which Wikidpad version is running to use either 
    # getGlobalAttributeValue() for WP_2.1, or getGlobalPropertyValue() for WP_2.0
    
    
    if WIKIDPAD_VERSION == '2.0':

        try:

            font_face = pwikiframe.getWikiDocument().getGlobalPropertyValue('font')
            
            
        except:
        
            font_face = None        
        
            
    else:
            
        try:
        
            font_face = pwikiframe.getWikiDocument().getGlobalAttributeValue('font')
            
        except:
        
            font_face = None
                
           
    if font_face is None:
    
        font_face = pwikiframe.presentationExt.faces['mono']
        
        
    # wx.font: pointSize, family, style, weight, underline=False, face
    font = wx.Font(int(font_size), wx.DEFAULT, wx.NORMAL, wx.NORMAL, False, font_face)
        
    return(font)
    
 
      
      

# //////////////////////   
#    WIKIDPAD HOOKS
# \\\\\\\\\\\\\\\\\\\\\\



# Descriptor for Insert Symbols plugin
WIKIDPAD_PLUGIN = (('MenuFunctions',1),('Options', 1))



# /// Register menu item \\\
def describeMenuItems(wiki):
    

    
    keybindings = wiki.getKeyBindings()
    
    kb = keybindings.InsertSymbols
    if kb == '':        
        kb = 'Ctrl-Shift-I'
    #print kb
    return ((insert_symbols, 'Insert symbols' + '\t' + kb , ''),)


    
# /// Options panel \\\

def registerOptions(ver, app):
    """
    API function for 'Options' plugins
    Register configuration options and their GUI presentation
    ver -- API version (can only be 1 currently)
    app -- wxApp object
    """
    
    # If we are running on Wikidpad 1.9, exit
    if wrong_wikidpad_version():
    
        return
    
    
    # Register options and set defaults
    app.getDefaultGlobalConfigDict()[('main', 'plugin_insertSymbols_symbolsList')] = u'→, ←, •, √, ±, ≠, ×, ÷, ↑, ↓, ↔'
    
    app.getDefaultGlobalConfigDict()[('main', 'plugin_insertSymbols_fontSize')] = '12'
    
    app.getDefaultGlobalConfigDict()[('main', 'plugin_insertSymbols_window_width')] = '160'
    
    app.getDefaultGlobalConfigDict()[('main', 'plugin_insertSymbols_window_height')] = '185'
    
    app.getDefaultGlobalConfigDict()[('main', 'plugin_insertSymbols_window_xpos')] = ''
    
    app.getDefaultGlobalConfigDict()[('main', 'plugin_insertSymbols_window_ypos')] = ''
    
    app.getDefaultGlobalConfigDict()[('main', 'plugin_insertSymbols_modkey')] = 'Shift'
    
    app.getDefaultGlobalConfigDict()[('main', 'plugin_insertSymbols_pinned')] = 'False'
    
    
    # Add panel in options dialog
    app.addGlobalPluginOptionsDlgPanel(InsertSymbolsOptionsPanel, 'Insert Symbols')
    
    
    
    
class InsertSymbolsOptionsPanel(wx.Panel):
    def __init__(self, parent, optionsDlg, mainControl):
        """
        Called when 'Options' dialog is opened to show the panel.
        Transfer here all options from the configuration file into the
        text fields, check boxes, ...
        """
        
        self.pwikiframe = mainControl
        
        self.app = wx.GetApp()
        
        wx.Panel.__init__(self, parent)
        

        # Read options form Wikidpad config file      
        symbols_list = self.app.getGlobalConfig().get('main', 'plugin_insertSymbols_symbolsList', '')
        
        font_size = self.app.getGlobalConfig().get('main', 'plugin_insertSymbols_fontSize', '')
        
        mod_key = self.app.getGlobalConfig().get('main', 'plugin_insertSymbols_modkey', '')
        
        pinned_state = str_to_bool(self.app.getGlobalConfig().get('main', 'plugin_insertSymbols_pinned', ''))
        
        
        # //// Build option panel \\\\
        
        v_sizer = wx.BoxSizer( wx.VERTICAL )
        
        
        # Symbols list label + textctrl
        self.symbols_label = wx.StaticText( self, wx.ID_ANY, 'Comma separated list of symbols to display in the symbols list:', wx.DefaultPosition, wx.DefaultSize, style=wx.ALIGN_LEFT )
        
        self.symbols_label.Wrap( -1 )
        
        v_sizer.Add( self.symbols_label, 0, wx.ALL, 5 )
        
        self.symbols_textctrl = wx.TextCtrl( self, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, size=(-1, 100), style=wx.TE_MULTILINE)
        
        # Get Wikidpad font to display the symbols in the textctrl
        wp_font = get_wikidpad_font(self.pwikiframe, int(font_size)) 
        self.symbols_textctrl.SetFont(wp_font)
              
        v_sizer.Add( self.symbols_textctrl, 0, wx.ALL | wx.EXPAND, 5 )
        
        # Update symbols textctrl with data read from WP config file
        self.symbols_textctrl.SetValue(symbols_list)
        
        
        # Font size label + textctrl
        h_sizer = wx.BoxSizer( wx.HORIZONTAL )
        
        self.fontsize_label = wx.StaticText( self, wx.ID_ANY, 'Font Size:', wx.DefaultPosition, wx.DefaultSize, 0 )
        
        self.fontsize_label.Wrap( -1 )
        
        h_sizer.Add( self.fontsize_label, 0, wx.ALL, 5 )
		
        self.fontsize_textctrl = wx.TextCtrl( self, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.Size( 40,-1 ), wx.TE_RIGHT )
        
        
        # Update fontsize textctrl with data read from WP config file
        self.fontsize_textctrl.SetValue(font_size)
        
        h_sizer.Add( self.fontsize_textctrl, 0, wx.ALL, 5 )
        
        v_sizer.Add( h_sizer )
        
        
        # Radio box: modifier-key choice
        mod_key_radioboxChoices = [ 'Alt', 'Ctrl', 'Shift' ]
        
        self.mod_key_radiobox = wx.RadioBox( self, wx.ID_ANY, 'Symbols window remains open when holding down', wx.DefaultPosition, wx.DefaultSize, mod_key_radioboxChoices, 1, wx.RA_SPECIFY_ROWS )
        
        self.mod_key_radiobox.SetForegroundColour('black')
        
        # Select the correct radiobox according to what is stored in the options
        
        key_to_value = {'Alt':0, 'Ctrl':1, 'Shift':2}
        
        self.mod_key_radiobox.SetSelection( key_to_value[mod_key] )
        
        v_sizer.Add( self.mod_key_radiobox, 0, wx.ALL, 5 )
        
        
        # Pinned checkbox
        
        self.pinned_checkbox = wx.CheckBox( self, wx.ID_ANY, "Symbols window stays always open ", wx.DefaultPosition, wx.DefaultSize, 0 )
        
        self.pinned_checkbox.SetValue(pinned_state)
        
        v_sizer.Add( self.pinned_checkbox, 0, wx.ALL, 5 )
		
     
        self.SetSizer(v_sizer)
        
        self.Fit()
        
        
    def setVisible(self, vis):
        """
        Called when panel is shown or hidden. The actual wxWindow.Show()
        function is called automatically.
        
        If a panel is visible and becomes invisible because another panel is
        selected, the plugin can veto by returning False.
        When becoming visible, the return value is ignored.
        """
        return True

        
    def checkOk(self):
        """
        Called when 'OK' is pressed in dialog. The plugin should check here if
        all input values are valid. If not, it should return False, then the
        Options dialog automatically shows this panel.
        
        There should be a visual indication about what is wrong (e.g. red
        background in text field). Be sure to reset the visual indication
        if field is valid again.
        """
        return True

        
    def handleOk(self):
        """
        This is called if checkOk() returned True for all panels. Transfer here
        all values from text fields, checkboxes, ... into the configuration
        file.
        """
        
        new_symbols_list = self.symbols_textctrl.GetValue()
        
        # Sanitize string before writing to option file
        new_symbols_list = new_symbols_list.replace(' ','')
        new_symbols_list = new_symbols_list.rstrip(',')
        new_symbols_list = new_symbols_list.replace(',',', ') # comma+space to improve readability
        
        self.app.getGlobalConfig().set('main', 'plugin_insertSymbols_symbolsList', str(new_symbols_list))
        
        # Font size
        new_font_size = self.fontsize_textctrl.GetValue()
        
        self.app.getGlobalConfig().set('main', 'plugin_insertSymbols_fontSize', str(new_font_size))
        
        # Modifier key
        modkey = self.mod_key_radiobox.GetStringSelection()
        
        self.app.getGlobalConfig().set('main', 'plugin_insertSymbols_modkey', str(modkey))
                
        # Pinned checkbox
        pinned = str(self.pinned_checkbox.GetValue())
        
        self.app.getGlobalConfig().set('main', 'plugin_insertSymbols_pinned', str(pinned))
        
        return


        

# /////////////////////
#   Symbols frame 
# \\\\\\\\\\\\\\\\\\\\\
    
class SymbolsWindow(wx.Frame):

    """ Builds wx.Frame for the ListCtrl """

    def __init__(self,  parent, symbols_list, window_size, font_size, window_position):
        
        self.pwikiframe = parent
        
        self.app = wx.GetApp()
       

        wx.Frame.__init__(self, parent, -1, 'Symbols', pos=(window_position['x'], window_position['y']), size=(window_size['w'], window_size['h']), style = wx.CAPTION | wx.SYSTEM_MENU | wx.CLIP_CHILDREN | wx.CLOSE_BOX | wx.RESIZE_BORDER | wx.FRAME_TOOL_WINDOW | wx.FRAME_FLOAT_ON_PARENT, name='symbols_window_frame' )
        
  
  
        # //// ListCtrl \\\\

        self.list_ctrl = wx.ListCtrl(self, -1, (-1, -1), (-1, -1), wx.LC_REPORT|wx.LC_NO_HEADER|wx.LC_SINGLE_SEL)

        
        self.list_ctrl.InsertColumn(0, '', width=-1)

        # populate the list
        
        symbols_list = symbols_list.replace(' ','')
        
        self.symbols = symbols_list.split(',')
        
        for symbol in self.symbols:

            self.list_ctrl.InsertStringItem(sys.maxsize, symbol)           
        
        

        # Set the font of the listctrl to the same font used in Wikidpad
        wp_font = get_wikidpad_font(self.pwikiframe, font_size)
        self.list_ctrl.SetFont(wp_font)
        
        # Activate and set focus on the first element of the list
        self.list_ctrl.SetItemState(0, wx.LIST_STATE_SELECTED, wx.LIST_STATE_SELECTED)
        self.list_ctrl.SetItemState(0, wx.LIST_STATE_FOCUSED, wx.LIST_STATE_FOCUSED)

         
         
        # //// Events binding \\\\
        
        self.Bind(wx.EVT_MOVE, self.OnMove)
        self.Bind(wx.EVT_SIZE, self.OnSize)
         
        self.list_ctrl.Bind(wx.EVT_KEY_DOWN, self.onKeyPress)       
        self.list_ctrl.Bind(wx.EVT_LIST_ITEM_ACTIVATED, self.OnActivated)
    
    
    
    # //// Helper functions \\\\
    
    def check_modifier(self):
    
        """ Finds out which modifier key should be checked and returns if pressed (True) or not """
    
        state = wx.GetMouseState()
            
        
        modkey = self.app.getGlobalConfig().get('main', 'plugin_insertSymbols_modkey', '')
        
        
        if modkey == 'Alt':
        
            modifier = state.altDown
            
        elif modkey == 'Ctrl':
        
            modifier = state.controlDown
        
        else:
       
            modifier = state.shiftDown
            
        return modifier
    
    

    # ////  Events handlers \\\\
       
    
    def OnMove(self, event):
        
        """ Stores the symbols window position in the WP config file """
        
        x,y = self.GetPosition() 
        
        self.app.getGlobalConfig().set('main', 'plugin_insertSymbols_window_xpos', x)
    
        self.app.getGlobalConfig().set('main', 'plugin_insertSymbols_window_ypos', y)
        
        event.Skip()
    
    
    def OnSize(self, event):
    
        """ Stores the symbols window size in the WP config file """
        
        width, height = self.GetSize()
        
        self.app.getGlobalConfig().set('main', 'plugin_insertSymbols_window_width', width)
        
        self.app.getGlobalConfig().set('main', 'plugin_insertSymbols_window_height', height)
        
        event.Skip()
        
        
    def onKeyPress(self, event):
    
        """ Catches ESC and ENTER key events """

        keycode = event.GetKeyCode()
        
        # Close symbols window if ESC is pressed 
        if keycode == wx.WXK_ESCAPE:
        
            self.Destroy()
            
        
        # == Windows ONLY ==
        #
        # Handle insertion of symbols when ENTER is pressed together with a modifier key 
        #
        # On Windows, EVT_LIST_ITEM_ACTIVATED is triggered only when ENTER *alone* is pressed,
        # not if in combination with other modifiers. On Linux, on the contrary, it's triggered
        # even if a modifier key is pressed
        
        if isWindows():
            if keycode == wx.WXK_RETURN:
                
                modkey = self.check_modifier()
                
                pinned = str_to_bool(self.app.getGlobalConfig().get('main', 'plugin_insertSymbols_pinned', ''))
                          
                if modkey and not pinned: 
                
                    selected_item = self.list_ctrl.GetNextItem(-1, wx.LIST_NEXT_ALL, wx.LIST_STATE_SELECTED)
                   
                    self.pwikiframe.getActiveEditor().ReplaceSelection(self.symbols[selected_item])
                    
                    # This doesn't work on Linux, see OnActivated() below
                    self.pwikiframe.getActiveEditor().SetFocus()
            
            
        event.Skip()

        

    def OnActivated(self, event):
    
        """ Inserts the selected symbol of the ListCtrl into Wikidpad editor """
        
        selected_item = self.list_ctrl.GetNextItem(-1, wx.LIST_NEXT_ALL, wx.LIST_STATE_SELECTED)        
        
        self.pwikiframe.getActiveEditor().ReplaceSelection(self.symbols[selected_item])
        
       
        # Check if a modifier key is pressed, or if the window is pinned otherwise close it
        modkey = self.check_modifier()
        
        pinned = str_to_bool(self.app.getGlobalConfig().get('main', 'plugin_insertSymbols_pinned', ''))
        
        if modkey or pinned:
        
            # This doesn't work on Linux, where the focus remains on the symbols window
            # I tried:
            # a Raise() before a the SetFocus(), and a Raise() and SetFocus() on the panel,
            # parent of the StyleTextCtrl(), accessed via GetParent()
            self.pwikiframe.getActiveEditor().SetFocus()
                  
            return
        
        self.Destroy()          
        




# ///////////////////////////////////////
#    Main function called by Wikidpad 
# \\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\

def insert_symbols(wiki, evt):
    
    """ Insert Symbols main function called by WikidPad """ 
    
    # If we are running on Wikidpad 1.9, exit
    if wrong_wikidpad_version():
    
        return
        

    # If symbols window is pinned, do not open another one but set the focus on the one 
    # currently opened. (!) FindWindowByLabel() that would match the window title is 
    # OS dependent and doesn't work on Linux
    symbols_window = wiki.FindWindowByName('symbols_window_frame')
    
    if symbols_window is not None:
        symbols_window.Raise()
        symbols_window.list_ctrl.SetFocus()
        return
    
    

    app = wx.GetApp()
    
    
    # Read options from config file
    symbols_list = app.getGlobalConfig().get('main', 'plugin_insertSymbols_symbolsList', '')
    
    font_size = app.getGlobalConfig().get('main', 'plugin_insertSymbols_fontSize', '')
    
    width = app.getGlobalConfig().get('main', 'plugin_insertSymbols_window_width', '')
    
    height = app.getGlobalConfig().get('main', 'plugin_insertSymbols_window_height', '')
    
    x = app.getGlobalConfig().get('main', 'plugin_insertSymbols_window_xpos', '')
    
    y = app.getGlobalConfig().get('main', 'plugin_insertSymbols_window_ypos', '')  
    
    
    window_size = {'w':int(width), 'h':int(height)}
    
    
    # Center the symbols window if no previous position was set
    
    if x == '' and y == '':

        # Calculate center position for current symbols window size
        x_scr, y_scr = wx.GetDisplaySize()
        
        x_center = (x_scr - window_size['w'])/2
        
        y_center = (y_scr - window_size['h'])/2
        
        window_position = {'x':x_center, 'y':y_center}
    
    else:
    
        window_position = {'x':int(x), 'y':int(y)}
    
    
    
    # Create InserSymbols main window
    symbols_window = SymbolsWindow(wiki, symbols_list, window_size, font_size, window_position)

    symbols_window.Show()
    
    symbols_window.Raise()  # for Linux, or the listctrl won't get the focus
    symbols_window.list_ctrl.SetFocus()
    

#EOF
