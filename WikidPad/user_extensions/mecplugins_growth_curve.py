#!/usr/bin/env python
# -*- coding: utf-8 -*-
WIKIDPAD_PLUGIN = (("MenuFunctions",1), ("ToolbarFunctions",1))

from datetime import timedelta
import numpy as np
from scipy.optimize import curve_fit
import matplotlib.pyplot as plt
import dateparser
import textwrap
from pydna.utils import parse_text_table

def describeMenuItems(wiki):
    return ( (growth,
              _(u"mecplugins|growth model")	   ,
              _(u"growth")),
            )

def describeToolbarItems(wiki):
    return ((growth, _(u"growth"), _(u"growth curve"), "mec_growth"),)

def growth(wiki, evt):
    if not wiki.getCurrentWikiWord():
        return
    start, end = wiki.getActiveEditor().GetSelection()
    content = wiki.getActiveEditor().GetSelectedText()
    
    if not content:
        content = textwrap.dedent("""\
        time     hour OD640
        10:00:00 0.00 0.100
        12:00:00 2.00 0.200
        14:00:00 4.00 0.400
        16:00:00 6.00
        """)
    else:
        f,cs,rs,rc,cr = parse_text_table(content)
        timelabel, timepoints = cr[0][0], cr[0][1:]
        hourlabel, hourpoints = cr[1][0], cr[1][1:]
        odlabel, odpoints     = cr[-1][0], cr[-1][1:]

        if (hourlabel, hourpoints) == (odlabel, odpoints):
            hourlabel, hourpoints = "hour", None
        
        timezero = dateparser.parse(timepoints[0])
        xy = [((dateparser.parse(x) - timezero).seconds/3600,float(y)) for x,y in zip(timepoints,odpoints) if x.strip() and y.strip()]

        def exp_growth(t, x0, µmax):
            # x0 initial optical density
            # t = time (h)
            # µmax maximum growth rate (1/h)
            return x0 * np.exp(µmax * t)
        
        
        def inv_exp_growth(X, x0, µmax):
            # x0 initial optical density
            # t = time (h)
            # µmax maximum growth rate (1/h)
            return np.log(X/x0)/µmax


        xdata = np.array([x for x,y in xy], dtype='f')
        ydata = np.array([y for x,y in xy], dtype='f')
        
        popt, pcov = curve_fit(exp_growth, 
                               xdata,
                               ydata,
                               bounds=([0.0, 0.0], [1.0, 1.0]))
        
        x0, µmax = popt
        # https://stackoverflow.com/questions/19189362/getting-the-r-squared-value-using-curve-fit
        residuals = ydata - exp_growth(xdata, *popt)
        ss_res = np.sum(residuals**2)
        ss_tot = np.sum((ydata-np.mean(ydata))**2)
        r2 = 1 - (ss_res / ss_tot)
        
        eqn = "{} = {:.3f} x exp({:.3f} x {}); R2={:.3f}".format(odlabel.strip(), x0, µmax, hourlabel.strip(), r2)
        
        tms = [timelabel]
        hrs = [hourlabel]
        ods = [odlabel] 
        
        for tm,od in zip(timepoints, odpoints):
            if tm.strip() and not od.strip():
                hr = "{:.2f}".format((dateparser.parse(tm)-timezero).seconds/3600)
                od = "{:.3f}".format(exp_growth(float(hr), x0, µmax))
            elif not tm.strip() and od.strip():    
                hr = "{:.2f}".format(inv_exp_growth(float(od), x0, µmax))
                tm = (timezero+timedelta(hours=float(hr))).strftime("%H:%M:%S")
            else:
                hr = "{:.2f}".format((dateparser.parse(tm)-timezero).seconds/3600)
            tms.append(tm)
            hrs.append(hr)
            ods.append(od)

        content = "\n".join(" ".join(cell) for cell in zip(tms,hrs,ods))
        content+="\n"+eqn

    start   = 1+len("\n".join(wiki.getActiveEditor().GetText().splitlines()[:wiki.getActiveEditor().GetCurrentLine()]))
    end     = 1+start+len(content)
    wiki.getActiveEditor().SetSelectionByCharPos(start, end)
    
    wiki.getActiveEditor().ReplaceSelection(content)
    wiki.getActiveEditor().SetSelectionByCharPos(start, start+len(content))
    return
