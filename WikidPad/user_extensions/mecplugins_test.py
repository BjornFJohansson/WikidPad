#!/usr/bin/env python
# -*- coding: utf-8 -*-

WIKIDPAD_PLUGIN = (("MenuFunctions",1),)

import datetime
import re

def describeMenuItems(wiki):
    return ((test, _("test") + "\tCtrl-Shift-T", _("test")),)

def test(wiki,evt):    
    today = datetime.date.today()
    start = today - datetime.timedelta(days=today.weekday())
    weekdates = [(start+datetime.timedelta(days=R)).isoformat() for R in range(7)]
    wiki.openWikiPage(str(weekdates[0]))
    openpages =  wiki.getMainAreaPanel().getDocPagePresenters()

    for day in weekdates:
        presenter = wiki.createNewDocPagePresenterTab()
        presenter.openWikiPage(str(day))

    for page in openpages:
        if re.match("^\d{4}-\d{2}-\d{2}$",page.getWikiWord()):
            wiki.getMainAreaPanel().closePresenterTab(page)
        

            
    #wiki.getMainAreaPanel().showPresenter(page)
    wiki.openWikiPage('2019-12-13') # (today.isoformat())
    
    return


def test(wiki,evt):    
    today = datetime.date.today() + datetime.timedelta(weeks=1)
    start = today - datetime.timedelta(days=today.weekday())

    weekdates = [(start+datetime.timedelta(days=R)).isoformat() for R in range(7)]
    wiki.openWikiPage(str(weekdates[0]))
    openpages =  wiki.getMainAreaPanel().getDocPagePresenters()

    for page in openpages:
        if re.match("^\d{4}-\d{2}-\d{2}$",page.getWikiWord()):
            wiki.getMainAreaPanel().closePresenterTab(page) # RemovePage ?

    for day in weekdates:
        presenter = wiki.createNewDocPagePresenterTab()
        presenter.openWikiPage(str(day))
    wiki.getMainAreaPanel().showPresenter(page)
    return


    # MoveAfterInTabOrder
    # MoveBeforeInTabOrder
    
    # appendPresenterTab
    # closePresenterTab
    
    # getCurrentTabTitle
    
    # getDocPagePresenters
    
    
    # createNewDocPagePresenterTab

# ['AcceleratorTable', 'AcceptsFocus', 'AcceptsFocusFromKeyboard', 'AcceptsFocusRecursively', 'AddChild', 'AddFilter', 'AddPendingEvent', 'AdjustForLayoutDirection', 'AlwaysShowScrollbars', 'AssociateHandle', 'AutoLayout', 'BackgroundColour', 'BackgroundStyle', 'BeginRepositioningChildren', 'BestSize', 'BestVirtualSize', 'Bind', 'Border', 'CacheBestSize', 'CanAcceptFocus', 'CanAcceptFocusFromKeyboard', 'CanScroll', 'CanSetTransparent', 'CaptureMouse', 'Caret', 'Center', 'CenterOnParent', 'Centre', 'CentreOnParent', 'CharHeight', 'CharWidth', 'Children', 'ChildrenRepositioningGuard', 'ClassInfo', 'ClassName', 'ClearBackground', 'ClientAreaOrigin', 'ClientRect', 'ClientSize', 'ClientToScreen', 'ClientToWindowSize', 'Close', 'Connect', 'Constraints', 'ContainingSizer', 'ConvertDialogPointToPixels', 'ConvertDialogSizeToPixels', 'ConvertDialogToPixels', 'ConvertPixelsToDialog', 'Create', 'Cursor', 'DLG_UNIT', 'DefaultAttributes', 'DeletePendingEvents', 'Destroy', 'DestroyChildren', 'DestroyLater', 'Disable', 'Disconnect', 'DissociateHandle', 'DoEnable', 'DoFreeze', 'DoGetBestClientSize', 'DoGetBestSize', 'DoGetBorderSize', 'DoGetClientSize', 'DoGetPosition', 'DoGetSize', 'DoMoveWindow', 'DoSetClientSize', 'DoSetSize', 'DoSetSizeHints', 'DoSetWindowVariant', 'DoThaw', 'DoUpdateWindowUI', 'DragAcceptFiles', 'DropTarget', 'EffectiveMinSize', 'Enable', 'Enabled', 'EndRepositioningChildren', 'EventHandler', 'EvtHandlerEnabled', 'ExtraStyle', 'FindFocus', 'FindWindow', 'FindWindowById', 'FindWindowByLabel', 'FindWindowByName', 'Fit', 'FitInside', 'Font', 'ForegroundColour', 'Freeze', 'GetAcceleratorTable', 'GetAccessible', 'GetAutoLayout', 'GetBackgroundColour', 'GetBackgroundStyle', 'GetBestHeight', 'GetBestSize', 'GetBestVirtualSize', 'GetBestWidth', 'GetBorder', 'GetCapture', 'GetCaret', 'GetCharHeight', 'GetCharWidth', 'GetChildren', 'GetClassDefaultAttributes', 'GetClassInfo', 'GetClassName', 'GetClientAreaOrigin', 'GetClientRect', 'GetClientSize', 'GetConstraints', 'GetContainingSizer', 'GetContentScaleFactor', 'GetCursor', 'GetDefaultAttributes', 'GetDefaultBorder', 'GetDefaultBorderForControl', 'GetDefaultHIGBorder', 'GetDropTarget', 'GetEffectiveMinSize', 'GetEventHandler', 'GetEvtHandlerEnabled', 'GetExtraStyle', 'GetFont', 'GetForegroundColour', 'GetFullTextExtent', 'GetGrandParent', 'GetGtkWidget', 'GetHandle', 'GetHelpText', 'GetHelpTextAtPoint', 'GetId', 'GetLabel', 'GetLayoutDirection', 'GetMainWindowOfCompositeControl', 'GetMaxClientSize', 'GetMaxHeight', 'GetMaxSize', 'GetMaxWidth', 'GetMinClientSize', 'GetMinHeight', 'GetMinSize', 'GetMinWidth', 'GetName', 'GetNextHandler', 'GetNextSibling', 'GetParent', 'GetPopupMenuSelectionFromUser', 'GetPosition', 'GetPositionTuple', 'GetPrevSibling', 'GetPreviousHandler', 'GetRect', 'GetRefData', 'GetScreenPosition', 'GetScreenRect', 'GetScrollPos', 'GetScrollRange', 'GetScrollThumb', 'GetSize', 'GetSizeTuple', 'GetSizer', 'GetSizerProps', 'GetTextExtent', 'GetThemeEnabled', 'GetToolTip', 'GetToolTipText', 'GetTopLevelParent', 'GetUpdateClientRect', 'GetUpdateRegion', 'GetValidator', 'GetVirtualSize', 'GetVirtualSizeTuple', 'GetWindowBorderSize', 'GetWindowStyle', 'GetWindowStyleFlag', 'GetWindowVariant', 'GrandParent', 'Handle', 'HandleAsNavigationKey', 'HandleWindowEvent', 'HasCapture', 'HasExtraStyle', 'HasFlag', 'HasFocus', 'HasMultiplePages', 'HasScrollbar', 'HasTransparentBackground', 'HelpText', 'Hide', 'HideWithEffect', 'HitTest', 'Id', 'InformFirstDirection', 'InheritAttributes', 'InheritsBackgroundColour', 'InitDialog', 'InvalidateBestSize', 'IsBeingDeleted', 'IsDescendant', 'IsDoubleBuffered', 'IsEnabled', 'IsExposed', 'IsFocusable', 'IsFrozen', 'IsRetained', 'IsSameAs', 'IsScrollbarAlwaysShown', 'IsShown', 'IsShownOnScreen', 'IsThisEnabled', 'IsTopLevel', 'IsTransparentBackgroundSupported', 'IsUnlinked', 'Label', 'Layout', 'LayoutDirection', 'LineDown', 'LineUp', 'Lower', 'MacIsWindowScrollbar', 'MaxClientSize', 'MaxHeight', 'MaxSize', 'MaxWidth', 'MinClientSize', 'MinHeight', 'MinSize', 'MinWidth', 'Move', 'MoveAfterInTabOrder', 'MoveBeforeInTabOrder', 'MoveXY', 'Name', 'Navigate', 'NavigateIn', 'NewControlId', 'NextHandler', 'OnInternalIdle', 'PageDown', 'PageUp', 'Parent', 'PopEventHandler', 'PopupMenu', 'Position', 'PostCreate', 'PostSizeEvent', 'PostSizeEventToParent', 'PreviousHandler', 'ProcessEvent', 'ProcessEventLocally', 'ProcessPendingEvents', 'ProcessWindowEvent', 'ProcessWindowEventLocally', 'PushEventHandler', 'QueueEvent', 'Raise', 'Rect', 'Ref', 'RefData', 'Refresh', 'RefreshRect', 'RegisterHotKey', 'ReleaseMouse', 'RemoveChild', 'RemoveEventHandler', 'RemoveFilter', 'Reparent', 'SafelyProcessEvent', 'ScreenPosition', 'ScreenRect', 'ScreenToClient', 'ScrollLines', 'ScrollPages', 'ScrollWindow', 'SendDestroyEvent', 'SendIdleEvents', 'SendSizeEvent', 'SendSizeEventToParent', 'SetAcceleratorTable', 'SetAccessible', 'SetAutoLayout', 'SetBackgroundColour', 'SetBackgroundStyle', 'SetCanFocus', 'SetCaret', 'SetClientRect', 'SetClientSize', 'SetConstraints', 'SetContainingSizer', 'SetCursor', 'SetDefaultSizerProps', 'SetDimensions', 'SetDoubleBuffered', 'SetDropTarget', 'SetEventHandler', 'SetEvtHandlerEnabled', 'SetExtraStyle', 'SetFocus', 'SetFocusFromKbd', 'SetFocusIgnoringChildren', 'SetFont', 'SetForegroundColour', 'SetHelpText', 'SetId', 'SetInitialSize', 'SetLabel', 'SetLayoutDirection', 'SetMaxClientSize', 'SetMaxSize', 'SetMinClientSize', 'SetMinSize', 'SetName', 'SetNextHandler', 'SetOwnBackgroundColour', 'SetOwnFont', 'SetOwnForegroundColour', 'SetPalette', 'SetPosition', 'SetPreviousHandler', 'SetRect', 'SetRefData', 'SetScrollPos', 'SetScrollbar', 'SetSize', 'SetSizeHints', 'SetSizeHintsSz', 'SetSizeWH', 'SetSizer', 'SetSizerAndFit', 'SetSizerProp', 'SetSizerProps', 'SetStatusText', 'SetThemeEnabled', 'SetToolTip', 'SetToolTipString', 'SetTransparent', 'SetValidator', 'SetVirtualSize', 'SetVirtualSizeWH', 'SetWindowStyle', 'SetWindowStyleFlag', 'SetWindowVariant', 'ShouldInheritColours', 'Show', 'ShowWithEffect', 'Shown', 'Size', 'Sizer', 'Thaw', 'ThemeEnabled', 'ToggleWindowStyle', 'ToolTip', 'TopLevel', 'TopLevelParent', 'TransferDataFromWindow', 'TransferDataToWindow', 'TryAfter', 'TryBefore', 'UnRef', 'UnShare', 'Unbind', 'Unlink', 'UnregisterHotKey', 'UnreserveControlId', 'UnsetToolTip', 'Update', 'UpdateClientRect', 'UpdateRegion', 'UpdateWindowUI', 'UseBgCol', 'Validate', 'Validator', 'VirtualSize', 'WarpPointer', 'WindowStyle', 'WindowStyleFlag', 'WindowToClientSize', 'WindowVariant', '_MiscEventSourceMixin__miscevent', '__bool__', '__class__', '__delattr__', '__dict__', '__dir__', '__doc__', '__eq__', '__format__', '__ge__', '__getattribute__', '__gt__', '__hash__', '__init__', '__init_subclass__', '__le__', '__lt__', '__module__', '__ne__', '__new__', '__nonzero__', '__reduce__', '__reduce_ex__', '__repr__', '__setattr__', '__sizeof__', '__str__', '__subclasshook__', '__weakref__', 'close', 'createFromPerspective', 'currentDocPageProxyEvent', 'deleteForNewPerspective', 'displayErrorMessage', 'displayMessage', 'docPage', 'fillDefaultSubControls', 'fireMiscEventKeys', 'fireMiscEventProps', 'getAUITabCtrl', 'getAUITabPage', 'getActiveEditor', 'getConfig', 'getCurrentDocPageProxyEvent', 'getCurrentSubControl', 'getCurrentSubControlName', 'getDefaultFontFaces', 'getDocPage', 'getLayerVisible', 'getLiveText', 'getLongTitle', 'getMainControl', 'getMiscEvent', 'getPageHistory', 'getPerspectiveType', 'getShortTitle', 'getStatusBar', 'getStoredPerspective', 'getSubControl', 'getTabContextMenu', 'getUnifiedPageName', 'getWikiDocument', 'getWikiWord', 'goUpwardFromSubpage', 'hasSubControl', 'informEditorTextChanged', 'isCurrent', 'lastVisibleCtrlName', 'loadWikiPage', 'longTitle', 'mainControl', 'mainTreePositionHint', 'makeCurrent', 'miscEventHappened', 'onProgressBarClicked', 'onProgressBarContext', 'openDocPage', 'openFuncPage', 'openWikiPage', 'pageHistory', 'removeMiscEvent', 'saveCurrentDocPage', 'setByStoredPerspective', 'setDocPage', 'setLayerVisible', 'setSubControl', 'setTabProgress', 'setTabProgressThreadSafe', 'setTabTitleColour', 'setTitle', 'shortTitle', 'showStatusMessage', 'stdDialog', 'subControls', 'switchSubControl', 'tabContextMenu', 'tabProgressBar', 'tabProgressCount', 'viewPageHistory', 'visible']
