#!/usr/bin/env python
# -*- coding: utf-8 -*-
#WIKIDPAD_PLUGIN = (("MenuFunctions",1),("ToolbarFunctions",1))
WIKIDPAD_PLUGIN = (("MenuFunctions",1),)

#from . import mecplugins_ini
import codecs
import tempfile
import zipfile
import smtplib
import os
import wx
import subprocess
import sys

from string import Template

from email                      import encoders
from email.mime.multipart       import MIMEMultipart
from email.mime.base            import MIMEBase
from email.mime.text            import MIMEText

from WikidPad.lib.pwiki                      import SearchAndReplaceDialogs
from WikidPad.lib.pwiki                      import SearchAndReplace
from WikidPad.lib.pwiki                      import DocPages
from WikidPad.lib.pwiki.StringOps            import pathnameFromUrl, strftimeUB, mbcsEnc
from WikidPad.lib.pwiki.WikiExceptions       import WikiFileNotFoundException
from WikidPad.lib.pwiki.PersonalWikiFrame    import PersonalWikiFrame
from WikidPad.lib.pwiki                      import urllib_red as urllib

#from mecplugins_settings.archive import *

def describeMenuItems(wiki):
    return ((archive, _("mecplugins|Archive and stamp pages and linked files"), _("archive & stamp")),)

def describeToolbarItems(wiki):
    return ((archive, _("Archive and stamp pages and linked files"), _("archive & stamp"), "barcode"),)

def recursive_zip(zipf, directory):
    list = os.listdir(directory)
    for file in list:
        fullpath = os.path.join(directory, file)
        if os.path.isfile(fullpath):
            zipf.write(fullpath, fullpath)
        elif os.path.isdir(file):
            recursive_zip(zipf, os.path.join(directory, file))

def archive(wiki, evt):

    settings={}
    exec(wiki.getWikiDocument().getWikiPage("mecplugins_settings").getContent().encode(), globals(), settings)
    for k,v in settings.items():
        globals()[k]=v
    
    timestamp           = strftimeUB("%Y-%m-%d_%H_%M_%S")
    archivedir          = os.path.join(wiki.dataDir,"archive")
    zipfilename         = timestamp +'_wikidPad_file_archive.zip'
    zipfilepath         = os.path.join(archivedir,zipfilename)
    signaturefilename   = zipfilename+".asc"
    signaturefilepath   = os.path.join(archivedir,signaturefilename)

    dlg =  SearchAndReplaceDialogs.SearchWikiDialog(wiki, wiki.getCurrentDocPagePresenter().getMainControl(), -1, )

    if dlg.ShowModal() == wx.ID_CANCEL:
        return

    if dlg.ShowModal() == wx.ID_OK:
        lpOp2 = dlg.getValue().listWikiPagesOp
        sarOp = SearchAndReplace.SearchReplaceOperation()
        sarOp.listWikiPagesOp = lpOp2
        pagelist = wiki.getWikiDocument().searchWiki(sarOp)
    dlg.Destroy()

    number_of_pages = len(pagelist)

    response = wiki.stdDialog("oc", "Secure Stamping $ Archiving", Template("Sign and stamp file archive with $number_of_pages pages using your \n\npersonal PGP key (keyid $keyid)?\n\n").substitute(vars()))
    if response=="cancel":
        return

    paths=[]

    if number_of_pages<1:
        return

    zipfilepath = os.path.join(archivedir,zipfilename)
    zip = zipfile.ZipFile(zipfilepath, 'w' ,zipfile.ZIP_DEFLATED)

    for wpage in pagelist:
        page = wiki.getWikiDocument().getWikiPage(wpage)
        pagepath = urllib.parse.quote(wpage,"")+".wiki"
        pagetext = page.getContent()
        #print pagepath
        zip.writestr(pagepath, pagetext.encode("utf8")) #"Latin-1"

        urlNodes = page.parseTextInContext(pagetext).iterDeepByName("urlLink")
        for node in urlNodes:
            if node.url.startswith("rel") or node.url.startswith("file"):
                paths.append(pathnameFromUrl(wiki.makeRelUrlAbsolute(node.url)))

    paths = list(set(paths))  #remove duplicate paths

    if paths:
        if not os.path.isdir(archivedir):
            try:
                os.mkdir(archivedir)
            except OSError:
                if os.path.exists(dirname):
                    # We are nearly safe
                    pass
                else:
                    wiki.stdDialog("o", "Secure Stamping $ Archiving", Template("ERROR, the archive directory\n\n $archivedir \n\ncould not be created.\n\nThe operation was canceled").substitute(vars()))
                    return

    for path in paths:
        if os.path.isfile(path):
            zip.write(path,path)
        elif os.path.isdir(path):
            recursive_zip(zip, path)
    zip.close()

    if os.path.isfile(zipfilepath):
        filesize = str(round(os.path.getsize(zipfilepath)/1000))
        wiki.stdDialog("o", "Secure Stamping $ Archiving", Template("The archive directory\n\n $zipfilepath \n\nwas sucessfully created!\n\n archive size is $filesize kb").substitute(vars()))
    else:
        wiki.stdDialog("o", "Secure Stamping $ Archiving", Template("ERROR, the archive directory\n\n $zipfilepath \n\nwas not created.\n\nThe operation was canceled").substitute(vars()))
        return

    cmd = Template("gpg --armor --detach-sign --batch --yes --no-tty --local-user $keyid --passphrase $passphrase  --output \"$signaturefilepath\" \"$zipfilepath\"").substitute(vars())
    # stderr=subprocess.STDOUT
    # http://www.doughellmann.com/PyMOTW/subprocess/
    try:
        retcode=subprocess.check_call(cmd, shell=True)
        if retcode < 0:
            print("GpG was terminated by signal", -retcode, file=sys.stderr)
            wiki.stdDialog("o", "Secure stamp", "GpG reported an error trying to sign the archive!")
            return
        else:
            print("GpG returned", retcode, file=sys.stderr)
            wiki.stdDialog("o",  "Secure Stamping $ Archiving", "Gnu Privacy Guard successfully signed the archive")
    except OSError as e:
        print("Execution failed:", e, file=sys.stderr)
        wiki.stdDialog("o", "Secure stamp", "GpG reported an error trying to sign the archive!")
        return

    if not os.path.isfile(signaturefilepath):
        wiki.stdDialog("o",  "Secure Stamping $ Archiving", Template("The signature file \n\n $signaturefilepath \n\n does not exist!\nStamping was canceled.").substitute(vars()))
        return

    signature = open(signaturefilepath, "r")
    content = Template(content).substitute(vars())
    content+= signature.read()
    signature.close()

    themsg = MIMEMultipart()
    themsg['From']         = sender
    themsg['To']           = to
    themsg['Subject']      = subject
    themsg.preamble = 'I am not using a MIME-aware mail reader.\n'
    themsg.attach(MIMEText(content))

    session = smtplib.SMTP(smtpserver,smtpport,smtphostname,smtptimeout)
    session.ehlo()
    session.starttls()
    session.ehlo()
    session.login(smtpuser, smtppass)
    recipientlist = to.split(",")
    smtpresult = session.sendmail(sender, recipientlist, themsg.as_string())
    session.quit()

    if smtpresult:
        errstr = ""
        for recip in list(smtpresult.keys()):
            errstr = 'Could not deliver mail to: %s \nServer said: %s \n\n %s \n\n %s' % (recip, smtpresult[recip][0], smtpresult[recip][1], errstr)
        wiki.stdDialog("o",  "Secure Stamping $ Archiving", "SMTP mail error\n\n"+errstr+"\n\n mail not sent for signing")
        return
    wiki.stdDialog("o",  "Secure Stamping $ Archiving", Template("Mail containing electronic signature sent to \n $to").substitute(to = "\n".join(recipientlist)))
    return
