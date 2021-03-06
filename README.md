python-cyrus
============

python-cyrus (aka. cyruslib) is wrapped interface for imaplib.py, it adds support for cyrus specific commands.

Copyright (C) 2007-2009 Reinaldo de Carvalho <reinaldoc@gmail.com> 

Copyright (C) 2003-2006 Gianluigi Tiesi <sherpya@netfarm.it> 

Copyright (C) 2020 Kedros, a.s. www.kedros.sk 

Examples
--------

### Tips
- Using "rei" as sample user.
- Imap delimiter is availble as imap.SEP.
  e.g: "user%srei%sSent" % (imap.SEP, imap.SEP)
- Errors from imaplib or BAD commands raise CYRUSError,
  otherwise command is OK.
- CYRUSError: [int cod, str COMMAND, str description]

### Connection

    import cyruslib

    # without SSL
    imap = cyruslib.CYRUS("imap://127.0.0.1:143")

    # with SSL
    imap = cyruslib.CYRUS("imaps://127.0.0.1:993")

### Login:

    # Admin login (virtdomains: yes)
    imap.login("admin@example.com", "password")

    # Logon as user with admin password (virtdomains: yes)
    # SSL required!
    imap.login_plain("admin@example.com", "password", "user@example.com")

    # Admin login (virtdomains: no)
    imap.login("admin", "password")

    # Logon as user with admin password (virtdomains: no)
    # SSL required!
    imap.login_plain("admin", "password", "user")


### Exception handle:

    try:
        imap = cyruslib.CYRUS("imap://127.0.0.1:143")
        imap.login("admin@example.com", "password")
        # do anything here (cm, dm, lam, ...)
    except cyruslib.CYRUSError, e:
        print "%s: %s" % (e[1], e[2])

### List Mailbox:

    #  To list all mailboxes                       lm()
    #  To list users top mailboxes                 lm("user/%")
    #  To list all users mailboxes                 lm("user/*")
    #  To list users mailboxes startwith a word    lm("user/word*")
    #  To list global top folders                  lm("%")
    #  To list global startwith a word             unsupported by server
    #      suggestion (take care)                  lm("word*")

    mbxList = imap.lm()
    for mbx in mbxList:
        print mbx

### Codification:

    for mbx in imap.lm("user/rei/*"):
        print mbx
    > user/rei/caf&AOk-
    > user/rei/ma&AOc-a

    imap.setEncoding('utf-8')
    for mbx in imap.lm("user/rei/*"):
        print mbx
    > user/rei/café
    > user/rei/maça

### Create Mailbox:

    # unixhierarchysep: yes
    imap.cm("user/rei")

    # unixhierarchysep: no
    imap.cm("user.rei")

    # or delimiter independent
    imap.cm("user%srei" % imap.SEP)

    # also
    imap.cm("user%srei%sSent" % (imap.SEP, imap.SEP))

    # Global Mailbox (also availble to others commands)
    imap.cm("Notices")

### Delete Mailbox:

    # User Mailbox
    imap.dm("user/rei")

### Rename or Change Imap-Partition:

    imap.rename("user/rei/sent-mail", "user/rei/Sent")

    # Changing Imap-Partition (partition-label2 should be configured imapd.conf)
    imap.rename("user/rei", "user/rei", "label2")

### List ACLs:

    imap.lam("user/rei")

### Set ACL:

    # virtdomains: yes
    imap.sam("user/rei", "johndoe@example.com", "lrsw")

    # virtdomains: no
    imap.sam("user/rei", "johndoe", "lrsw")

### List Quota:

    imap.lq("user/rei")

### Set Quota:

    # Value in Kbytes
    imap.sq("user/rei", "10240")

### Get Annotation:
    # Server Annotation - ALL
    imap.getannotation("", "*")

    # especific
    imap.getannotation("", "/motd")
    imap.getannotation("", "/vendor/cmu/cyrus-imapd/shutdown")

    # Mailbox Annotation - ALL
    imap.getannotation("user/rei", "*")

    # especific
    imap.getannotation("user/rei", "/vendor/cmu/cyrus-imapd/expire")
    imap.getannotation("user/rei", "/vendor/cmu/cyrus-imapd/partition")


### Set Annotation:
    # Server Annotation
    imap.setannotation("", "/motd", "The server will be unavailable tomorrow.")
    imap.setannotation("", "/vendor/cmu/cyrus-imapd/shutdown", "The server is unavailble until 9am.")
    # Unset
    imap.setannotation("", "/motd", "")
    imap.setannotation("", "/vendor/cmu/cyrus-imapd/shutdown", "")

    # Mailbox Annotation
    imap.setannotation("user/rei/Trash", "/vendor/cmu/cyrus-imapd/expire", "60")
    imap.setannotation("user/rei/Spam", "/vendor/cmu/cyrus-imapd/expire", "30")
    # Unset
    imap.setannotation("user/rei/Trash", "/vendor/cmu/cyrus-imapd/expire", "")
    imap.setannotation("user/rei/Spam", "/vendor/cmu/cyrus-imapd/expire", "")

### Reconstruct:

    imap.reconstruct("user/rei")

### List Subscribed:

    imap = cyruslib.CYRUS("imaps://127.0.0.1:993")
    imap.login_plain("admin@example.com", "password", "rei@example.com")
    imap.lsub()

### Subscribe:

    imap = cyruslib.CYRUS("imap://127.0.0.1:143")
    imap.login("admin@example.com", "password")
    imap.cm("user%srei" % imap.SEP)
    imap.cm("user%srei%sTrash" % (imap.SEP, imap.SEP))
    imap.cm("user%srei%sSent" % (imap.SEP, imap.SEP))
    imap.cm("user%srei%sDrafts" % (imap.SEP, imap.SEP))
    imap.cm("user%srei%sSpam" % (imap.SEP, imap.SEP))
    del imap

    # ssl only
    imap = cyruslib.CYRUS("imaps://127.0.0.1:993")
    imap.login_plain("admin@example.com", "password", "rei@example.com")
    imap.subscribe("INBOX")
    imap.subscribe("INBOX%sTrash" % imap.SEP)
    imap.subscribe("INBOX%sSent" % imap.SEP)
    imap.subscribe("INBOX%sDrafts" % imap.SEP)
    imap.subscribe("INBOX%sSpam" % imap.SEP)
    del imap

### Unsubscribe:

    imap = cyruslib.CYRUS("imaps://127.0.0.1:993")
    imap.login_plain("admin@example.com", "password", "rei@example.com")
    imap.unsubscribe("INBOX%sSpam" % imap.SEP)

