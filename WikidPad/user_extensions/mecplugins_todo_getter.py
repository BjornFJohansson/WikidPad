#!/usr/bin/env python
# -*- coding: utf-8 -*-
WIKIDPAD_PLUGIN = (("hooks", 1),)

'''
todo-getter version 0.0.1
-------------------------

This is very much alpha software.
Only tested on wikidPad 2.3beta07 running with
Python version: 2.7.3 (default, Aug  1 2012, 05:14:39)
[GCC 4.6.3]
with Sqlite version: 3.7.9 and wxPython version: 2.9.4.1
on Linux-3.2.0-38-generic-x86_64-with-Ubuntu-12.04-precise

This plugin was inspired by Christian Ziemski's todo-extension

http://www.ziemski.net/wikidpad/index.html

The todo-getter is similar in the sense that it tries to sort todos
by date into different categories depending on how far in the future
they fall. Unlike the todo-extension, the todo-getter expects dated
todos to be placed on pages that are have names that are iso dates:
yyyy-mm-dd like 2007-03-22 for example, and the date (or deadline)
of the todo depends on the page where it is located.

todos on other pages are "undated".

Todos are created according to the following format:

todo.tag1.tag2.tag3: remeber to buy milk!
==== =============== ====================
type    categores     message

"type" is any of the todo types ("todo", "done", "action", "track",
"issue", "question" or "project")

todos are sorted and gathered on specific pages named according to
this principle:

[todo_type_tag1_tag2_tag3]

For example, the todo above would end up on the page:

[todo_todo_tag1_tag2_tag3]

While the todo item:

question.high: How do I get rich quick?

would end up on the page

[todo_question_high]

and the todo item

question.low: Pay my debt!

would end up on [todo_question_low]

Note that the page [todo_question] would only contain the
questions with no tags, while [todo_question_ALL] would
contain both high and low (plus all other tags).

The tag comparison is case insensitive and also not sensitive to
the order of the tags. This means that tags are similar to
gmail labels.

Thus the todo items:

todo.car.important: wash car!

todo.important.car: fix car!

would both end up on

[todo_todo_car_important] or

[todo_todo_important_car]


---

My usage:

Page                    content

[todo_todo]             all todos without tags
[todo_todo_home]        stuff todo around the house
[todo_done_ALL]         all dones without tags
[todo_track]            all tracks without tags

I use track for tracking things I ask of other people.
FP,GR,AC,FA,GT and DB are six different people. The things I
ask of them end up on the pages:

[todo_track_FP]
[todo_track_GR]
[todo_track_AC]
[todo_track_FA]
[todo_track_GT]
[todo_track_DB]

[todo_track_ALL]        All of them


The todo_track_FP will have the content below. Each todo will be
sorted depending on when it happens (= what the date of the page
where it is located might be). The todos of today gets selected for
visual feedback.

    ++Future


    ++Next week
    [2013-03-25] FP report on test of experiment A


    ++Tomorrow!


    ++Today!!
    [2013-03-23] FP prepare experiment A

    ++Past


    ++Undated

'''


import operator,re, datetime, textwrap
from collections import namedtuple
todo = namedtuple('todo', 'type categories page message')

def openedWikiWord(docPagePresenter, wikiWord):

    if (wikiWord[:5] != "todo_"): return

    categories = wikiWord[5:].lower().split("_")

    todo_type = categories.pop(0)

    todos = [todo(type = c.split(".")[0],
                  categories = c.split(".")[1:],
                  page = p,
                  message = m.strip())
             for (p, c, m)
             in docPagePresenter.getMainControl().wikiData.getTodos()]

    todos = [t for t in todos if t.type==todo_type]

    if categories == ['all']:
        todos = [t for t in todos if t.categories]
    elif categories:
        todos = [t for t in todos if set([c.lower() for c in t.categories])==set(categories)]
    else:
        todos = [t for t in todos if not t.categories]

    undated_todos = [t for t in todos if not re.match("[1-2][0-9]{3}-[0-1][0-9]-[0-3][0-9]", t.page)]
    undated_todos.sort(key=operator.attrgetter("page"))
    undated_todos_text = u"\n".join([u"[{}] {} {}".format(t.page, " ".join(t.categories), t.message) for t in undated_todos])

    dated_todos = sorted([t for t in todos if re.match("[1-2][0-9]{3}-[0-1][0-9]-[0-3][0-9]", t.page)], key=operator.attrgetter("page"), reverse=True)

    today = datetime.date.today()
    tomorrow = today + datetime.timedelta(days=1)
    weekdates = [(tomorrow+datetime.timedelta(days=R)).isoformat() for R in range(7)]
    today = today.isoformat()
    tomorrow = tomorrow.isoformat()

    future_todos     = [t for t in dated_todos if t.page>weekdates[-1]]
    next_weeks_todos = [t for t in dated_todos if t.page in weekdates]
    tomorrows_todos  = [t for t in dated_todos if t.page==tomorrow]
    todays_todos     = [t for t in dated_todos if t.page==today]
    past_todos       = [t for t in dated_todos if t.page<today]

    future_todos_text     = u"\n".join([u"[{}] {} {}".format(t.page, " ".join(t.categories), t.message) for t in future_todos])
    next_weeks_todos_text = u"\n".join([u"[{}] {} {}".format(t.page, " ".join(t.categories), t.message) for t in next_weeks_todos])
    tomorrow_todos_text   = u"\n".join([u"[{}] {} {}".format(t.page, " ".join(t.categories), t.message) for t in tomorrows_todos])
    today_todos_text      = u"\n".join([u"[{}] {} {}".format(t.page, " ".join(t.categories), t.message) for t in todays_todos])
    past_todos_text       = u"\n".join([u"[{}] {} {}".format(t.page, " ".join(t.categories), t.message) for t in past_todos])

    text = f'''\
### future
{future_todos_text}
### next week
{next_weeks_todos_text}
### tomorrow
{tomorrow_todos_text}
### today
{today_todos_text}
### past
{past_todos_text}
### undated
{undated_todos_text}'''

    text = textwrap.dedent(text.strip())
    oldtext = docPagePresenter.getActiveEditor().GetText().split("### future")[0]
    docPagePresenter.getActiveEditor().SetText(oldtext+text)  #SetTextUTF8
    docPagePresenter.saveCurrentDocPage()
    docPagePresenter.getActiveEditor().AppendText("\n")
    start = len(future_todos_text)+len(next_weeks_todos_text)+len(tomorrow_todos_text)+51
    stop  = start + len(today_todos_text)
    docPagePresenter.getActiveEditor().unfoldAll()
    docPagePresenter.getActiveEditor().foldAll()
    #print docPagePresenter.getActiveEditor().GetLineCount()
    #print docPagePresenter.getActiveEditor().getFoldingActive()
    docPagePresenter.getActiveEditor().SetSelectionByCharPos(start, stop)
    docPagePresenter.getActiveEditor().Refresh()

