#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import wx
from wx import stc
from wx.py.editwindow import EditWindow
class TestEditor(EditWindow):
    def __init__(self, *args, **kwargs):
        EditWindow.__init__(self, *args, **kwargs)
        self.IndicatorSetStyle(0, stc.STC_INDIC_SQUIGGLE)
        self.IndicatorSetForeground(0, "red")
        self.IndicatorSetAlpha(0, 0x80)
        self.IndicatorSetUnder(0, True)
        self.IndicatorSetStyle(1, stc.STC_INDIC_DIAGONAL)
        self.IndicatorSetForeground(1, "blue")
        self.IndicatorSetStyle(2, stc.STC_INDIC_STRIKE)
        self.IndicatorSetForeground(2, "red")
if __name__ == "__main__":
    app = wx.App()
    frame = wx.Frame(None)
    ed = TestEditor(frame)
    ed.Text = "The quick brown fox jumped uber the lazy dog.\n"
    ed.SetIndicatorCurrent(0)
    ed.IndicatorFillRange(27, 4)
    ed.SetIndicatorCurrent(1)
    ed.IndicatorFillRange(32, 3)
    ed.SetIndicatorCurrent(2)
    ed.IndicatorFillRange(36, 4)
    frame.ed = ed
    frame.Show()
    app.MainLoop()
