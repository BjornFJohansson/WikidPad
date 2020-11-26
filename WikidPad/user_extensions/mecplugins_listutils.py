#!/usr/bin/env python
# -*- coding: utf-8 -*-
#WIKIDPAD_PLUGIN = (("MenuFunctions",1),)
WIKIDPAD_PLUGIN = (("MenuFunctions",1), ("ToolbarFunctions",1))

import re
import itertools

from pydna.utils import parse_text_table
from pydna.utils import join_list_to_table
from pydna.utils import expandtolist
from natsort import natsorted

def describeMenuItems(wiki):
    return (	(sortSelection,	    _(u"mecplugins|List utils|Sort selected lines")	   , _(u"sort selection")),
                (invertSelection,	_(u"mecplugins|List utils|Invert selected lines")  , _(u"invert selection")),
                (remove_duplicates, _(u"mecplugins|List utils|Remove duplicate lines") , _(u"remove_duplicates")),
                (ziplists,	        _(u"mecplugins|List utils|Zip lists")	           , _(u"ziplists")),
                (unziplists,	    _(u"mecplugins|List utils|Unzip lists")	           , _(u"unziplists")),
                (table,	            _(u"mecplugins|List utils|table<->list")           , _(u"table")),
                (expand_to_list,    _(u"mecplugins|List utils|expand bracket to list") , _(u"expand_to_list")), #mecplugins|List utils|
                (bullet_list,       _(u"mecplugins|List utils|bullet list")            , _(u"bullet list")), #mecplugins|List utils|

                )


def describeToolbarItems(wiki):
    return ((table,       _(u"table"),       _(u"table"),       "mec_table"),
            (bullet_list, _(u"bullet list"), _(u"bullet list"), "list"     ),
            )


def bullet_list(wiki, evt):
    if not wiki.getCurrentWikiWord():
        return
    start, end = wiki.getActiveEditor().GetSelectionCharPos()
    content = wiki.getActiveEditor().GetSelectedText()

    contentlist = content.strip().splitlines()

    wobullets = []
    newbullets = []
    newunordered = []

    all_bullets = all( re.match("\d+\..*",r) for r in contentlist )
    no_bullets  = not any( re.match("^\d+\..*|(\-|\*|\+)\s.*",r) for r in contentlist )
    all_unordered = all( re.match("(\-|\*|\+)\s.*",r) for r in contentlist )

    for i,r in enumerate(contentlist):
        row = re.split("^\d+\.",r)[-1]
        row = re.split("(\-|\*|\+)\s",row)[-1]
        print(row)
        wobullets.append(row.strip())
        newbullets.append(f"{i+1}. {row.strip()}")
        newunordered.append(f"- {row.strip()}")

    if no_bullets:
        contentstring = "\n".join(newbullets)
    elif all_unordered:
        contentstring = "\n".join(wobullets)
    elif all_bullets:
        contentstring = "\n".join(newunordered)

    wiki.getActiveEditor().ReplaceSelection(contentstring.strip())
    wiki.getActiveEditor().SetSelectionByCharPos(start, start+len(contentstring))
    return


def expand_to_list(wiki, evt):
    if not wiki.getCurrentWikiWord():
        return
    start, end = wiki.getActiveEditor().GetSelection()
    content = wiki.getActiveEditor().GetSelectedText()
    if not content:
        content = wiki.getActiveEditor().GetText().splitlines()[wiki.getActiveEditor().GetCurrentLine()]
    if not content:
        return
    start   = 1+len("\n".join(wiki.getActiveEditor().GetText().splitlines()[:wiki.getActiveEditor().GetCurrentLine()]))
    end     = 1+start+len(content)
    wiki.getActiveEditor().SetSelectionByCharPos(start, end)
    content = expandtolist(content)
    wiki.getActiveEditor().ReplaceSelection(content)
    wiki.getActiveEditor().SetSelectionByCharPos(start, start+len(content))
    return

def remove_duplicates(wiki, evt):
    start, end = wiki.getActiveEditor().GetSelection()
    if not wiki.getCurrentWikiWord():
        return
    content = wiki.getActiveEditor().GetSelectedText()
    if not content:
        return
    rows = content.split('\n')
    rows = list(set(rows))
    wiki.getActiveEditor().ReplaceSelection(str('\n'.join(rows)))
    wiki.getActiveEditor().SetSelection(start, end)


def sortSelection(wiki, evt):
    start, end = wiki.getActiveEditor().GetSelection()
    if wiki.getCurrentWikiWord() is None:
        return
    content = wiki.getActiveEditor().GetSelectedText()
    if not content:
        content = wiki.getActiveEditor().GetText()
    rows = natsorted( content.splitlines(),key=str.lower)

    wiki.getActiveEditor().ReplaceSelection( u'\n'.join(rows))
    wiki.getActiveEditor().SetSelection(start, end)

def invertSelection(wiki, evt):
    start, end = wiki.getActiveEditor().GetSelection()
    if wiki.getCurrentWikiWord() is None:
        return
    content = wiki.getActiveEditor().GetSelectedText()
    if not content:
        content = wiki.getActiveEditor().GetText()
    rows = content.split('\n')
    rows.reverse()
    wiki.getActiveEditor().ReplaceSelection(str('\n'.join(rows)))
    wiki.getActiveEditor().SetSelection(start, end)

def ziplists(wiki, evt):
    start, end = wiki.getActiveEditor().GetSelection()
    if wiki.getCurrentWikiWord() is None:
        return
    content = wiki.getActiveEditor().GetSelectedText()
    if not content:
        return

    rows = content.splitlines()

    even = rows[             :len(rows)//2]
    odd  = rows[ len(rows)//2:            ]

    merged = list(itertools.chain(*list(itertools.izip_longest(even,odd,fillvalue=""))))

    wiki.getActiveEditor().ReplaceSelection("\n".join(merged))
    wiki.getActiveEditor().SetSelectionByCharPos(start, end+2)

def unziplists(wiki, evt):
    start, end = wiki.getActiveEditor().GetSelection()
    if wiki.getCurrentWikiWord() is None:
        return
    content = wiki.getActiveEditor().GetSelectedText()
    if not content:
        return
    rows = content.splitlines()

    odd  = rows[::2]
    even = rows[1::2]

    wiki.getActiveEditor().ReplaceSelection(str("\n".join(odd) + "\n"*2 + str("\n".join(even))))
    wiki.getActiveEditor().SetSelectionByCharPos(start, end+2)

def table(wiki, evt):
    if wiki.getCurrentWikiWord() is None:
        return
    start, end = wiki.getActiveEditor().GetSelectionCharPos()
    content = wiki.getActiveEditor().GetSelectedText()

    if "\n|||\n" in content or "\n---\n" in content:
        f = join_list_to_table(content)
    else:
        f, cs,rs,rc,cr = parse_text_table(content)

    if content.strip() == f.strip():
        f = cs

    wiki.getActiveEditor().ReplaceSelection(f)
    wiki.getActiveEditor().SetSelectionByCharPos(start, start+len(f))

    return
