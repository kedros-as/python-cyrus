#!/usr/bin/python
# -*- coding: utf-8 -*-

#import sys
#reload(sys)

import cyruslib

def mark(cmd):
    print "####\n####### %s\n####" % cmd

ssl = False
try:
    imap = cyruslib.CYRUS("imap://127.0.0.1:143")
    imap.setEncoding('utf-8')

    imap.VERBOSE = True
    imap.login("cyrusadmin@example.com", "zzzzz")

    imap.VERBOSE = False
    try:
        imap.dm("user/écafé")
    except:
        pass

    try:
        imap.dm("user/écafé2")
    except:
        pass

    try:
        imap.dm("Notices")
    except:
        pass

    imap.VERBOSE = True

    mark("lm()")
    mbxList = imap.lm()
    for mbx in mbxList:
        print mbx

    mark("cm()")
    imap.cm("user%sécafé" % imap.SEP)
    imap.cm("user%sécafé%sSent" % (imap.SEP, imap.SEP))
    imap.cm("user%sécafé%sTrash" % (imap.SEP, imap.SEP))
    imap.cm("user%sécafé%sSpam" % (imap.SEP, imap.SEP))
    imap.cm("user%sécafé2" % imap.SEP)
    imap.cm("Notices")
    imap.cm("Notices%sUrgente" % imap.SEP)
    imap.cm("Notices%sImportante" % imap.SEP)

    mark("rename()")
    imap.rename("user/écafé/Sent", "user/écafé/Sent2")

    mark("sam()")
    imap.sam("user/écafé", "johndoe@example.com", "lrsw")
    imap.sam("user/écafé", "johndoe", "lrsw")

    mark("lam()")
    imap.lam("user/écafé")

    mark("sq()")
    imap.sq("user/écafé", "10240")

    mark("lq()")
    imap.lq("user/écafé")

    mark("setannotation()")

    imap.setannotation("", "/motd", "The server will be unavailable tomorrow.")
    imap.setannotation("", "/vendor/cmu/cyrus-imapd/shutdown", "The server is unavailble until 9am.")

    mark("getannotation()")
    imap.getannotation("", "*")
    imap.getannotation("", "/motd")
    imap.getannotation("", "/vendor/cmu/cyrus-imapd/shutdown")
    imap.setannotation("", "/motd", "")
    imap.setannotation("", "/vendor/cmu/cyrus-imapd/shutdown", "")

    mark("setannotation()")
    imap.setannotation("user/écafé/Trash", "/vendor/cmu/cyrus-imapd/expire", "60")
    imap.setannotation("user/écafé/Spam", "/vendor/cmu/cyrus-imapd/expire", "30")

    mark("getannotation()")
    imap.getannotation("user/écafé", "*")
    imap.getannotation("user/écafé", "/vendor/cmu/cyrus-imapd/expire")
    imap.getannotation("user/écafé", "/vendor/cmu/cyrus-imapd/partition")
    imap.getannotation("user/écafé/Trash", "/vendor/cmu/cyrus-imapd/expire")
    imap.getannotation("user/écafé/Spam", "/vendor/cmu/cyrus-imapd/expire")
    imap.setannotation("user/écafé/Trash", "/vendor/cmu/cyrus-imapd/expire", "")
    imap.setannotation("user/écafé/Spam", "/vendor/cmu/cyrus-imapd/expire", "")

    mark("reconstruct()")
    imap.reconstruct("user/écafé")

    mark("dm()")
    imap.dm("user/écafé")
    imap.dm("user/écafé2")
    imap.dm("Notices")

except cyruslib.CYRUSError, e:
    print "%s: %s" % (e[1], e[2])
