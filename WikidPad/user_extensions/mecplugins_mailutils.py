#!/usr/bin/env python
# -*- coding: utf-8 -*-
########################################
# |  \/  |     (_) | |  | | | (_) |
# | \  / | __ _ _| | |  | | |_ _| |___
# | |\/| |/ _` | | | |  | | __| | / __|
# | |  | | (_| | | | |__| | |_| | \__ \
# |_|  |_|\__,_|_|_|\____/ \__|_|_|___/
########################################
WIKIDPAD_PLUGIN = (("MenuFunctions",1),("ToolbarFunctions",1))
#WIKIDPAD_PLUGIN = (("MenuFunctions",1),)

import tempfile
import zipfile
import smtplib
import os
import string
#import cgi

from WikidPad.lib.pwiki.StringOps            import strftimeUB
from WikidPad.lib.pwiki.StringOps            import pathnameFromUrl

from email                      import encoders
from email.mime.multipart       import MIMEMultipart
from email.mime.base            import MIMEBase
from email.mime.text            import MIMEText

def describeMenuItems(wiki):
    return ((sendbymail, _(u"mecplugins|Send selected text by mail"), _(u"mail selection")),)

def describeToolbarItems(wiki):
    return ((sendbymail, _(u"mail selection"), _(u"mail selection"), "mail"),)

def recursive_zip(zipf, directory):
    list = os.listdir(directory)
    for file in list:
        fullpath = os.path.join(directory, file)
        if os.path.isfile(fullpath):
            zipf.write(fullpath, fullpath)
        elif os.path.isdir(file):
            recursive_zip(zipf, os.path.join(directory, file))

def sendbymail(wiki, evt):

    CurrentWikiWord=wiki.getCurrentWikiWord()
    if CurrentWikiWord is None:
        return
    cont = wiki.getActiveEditor().GetSelectedText()
    if not cont:
        return

    docPage = wiki.getCurrentDocPage()
    pageAst = docPage.parseTextInContext(cont)
    urlNodes = pageAst.iterDeepByName("urlLink")
    paths=[]
    recipients_in_text=[]
    themsg = MIMEMultipart()

    for node in urlNodes:
        if node.url.startswith("file:"):
            paths.append(pathnameFromUrl(node.url))
        if node.url.startswith("rel:"):
            paths.append(pathnameFromUrl(wiki.makeRelUrlAbsolute(node.url)))
        if node.url.startswith("mailto:"):
            recipients_in_text.append(node.url[7:])
            cont = "".join(cont.split(node.url))

    if paths:
        response = wiki.stdDialog("ync", "Mail selected text", "Compress linked files and send as attachment?")
    else:
        response = "not set"

    if response == "cancel":
        return

    if response == "yes":

        filelist = []
        path_not_found = []

        for path in paths:
            if os.path.isfile(path):
                filelist.append(path)
            elif os.path.isdir(path):
                for root, subFolders, files in os.walk(path):
                    for file in files:
                        filelist.append(os.path.join(root,file))
            else:
                path_not_found.append(path)

        filelist = list(set(filelist))

        if path_not_found:
            no_of_missing_paths = len(path_not_found)
            missing_paths = "\n".join(path_not_found[0:5])
            response = wiki.stdDialog("ync","Mail selected text", string.Template("$no_of_missing_paths files or directories are missing\n\n $missing_paths\n\nSend anyway?").substitute(vars()))
            if response != "yes":
                return

        if filelist:
            zipfilename = strftimeUB("%Y-%m-%d|%A %B %d|%H:%M:%S")+'.zip'
            zf = tempfile.TemporaryFile()
            zip = zipfile.ZipFile(zf, 'w',zipfile.ZIP_DEFLATED)

            if len(filelist)>1:
                commonprefix = os.path.commonprefix(filelist)
            else:
                commonprefix = os.path.split(filelist[0])[0]

            for path in filelist:
                zip.write(path,path.split(commonprefix)[-1])

            zip.close()

            zf.seek(0)
            attached_zip = zf.read()
            if attached_zip:
                msg = MIMEBase('application', 'zip')
                msg.set_payload(attached_zip)
                encoders.encode_base64(msg)
                msg.add_header('Content-Disposition', 'attachment', filename=zipfilename)
                themsg.attach(msg)

    now  = strftimeUB("%H:%M:%S")
    subj = cont.splitlines()[0] # The first line of the content is the subject

    settings={}
    exec(wiki.getWikiDocument().getWikiPage("mecplugins_settings").getContent().encode(), globals(), settings)
    for k,v in settings.items():
        globals()[k]=v

    recipients_from_contacts_page = []
    if wiki.wikiDocument.isDefinedWikiWord(contacts_page):
        recipients_from_contacts_page = wiki.getWikiDocument().getWikiPage(contacts_page).getContent().splitlines()
        recipients_from_contacts_page = [a for a in recipients_from_contacts_page if not a.isspace()]
        if not recipients_from_contacts_page:
            wiki.stdDialog("o", u"Mail selected text","Contacts page {0} in wiki is empty!".format(contacts_page))
    else:
        wiki.stdDialog("o", u"Mail selected text","No mail contacts page {0} in wiki".format(contacts_page))
    selected_recipients=[]
    if recipients_from_contacts_page:
        selected_recipients=wiki.stdDialog("listmcstr", "Mail selected text", "Choose one or more recipients:", recipients_from_contacts_page)
    recipients = recipients_in_text + selected_recipients
    if not recipients:
        wiki.stdDialog("o", "Mail selected text","No recipients selected")
        return
    #cont = cont.encode('utf8')
    themsg['From']         = sender
    themsg['To']           = ", ".join(recipients)
    themsg['Subject']      = subj
    themsg.preamble = 'I am not using a MIME-aware mail reader.\n'

    htmlcont= '<span style="font-family: Consolas, monaco, monospace"><pre>{}</pre></span>'.format(cont)

    themsg.attach(MIMEText(htmlcont,'html'))

    if extra_recipient and not extra_recipient.isspace():
        recipients.append(extra_recipient)
    assert type(recipients) == list
    session = smtplib.SMTP(smtpserver,smtpport,smtphostname,smtptimeout)
    session.ehlo()
    session.starttls()
    session.ehlo()
    session.login(smtpuser, smtppass)
    smtpresult = session.sendmail(sender, recipients, themsg.as_string())
    if smtpresult:
        report = "Mail(s) could not be sent!\n"
        for recip in smtpresult.keys():
            report = """Could not deliver mail to: %s

    Server said: %s
    %s

    %s""" % (recip, smtpresult[recip][0], smtpresult[recip][1], report)

        #raise smtplib.SMTPException, report
    else:
        report = u"mail sent {0} to:\n{1}".format(now, u"\n".join(recipients))
    session.quit()
    wiki.stdDialog("o", "Mail selected text", report)
    return