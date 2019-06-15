#!/usr/bin/env python
# -*- coding: utf-8 -*-
#############################################
#  _____        _        _    _ _   _ _
# |  __ \      | |      | |  | | | (_) |
# | |  | | __ _| |_  ___| |  | | |_ _| |___
# | |  | |/ _` | __|/ _ \ |  | | __| | / __|
# | |__| | (_| | |_|  __/ |__| | |_| | \__ \
# |_____/ \__,_|\__|\___|\____/ \__|_|_|___/
#############################################

#WIKIDPAD_PLUGIN = (("MenuFunctions",1),)
WIKIDPAD_PLUGIN = (("ToolbarFunctions",2), ("ToolbarFunctions",1), ("MenuFunctions",1))

#from . import mecplugins_ini
import wx
import wx.stc
import WikidPad.lib.pwiki.SearchAndReplace as Sar
import datetime
import calendar
import time
#import string
import webbrowser
import re
import uuid
import sys

#from pwiki.wikidata.WikiDataManager import WikiDataManager
from WikidPad.lib.pwiki.wxHelper  import copyTextToClipboard
from WikidPad.lib.pwiki.StringOps import strftimeUB

def describeMenuItems(wiki):
    return (
            (calctrl,             _(u"mecplugins|Date utils|Calendar"),                    _(u"mec_calendar")),
            (prev,                _(u"mecplugins|Date utils|Previous date"),               _(u"previous")),
            (yesterday,           _(u"mecplugins|Date utils|Yesterday"),                   _(u"yesterday")),
            (today,               _(u"mecplugins|Date utils|Today"),                       _(u"today")),
            (close_tabs,          _(u"mecplugins|Date utils|close tabs"),                  _(u"close tabs")),
            (tomorrow,            _(u"mecplugins|Date utils|Tomorrow"),                    _(u"tomorrow")),
            (next_,               _(u"mecplugins|Date utils|Next date"),                   _(u"next")),
            (nextyear,            _(u"mecplugins|Date utils|Next year"),                   _(u"next year")),
            (copydatetoclipboard, _(u"mecplugins|Date utils|Copy date to clipboard"),      _(u"copy date to clipboard")),
            (copylink,            _(u"mecplugins|Date utils|Copy current page name"),      _(u"copy current page name")),
            (thisweek,            _(u"mecplugins|Date utils|this week"),                   _(u"this week")),
            (nextweek,            _(u"mecplugins|Date utils|next week"),                   _(u"next week")),
            (nextmonth,           _(u"mecplugins|Date utils|next month"),                  _(u"next month")),
            (nextyear,            _(u"mecplugins|Date utils|next year"),                   _(u"next year")),
            (inserttime,          _(u"mecplugins|Date utils|insert time / uuid4\tF5"),      _(u"insert time")),            
            (weekday_list,        _(u"mecplugins|Date utils|weekday list"),                _(u"weekday list")),
            )

def describeToolbarItemsV02(wiki):
    return (
            (close_tabs,                _(u"close tabs"),               _(u"close tabs"),               ("up arrow",),            None,   None, close_tabsrightclick),
            (prev,                      _(u"previous defined"),         _(u"previous defined"),         ("left arrow",),          None,   None, prevrightclick),
            (yesterday,                 _(u"yesterday"),                _(u"yesterday"),                ("arrow_left",),          None,   None, yesterdayrightclick),
            (today,                     _(u"today"),                    _(u"today"),                    ("mec_today",),           None,   None, todayrightclick),    
            (tomorrow,                  _(u"tomorrow"),                 _(u"tomorrow"),                 ("arrow_right",),         None,   None, tomorrowrightclick),
            (next_,                     _(u"next defined"),             _(u"next defined"),             ("right arrow",),         None,   None, nextrightclick),
            (calctrl,                   _(u"calendar"),                 _(u"calendar"),                 ("calendar",),),
            (copylink,                  _(u"copy link"),                _(u"copy link"),                ("mec_anchor",),),
            (thisweek,                  _(u"thisweek"),                 _(u"this week"),                ("mec_thisweekandnext",), None,   None, nextweek),
            (nextyear,                  _(u"last or next year"),        _(u"last or next year"),        ("user",),                None,   None, lastyear),
            (inserttime,                _(u"insert time / uuid4"),      _(u"insert time / uuid4"),      ("time",),                None,   None, insertuuid),
            )


def close_tabs(wiki, evt):
    here = wiki.getCurrentWikiWord()
    openpages =  wiki.getMainAreaPanel().getDocPagePresenters()
    for page in openpages:
        if page.getWikiWord()!=here:
            wiki.getMainAreaPanel().closePresenterTab(page)
    return

def close_tabsrightclick(wiki, evt):
    return

def inserttime(wiki, evt):
    wiki.getActiveEditor().ReplaceSelection("{} ".format(time.strftime("%H:%M:%S", time.localtime())))
    return

def insertuuid(wiki, evt):
    wiki.getActiveEditor().ReplaceSelection(str(uuid.uuid4()))
    return


def prevrightclick(wiki, evt):
    openpages =  wiki.getMainAreaPanel().getDocPagePresenters()

    lpOp2 = Sar.ListWikiPagesOperation()
    lpOp2.ordering = "ascending"
    item2 = Sar.RegexWikiPageNode(lpOp2, "^\d{4}-\d{2}-\d{2}$")
    lpOp2.setSearchOpTree(item2)
    searchOp = Sar.SearchReplaceOperation()
    searchOp.wildCard = "no"
    searchOp.wikiWide = True
    searchOp.listWikiPagesOp = lpOp2
    searchfrag = wiki.getActiveEditor().GetSelectedText()
    if searchfrag:
        selection_start, selection_end = wiki.getActiveEditor().GetSelectionCharPos()
        searchOp.searchStr = searchfrag
        datelist = wiki.getWikiDocument().searchWiki(searchOp)
    else:
        datelist = wiki.getWikiDocument().searchWiki(searchOp)
    here = wiki.getCurrentWikiWord()
    today = datetime.date.today().isoformat()
    try:
        now = datetime.date(*time.strptime(here, "%Y-%m-%d")[0:3])
    except ValueError:
        before = today
    before = datelist[datelist.index(str(now))-1]

    if not searchfrag:
        page_already_open = False
        for page in openpages:
            if page.getWikiWord()==before:
                page_already_open = True
                wiki.getMainAreaPanel().showPresenter(page)
        if not page_already_open:
            presenter = wiki.createNewDocPagePresenterTab()
            presenter.openWikiPage(before)
            wiki.getMainAreaPanel().showPresenter(presenter)
    else: # search for something in the page
        before = str(now)
        newpos = wiki.getActiveEditor().GetText().lower().rfind(searchfrag.lower(),0,selection_start)
        if newpos==-1:
            before = datelist[datelist.index(str(before))-1]
            page_already_open = False
            for page in openpages:
                if page.getWikiWord()==before:
                    page_already_open = True
                    wiki.getMainAreaPanel().showPresenter(page)
                    break
            if not page_already_open:
                presenter = wiki.createNewDocPagePresenterTab()
                presenter.openWikiPage(before)
                wiki.getMainAreaPanel().showPresenter(presenter)
            newpos = wiki.getActiveEditor().GetText().lower().rfind(searchfrag.lower())
        wiki.getActiveEditor().SetSelectionByCharPos(newpos,newpos+len(searchfrag))
        wiki.getActiveEditor().unfoldAll()
    return

def prev(wiki, evt):
    searchfrag = wiki.getActiveEditor().GetSelectedText()

    lpOp2 = Sar.ListWikiPagesOperation()
    lpOp2.ordering = "ascending"
    item2 = Sar.RegexWikiPageNode(lpOp2, "^\d{4}-\d{2}-\d{2}$")
    lpOp2.setSearchOpTree(item2)

    here = wiki.getCurrentWikiWord()
    today = datetime.date.today().isoformat()

    searchOp = Sar.SearchReplaceOperation()
    searchOp.wildCard = "no"
    searchOp.wikiWide = True
    searchOp.listWikiPagesOp = lpOp2

    if searchfrag!='':
        selection_start, selection_end = wiki.getActiveEditor().GetSelectionCharPos()
        searchOp.searchStr = searchfrag
        datelist = wiki.getWikiDocument().searchWiki(searchOp)
    else:
        datelist = wiki.getWikiDocument().searchWiki(searchOp)

    try:
        now = datetime.date(*time.strptime(here, "%Y-%m-%d")[0:3])
    except ValueError:
        before = today

    before = datelist[datelist.index(str(now))-1]

    if searchfrag=='':
        wiki.openWikiPage(before)

    else: # search for something in the page
        before = str(now)
        newpos = wiki.getActiveEditor().GetText().lower().rfind(searchfrag.lower(),0,selection_start)

        if newpos==-1:
            before = datelist[datelist.index(str(before))-1]
            wiki.openWikiPage(before)
            newpos = wiki.getActiveEditor().GetText().lower().rfind(searchfrag.lower())

        wiki.getActiveEditor().SetSelectionByCharPos(newpos,newpos+len(searchfrag))
        wiki.getActiveEditor().unfoldAll()
    return

def today(wiki, evt):
    today = datetime.date.today().isoformat()
    openpages =  wiki.getMainAreaPanel().getDocPagePresenters()
    for page in openpages:
        if page.getWikiWord()==today:
            wiki.getMainAreaPanel().showPresenter(page)
            return
    #presenter = wiki.createNewDocPagePresenterTab()
    #presenter.openWikiPage(today)
    #wiki.getMainAreaPanel().showPresenter(presenter)
    wiki.openWikiPage(today)
    return

def todayrightclick(wiki, evt):
    todaywasopen=False
    today = datetime.date.today().isoformat()
    openpages =  wiki.getMainAreaPanel().getDocPagePresenters()
    for page in openpages:
        if page.getWikiWord()==today:
            wiki.getMainAreaPanel().showPresenter(page)
            todaywasopen = True      
        #elif re.match("^\d{4}-\d{2}-\d{2}$",page.getWikiWord()):
        #    wiki.getMainAreaPanel().closePresenterTab(page)
    if not todaywasopen:
        presenter = wiki.createNewDocPagePresenterTab()
        presenter.openWikiPage(today)
        wiki.getMainAreaPanel().showPresenter(presenter)
    return

def thisweek(wiki, evt):
#    here = wiki.getCurrentWikiWord()
#    try:
#        today = datetime.date(*time.strptime(here, "%Y-%m-%d")[0:3])
#    except ValueError:
#        today = datetime.date.today()
    
    today = datetime.date.today()
    weeknumber = int(today.strftime("%W")) #((today - datetime.date(today.year,1,1)).days / 7) + 1
    
    d = datetime.date(today.year,1,1)
    
    if(d.weekday()>3):
        d = d+datetime.timedelta(7-d.weekday())
    else:
        d = d - datetime.timedelta(d.weekday())
        
    dlt = datetime.timedelta(days = (weeknumber-1) * 7)
    
    weekdates = [(d+dlt+datetime.timedelta(days=R)).isoformat() for R in range(7)]
    
    openpages =  wiki.getMainAreaPanel().getDocPagePresenters()

    for page in openpages:
        if re.match("^\d{4}-\d{2}-\d{2}$",page.getWikiWord()):
            wiki.getMainAreaPanel().closePresenterTab(page)

    wiki.openWikiPage(str(weekdates[0]))
    for day in weekdates[1:]:
        presenter = wiki.createNewDocPagePresenterTab()
        presenter.openWikiPage(str(day))
        if day==today.isoformat():
            page = presenter
    wiki.getMainAreaPanel().showPresenter(page)
    return

def nextweek(wiki, evt):
    
    today = datetime.date.today() + datetime.timedelta(weeks=1)
    weeknumber = int(today.strftime("%W")) #((today - datetime.date(today.year,1,1)).days / 7) + 1
    d = datetime.date(today.year,1,1)

    if(d.weekday()>3):
        d = d+datetime.timedelta(7-d.weekday())
    else:
        d = d - datetime.timedelta(d.weekday())
    dlt = datetime.timedelta(days = (weeknumber-1)*7)
    weekdates = [(d+dlt+datetime.timedelta(days=R)).isoformat() for R in range(7)]
    openpages =  wiki.getMainAreaPanel().getDocPagePresenters()

    for page in openpages:
        if re.match("^\d{4}-\d{2}-\d{2}$",page.getWikiWord()):
            wiki.getMainAreaPanel().closePresenterTab(page) # RemovePage ?
            
    wiki.openWikiPage(str(weekdates[0]))
    for day in weekdates[1:]:
        presenter = wiki.createNewDocPagePresenterTab()
        presenter.openWikiPage(str(day))
        if day==today.isoformat():
            page = presenter
    wiki.getMainAreaPanel().showPresenter(page)
    return

def nextmonth(wiki, evt):
    here = wiki.getCurrentWikiWord()
    try:
        now = datetime.date(*time.strptime(here, "%Y-%m-%d")[0:3])
    except ValueError:
        now = datetime.date.today()
    wiki.openWikiPage(now.replace(month=now.month+1).isoformat())
    return

def nextyear(wiki, evt):
    here = wiki.getCurrentWikiWord()
    try:
        now = datetime.date(*time.strptime(here, "%Y-%m-%d")[0:3])
    except ValueError:
        now = datetime.date.today()
    wiki.openWikiPage(now.replace(year=now.year+1).isoformat())
    return



def nextrightclick(wiki, evt):
    openpages  = wiki.getMainAreaPanel().getDocPagePresenters()
    here = wiki.getCurrentWikiWord()
    today = datetime.date.today().isoformat()
    searchfrag = wiki.getActiveEditor().GetSelectedText()
    lpOp2 = Sar.ListWikiPagesOperation()
    lpOp2.ordering = "ascending"
    item2 = Sar.RegexWikiPageNode(lpOp2, "^\d{4}-\d{2}-\d{2}$")
    lpOp2.setSearchOpTree(item2)
    searchOp = Sar.SearchReplaceOperation()
    searchOp.wildCard = "no"
    searchOp.wikiWide = True
    searchOp.listWikiPagesOp = lpOp2
    if searchfrag!='':
        selection_start, selection_end = wiki.getActiveEditor().GetSelectionCharPos()
        searchOp.searchStr = searchfrag
        datelist = wiki.getWikiDocument().searchWiki(searchOp)
    else:
        datelist = wiki.getWikiDocument().searchWiki(searchOp)
    try:
        now = datetime.date(*time.strptime(here, "%Y-%m-%d")[0:3])
    except ValueError:
        now = today
    try:
        next_ = datelist[datelist.index(str(now))+1]
    except IndexError:
        next_ = datelist[0]
    if searchfrag=='':
        page_already_open = False
        for page in openpages:
            if page.getWikiWord()==next_:
                page_already_open = True
                wiki.getMainAreaPanel().showPresenter(page)
        if not page_already_open:
            presenter = wiki.createNewDocPagePresenterTab()
            presenter.openWikiPage(next_)
            wiki.getMainAreaPanel().showPresenter(presenter)
    else:
        next_ = str(now)
        newpos = wiki.getActiveEditor().GetText().lower().find(searchfrag.lower(), selection_end,)
        if newpos==-1: #no more searchfrags in page
            try:
                next_ = datelist[datelist.index(str(next_))+1]
            except IndexError:
                next_ = datelist[0]
            page_already_open = False
            for page in openpages:
                if page.getWikiWord()==next_:
                    page_already_open = True
                    wiki.getMainAreaPanel().showPresenter(page)
                    break
            if not page_already_open:
                presenter = wiki.createNewDocPagePresenterTab()
                presenter.openWikiPage(next_)
                wiki.getMainAreaPanel().showPresenter(presenter)
            newpos = wiki.getActiveEditor().GetText().lower().find(searchfrag.lower())
        wiki.getActiveEditor().SetSelectionByCharPos(newpos,newpos+len(searchfrag))
        wiki.getActiveEditor().unfoldAll()
    return

def next_(wiki, evt):
    here = wiki.getCurrentWikiWord()
    today = datetime.date.today().isoformat()

    searchfrag = wiki.getActiveEditor().GetSelectedText()

    lpOp2 = Sar.ListWikiPagesOperation()
    lpOp2.ordering = "ascending"
    item2 = Sar.RegexWikiPageNode(lpOp2, "^\d{4}-\d{2}-\d{2}$")
    lpOp2.setSearchOpTree(item2)

    searchOp = Sar.SearchReplaceOperation()
    searchOp.wildCard = "no"
    searchOp.wikiWide = True
    searchOp.listWikiPagesOp = lpOp2

    if searchfrag!='':
        selection_start, selection_end = wiki.getActiveEditor().GetSelectionCharPos()
        searchOp.searchStr = searchfrag
        datelist = wiki.getWikiDocument().searchWiki(searchOp)
    else:
        datelist = wiki.getWikiDocument().searchWiki(searchOp)

    try:
        now = datetime.date(*time.strptime(here, "%Y-%m-%d")[0:3])
    except ValueError:
        now = today

    try:
        next_ = datelist[datelist.index(str(now))+1]
    except IndexError:
        next_ = datelist[0]
    if searchfrag=='':
        wiki.openWikiPage(next_)
    else:
        next_ = str(now)
        newpos = wiki.getActiveEditor().GetText().lower().find(searchfrag.lower(), selection_end,)
        if newpos==-1:
            try:
                next_ = datelist[datelist.index(str(next_))+1]
            except IndexError:
                next_ = datelist[0]
            wiki.openWikiPage(next_)
            newpos = wiki.getActiveEditor().GetText().lower().find(searchfrag.lower())
        wiki.getActiveEditor().SetSelectionByCharPos(newpos,newpos+len(searchfrag))
        wiki.getActiveEditor().unfoldAll()
    return


def lastyear(wiki, evt):
    here = wiki.getCurrentWikiWord()
    try:
        now = datetime.date(*time.strptime(here, "%Y-%m-%d")[0:3])
    except ValueError:
        now = datetime.date.today()
    wiki.openWikiPage(now.replace(year=now.year-1).isoformat())
    return

def yesterday(wiki, evt):
    here = wiki.getCurrentWikiWord()
    try:
        yesterday = datetime.date(*time.strptime(here, "%Y-%m-%d")[0:3]) - datetime.timedelta(days=1)
    except ValueError:
        yesterday = datetime.date.today() - datetime.timedelta(days=1)
    yesterday = str(yesterday)
    openpages =  wiki.getMainAreaPanel().getDocPagePresenters()
    for page in openpages:
        if page.getWikiWord()==yesterday:
            wiki.getMainAreaPanel().showPresenter(page)
            return
    wiki.openWikiPage(yesterday)
    return

def tomorrow(wiki, evt):
    here = wiki.getCurrentWikiWord()
    try:
        tomorrow = datetime.date(*time.strptime(here, "%Y-%m-%d")[0:3]) + datetime.timedelta(days=1)
    except ValueError:
        tomorrow = datetime.date.today() + datetime.timedelta(days=1)
    tomorrow = str(tomorrow)
    openpages =  wiki.getMainAreaPanel().getDocPagePresenters()
    for page in openpages:
        if page.getWikiWord()==tomorrow:
            wiki.getMainAreaPanel().showPresenter(page)
            return
    wiki.openWikiPage(tomorrow)
    return

def tomorrowrightclick(wiki, evt):
    here = wiki.getCurrentWikiWord()
    today = datetime.date.today()
    try:
        now = datetime.date(*time.strptime(here, "%Y-%m-%d")[0:3])
    except ValueError:
        now = today
    tomorrow = str(now + datetime.timedelta(days=1))
    openpages =  wiki.getMainAreaPanel().getDocPagePresenters()
    for page in openpages:
        if page.getWikiWord()==tomorrow:
            wiki.getMainAreaPanel().showPresenter(page)
            return
    presenter = wiki.createNewDocPagePresenterTab()
    presenter.openWikiPage(tomorrow)
    wiki.getMainAreaPanel().showPresenter(presenter)
    return

def yesterdayrightclick(wiki, evt):
    here = wiki.getCurrentWikiWord()
    today = datetime.date.today()
    try:
        now = datetime.date(*time.strptime(here, "%Y-%m-%d")[0:3])
    except ValueError:
        now = today
    yesterday = str(now - datetime.timedelta(days=1))
    openpages =  wiki.getMainAreaPanel().getDocPagePresenters()
    for page in openpages:
        if page.getWikiWord()==yesterday:
            wiki.getMainAreaPanel().showPresenter(page)
            return
    presenter = wiki.createNewDocPagePresenterTab()
    presenter.openWikiPage(yesterday)
    wiki.getMainAreaPanel().showPresenter(presenter)
    return

def opencal(wiki, evt):
    webbrowser.open_new_tab('http://www.google.com/calendar/render')

def weekday_list(wiki, evt):
    if wiki.getCurrentWikiWord() is None:
        return        
    start, end = wiki.getActiveEditor().GetSelection()    
    potential_date = wiki.getActiveEditor().GetSelectedText().strip()
    if not potential_date:
        return
    try:
        date = datetime.date(*time.strptime(potential_date, "%Y-%m-%d")[0:3])
    except ValueError:
        return
    dates = u"\n".join(d.isoformat() for d in [date + datetime.timedelta(weeks=n) for n in range(52)])
    wiki.getActiveEditor().ReplaceSelection(dates)
    wiki.getActiveEditor().SetSelection(start+len(potential_date), end+len(dates)-len(potential_date))    


def copydatetoclipboard(wiki, evt):
    mstr = wiki.configuration.get("main", "strftime")
    date=strftimeUB(mstr)
    slask=copyTextToClipboard(date)
    return

def copylink(wiki, evt):
    here = wiki.getCurrentWikiWord()
    searchfrag = wiki.getActiveEditor().GetSelectedText()
    if searchfrag:
        here +="#"+searchfrag.replace(" ","# ")
    slask=copyTextToClipboard(here)
    return

def calctrl(wiki, evt):
    wikix, wikiy = wiki.GetPosition()
    wikiwidth, wikiheight = wiki.GetClientSize()
    frame_1 = CalendarDialog(wiki)
    calendarwidth, calendarheight = frame_1.GetBestSize()
    dx = wx.SystemSettings.GetMetric(wx.SYS_VSCROLL_X, win=wiki)
    x = wikix+wikiwidth - calendarwidth - dx - 1 - 8

    if sys.platform.startswith("linux"):
        dy = wiki.GetMenuBar().GetSize()[1]
    else:
        dy = 0

    dy+= wiki.GetToolBar().GetSize()[1]
    dy+= wx.SystemSettings.GetMetric(wx.SYS_CAPTION_Y,win=wiki)

    y = wikiy + dy

    #print y

    frame_1.SetPosition((x, y))
    frame_1.Show()

    #print wiki.GetNotebook() #GetSize()

    #print wx.SystemSettings_GetMetric(wx.SYS_MENU_Y ,win=wiki)
    #print wx.SystemSettings_GetMetric(wx.SYS_BORDER_X,win=wiki)
    #print wx.SystemSettings_GetMetric(wx.SYS_EDGE_X,win=wiki)
    #print wx.SystemSettings_GetMetric(wx.SYS_HSCROLL_ARROW_X,win=wiki)
    #print wx.SystemSettings_GetMetric(wx.SYS_FRAMESIZE_X,win=wiki)

class CalendarDialog(wx.Frame):
    def __init__(self, parent):
        self.wiki_ref = parent
        wx.Frame.__init__(self,
                          parent,
			  id=-1,
                          style=wx.FRAME_FLOAT_ON_PARENT |
                          wx.SYSTEM_MENU |
                          wx.CAPTION |
                          wx.CLOSE_BOX |
                          wx.CLIP_CHILDREN)

                          #wx.FRAME_NO_TASKBAR |

        self.calendar_ctrl_1=wx.adv.GenericCalendarCtrl(self,
                                                        -1,
                                                        style=wx.adv.CAL_MONDAY_FIRST|
                                                        wx.adv.CAL_SHOW_HOLIDAYS|
                                                        wx.adv.CAL_SHOW_SURROUNDING_WEEKS|
                                                        wx.adv.CAL_SEQUENTIAL_MONTH_SELECTION|
                                                        wx.adv.CAL_SHOW_WEEK_NUMBERS)

        # Tool Bar
        #self.frame_3_toolbar = wx.ToolBar(self, -1)
        #self.SetToolBar(self.frame_3_toolbar)
        #self.frame_3_toolbar.AddLabelTool(wx.NewId(), "itemm", wx.Bitmap("/home/bjorn/WikidPad/icons/add.gif", wx.BITMAP_TYPE_ANY), wx.NullBitmap, wx.ITEM_NORMAL, "", "")
        #self.frame_3_toolbar.AddLabelTool(wx.NewId(), "itemm", wx.Bitmap("/home/bjorn/WikidPad/icons/add.gif", wx.BITMAP_TYPE_ANY), wx.NullBitmap, wx.ITEM_NORMAL, "", "")
        #self.frame_3_toolbar.AddSimpleTool(10, wx.Bitmap("/home/bjorn/WikidPad/icons/add.gif", wx.BITMAP_TYPE_ANY), "New", "Long help for 'New'")
        #self.Bind(wx.EVT_TOOL, self.gnurgla2, id=10)
        # Tool Bar end

        self.Bind(wx.EVT_TOOL, self.gnurgla, id=-1)

        self.__set_properties()
        self.__do_layout()
        self.Bind(wx.adv.EVT_CALENDAR_WEEKDAY_CLICKED, self.OnWeekDayChosen,    self.calendar_ctrl_1)
        #self.Bind(wx.lib.calendar.EVT_CALENDAR_SEL_CHANGED,     self.OnSelectionChanged, self.calendar_ctrl_1)
        self.Bind(wx.adv.EVT_CALENDAR_YEAR,            self.OnYearChanged,      self.calendar_ctrl_1)
        self.Bind(wx.adv.EVT_CALENDAR_MONTH,           self.OnMonthChanged,     self.calendar_ctrl_1)
        self.Bind(wx.adv.EVT_CALENDAR_DAY,             self.OnDayChanged,       self.calendar_ctrl_1)
        self.Bind(wx.EVT_CLOSE, self.OnClose)
        #self.Bind(wx.EVT_ICONIZE, self.OnMinimize)
        #self.Bind(wx.wx.EVT_MAXIMIZE, self.OnMaximize)
        #self.calendar_ctrl_1.Bind(wx.EVT_KILL_FOCUS, self.OnClose)
        self.today = self.calendar_ctrl_1.GetDate()
        self.set_defined_dates()

    def gnurgla(self, event): # wxGlade: MyFrame.<event_handler>
        event.Skip()

    def gnurgla2(self, event): # wxGlade: MyFrame.<event_handler>
        event.Skip()

    def OnMinimize(self, event):
        self.Hide()

    def OnMaximize(self,event):
        self.Show()

    def OnClose(self,event):
        event.Skip()
        self.Destroy()

    def set_defined_dates(self):	
        entries =[]
        date = self.calendar_ctrl_1.GetDate()
        year =  date.GetYear()
        month = date.GetMonth() + 1
        for day in range(1, 32):
            if self.wiki_ref.getWikiDocument().isDefinedWikiLink("%02d-%02d-%02d" % (year, month, day)):
                entries.append(day)

        self.HighlightEvents(entries)

        #if self.today.GetYear()==year and self.today.GetMonth()+1 == month:
        #    pass
            #day = self.today.GetDay()
            #attrib = self.calendar_ctrl_1.GetAttr(day)
            #self.calendar_ctrl_1.ResetAttr(day)
            #attrib.SetTextColour(wx.BLUE) #attrib wx.lib.calendar.CalendarDateAttr(border=wx.lib.calendar.CAL_BORDER_SQUARE, colBorder="blue"))
            #self.calendar_ctrl_1.SetAttr(self.today.GetDay(),attrib)

    def HighlightEvents(self, days):
        date = self.calendar_ctrl_1.GetDate()
        year = date.GetYear()
        month = date.GetMonth() + 1
        #wx.BeginBusyCursor()
        try:
            for day in range(1, 32):
                if day in days:
                    self.SetDayAttr(day, True)
                    self.calendar_ctrl_1.Refresh(True)
                else:
                    self.SetDayAttr(day, False)
                    self.calendar_ctrl_1.Refresh(True)
            self.calendar_ctrl_1.Refresh(True)
        finally:
            pass
        #wx.EndBusyCursor()

    def SetDayAttr(self, day, has_event):
        if has_event:
            attr = wx.adv.CalendarDateAttr()
            attr.SetBorder(wx.adv.CAL_BORDER_SQUARE)
            attr.SetBorderColour(wx.BLUE)
            attr.SetBackgroundColour(wx.GREEN)
            self.calendar_ctrl_1.ResetAttr(day)
            self.calendar_ctrl_1.SetAttr(day, attr)
        else:
            self.calendar_ctrl_1.ResetAttr(day)

    def __set_properties(self):
        # begin wxGlade: MyFrame.__set_properties
        self.SetTitle("Open journal entry")
        # end wxGlade

    def __do_layout(self):
        # begin wxGlade: MyFrame.__do_layout
        sizer_1 = wx.BoxSizer(wx.VERTICAL)
        sizer_1.Add(self.calendar_ctrl_1, 0, wx.ALL, 5)
        self.SetSizer(sizer_1)
        sizer_1.Fit(self)
        self.Layout
        # end wxGlade

    def OnWeekDayChosen(self,event):
        wx.BeginBusyCursor()
        date = self.calendar_ctrl_1.GetDate()
        year = date.GetYear()
        month = date.GetMonth() + 1
        weekday = event.WeekDay-1
        if weekday ==-1:
            weekday=6
        calendar.setfirstweekday(calendar.MONDAY)
        cal=calendar.Calendar()
        days_in_this_month   = [d.isoformat() for d in cal.itermonthdates(year,month) if d.weekday()==weekday]
        all_days             = days_in_this_month[:]

        wiki=self.wiki_ref
        here = wiki.getCurrentWikiWord()
        openpages  = wiki.getMainAreaPanel().getDocPagePresenters()

        for page in openpages:
            if re.match("^\d{4}-\d{2}-\d{2}$",page.getWikiWord()):
                wiki.getMainAreaPanel().closePresenterTab(page)

        for presenter in openpages:
            ww=presenter.getWikiWord()
            if ww in days_in_this_month:
                all_days.remove(ww)
                wiki.getMainAreaPanel().closePresenterTab(presenter)

        if len(all_days)>0:
            wiki.openWikiPage(days_in_this_month[0])
            page=None
            for isodate in days_in_this_month[1:]:
                newpresenter = wiki.createNewDocPagePresenterTab()
                newpresenter.openWikiPage(isodate)
                wiki.getMainAreaPanel().showPresenter(newpresenter)
                if isodate == here:
                    page = newpresenter
            if page:
                wiki.getMainAreaPanel().showPresenter(page)
        else:
            pass
            wiki.openWikiPage(here)

        wx.EndBusyCursor()
        event.Skip()
        return

    def OnSelectionChanged(self, event):
        #date = self.calendar_ctrl_1.GetDate()
        #print "OnSelectionChanged", date.FormatISODate()
        event.Skip()

    def OnCalSelected(self, event):
        #print "on cal sel"
        event.Skip()

    def OnDayChanged(self,event):
        date = self.calendar_ctrl_1.GetDate().FormatISODate()
        wiki=self.wiki_ref
        openpages =  wiki.getMainAreaPanel().getDocPagePresenters()
        for page in openpages:
            if page.getWikiWord()==date:
                wiki.getMainAreaPanel().showPresenter(page)
                event.Skip()
                return
        wiki.openWikiPage(date)
        event.Skip()
        return

    def OnMonthChanged(self,event):
        # "month changed"
        self.set_defined_dates()
        event.Skip()

    def OnYearChanged(self,event):
        #print "year changed"
        self.set_defined_dates()
        event.Skip()
