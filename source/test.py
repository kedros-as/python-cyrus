#!/usr/bin/python

import cyruslib, sys

#imap = cyruslib.CYRUS(sys.argv[1])
#sys.exit()

#try:
#    imap = cyruslib.CYRUS("127.0.0.1", 143, False)
#    imap.login("cyrusadmin@example.com", "xxxx")
#except cyruslib.CYRUSError, e:
#    print e[1]

#imap.dm("user/rei")
#imap.dm("user/rei/xxxx")
#imap.dm("user/rei/xxxxx/zzzzz")
#imap.dm("user/rei/xxxxx/zzzzz/yyyyy")
#imap.dm("user/eli")
#imap.dm("user/eli2")

#imap.dm("avisos/xxxxx/wwwww")
#imap.dm("avisos/xxxxx")
#imap.dm("noticias")


#print imap.lm("/*")
#for mbx in mbxList:
#    print mbx


imap = cyruslib.CYRUS("imap://192.168.0.2:143")
imap.login("cyrusadmin", "xxxx")
imap.setNormalize(True)
print imap.lm()
print imap.getannotation("user/thaiana.bitti@exemplo.com.br/Sent","/vendor/cmu/cyrus-imapd/expire")
#print imap.setannotation("user/thaiana.bitti@exemplo.com.br/Sent","/vendor/cmu/cyrus-imapd/expire", "60")

#imap.login("cyrusadmin@example.com", "xxxx")
#print imap.getannotation("user/alessandrama/II JORNADA LETRAS 2007","*")
#print imap.getannotation("user/alessandrama/Drafts","*")

#imap.setEncoding('utf-8')
#imap.setEncoding('iso-8859-1')
#for mbx in imap.lm("user/rei/*"):
#    print mbx


#imap.dm("user/rei9")
#x
#imap.cm("user%srei9" % imap.SEP)
#imap.cm("user%srei9%sTrash" % (imap.SEP, imap.SEP))
#imap.cm("user%srei9%sSent" % (imap.SEP, imap.SEP))
#imap.cm("user%srei9%sDrafts" % (imap.SEP, imap.SEP))
#imap.cm("user%srei9%sSpam" % (imap.SEP, imap.SEP))
#imap.subscribe("user%srei9%sSpam" % (imap.SEP, imap.SEP))
#del imap

# ssl only
#imap = cyruslib.CYRUS("127.0.0.1", 993, True)
#imap.login_plain("cyrusadmin@example.com", "xxxx", "rei9@example.com")
#imap.subscribe("INBOX")
#imap.subscribe("INBOX%sTrash" % imap.SEP)
#imap.subscribe("INBOX%sSent" % imap.SEP)
#imap.subscribe("INBOX%sDrafts" % imap.SEP)
#imap.subscribe("INBOX%sSpam" % imap.SEP)
#del imap

