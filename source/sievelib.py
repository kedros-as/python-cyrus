# -*- coding: utf-8 -*-
#
# Sievelib v0.4-20080619
# Copyright (c) 2007-2008 Reinaldo de Carvalho <reinaldoc@gmail.com>
# Copyright (c) 2004-2006 Hartmut Goebel <h.goebel@crazy-compilers.com>
# Copyright (c) 2001-2002 Ulrich Eck <ueck@net-labs.de>
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA.

"""Sieve management client.

A Protocol for Remotely Managing Sieve Scripts
Based on <draft-martin-managesieve-04.txt>

Changelog:
  * PLAIN authentication support - <reinaldoc@gmail.com>
  * Deactive script via setactive() - <reinaldoc@gmail.com>

"""

__version__ = "0.4"
__author__ = """Reinaldo de Carvalho <reinaldoc@gmail.com>
Hartmut Goebel <h.goebel@crazy-compilers.com>
Ulrich Eck <ueck@net-labs.de> April 2001
"""

import binascii, re, socket, time, random, sys

__all__ = [ 'MANAGESIEVE', 'SIEVE_PORT', 'OK', 'NO', 'BYE', 'Debug']

#from imaplib import _log, _mesg

Debug = 0
CRLF = '\r\n'
SIEVE_PORT = 2000

OK = 'OK'
NO = 'NO'
BYE = 'BYE'

# todo: return results or raise exceptions?
# todo: on result 'BYE' quit immediatly
# todo: raise exception on 'BYE'?

#    Commands
commands = {
    # name          valid states
    'AUTHENTICATE': ('NONAUTH',),
    'LOGOUT':       ('NONAUTH', 'AUTH', 'LOGOUT'),
    'CABABILTY':    ('NONAUTH', 'AUTH'),
    'GETSCRIPT':    ('AUTH', ),
    'PUTSCRIPT':    ('AUTH', ),
    'SETACTIVE':    ('AUTH', ),
    'DELETESCRIPT': ('AUTH', ),
    'LISTSCRIPTS':  ('AUTH', ),
    'HAVESPACE':    ('AUTH', ),
    }

### needed
Oknobye = re.compile(r'(?P<type>(OK|NO|BYE))'
                     r'( \((?P<code>.*)\))?'
                     r'( (?P<data>.*))?')
# draft-martin-managesieve-04.txt defines the size tag of literals to
# contain a '+' (plus sign) behind teh digits, but timsieved does not
# send one. Thus we are less strikt here:
Literal = re.compile(r'.*{(?P<size>\d+)\+?}$')
re_dquote  = re.compile(r'"(([^"\\]|\\.)*)"')
re_esc_quote = re.compile(r'\\([\\"])')


def sieve_name(name):
    # todo: correct quoting
    return '"%s"' % name

def sieve_string(string):
    return '{%d+}%s%s' % ( len(string), CRLF, string )


class MANAGESIEVE:
    """Sieve client class.

    Instantiate with: MANAGESIEVE(host [, port])

        host - host's name (default: localhost)
        port - port number (default: standard Sieve port).

    All Sieve commands are supported by methods of the same
    name (in lower-case).

    Each command returns a tuple: (type, [data, ...]) where 'type'
    is usually 'OK' or 'NO', and 'data' is either the text from the
    tagged response, or untagged results from command.

    All arguments to commands are converted to strings, except for
    AUTHENTICATE.
    """
    
    """
    However, the 'password' argument to the LOGIN command is always
    quoted. If you want to avoid having an argument string quoted (eg:
    the 'flags' argument to STORE) then enclose the string in
    parentheses (eg: "(\Deleted)").
    
    Errors raise the exception class <instance>.error("<reason>").
    IMAP4 server errors raise <instance>.abort("<reason>"),
    which is a sub-class of 'error'. Mailbox status changes
    from READ-WRITE to READ-ONLY raise the exception class
    <instance>.readonly("<reason>"), which is a sub-class of 'abort'.

    "error" exceptions imply a program error.
    "abort" exceptions imply the connection should be reset, and
            the command re-tried.
    "readonly" exceptions imply the command should be re-tried.

    Note: to use this module, you must read the RFCs pertaining
    to the IMAP4 protocol, as the semantics of the arguments to
    each IMAP4 command are left to the invoker, not to mention
    the results.
    """

    class error(Exception): """Logical errors - debug required"""
    class abort(error):     """Service errors - close and retry"""

    def __init__(self, host='', port=SIEVE_PORT):
        self.host = host
        self.port = port
        self.debug = Debug
        self.state = 'NONAUTH'

        self.response_text = self.response_code = None
        
        self.capabilities = []
        self.loginmechs = []
        self.implementation = ''
        self.supports_tsl = 0

        # Open socket to server.
        try:
            self._open(host, port)
            self.alive = True
        except:
            self.alive = False
            return

        # Get server welcome message,
        # request and store CAPABILITY response.
        if __debug__:
            if self.debug >= 1:
                self._mesg('managesieve version %s' % __version__)

        typ, data = self._get_response()
        if typ == 'OK':
            self._parse_capabilities(data)
        return


    def _mesg(self, s, secs=None):
        if secs is None:
            secs = time.time()
        tm = time.strftime('%M:%S', time.localtime(secs))
        sys.stderr.write('  %s.%02d %s\n' % (tm, (secs*100)%100, s))
        sys.stderr.flush()

    def _log(self, s, secs=None):
        pass

    def _parse_capabilities(self, lines):
        for cap in lines:
            if __debug__:
                if self.debug >= 3:
                    self._mesg('%s' % (cap))
            if cap[0] == "IMPLEMENTATION":
                self.implementation = cap[1]
            elif cap[0] == "SASL":
                self.loginmechs = cap[1].split()
            elif cap[0] == "SIEVE":
                self.capabilities = cap[1].split()
            elif cap[0] == "STARTTSL":
                self.supports_tsl = 1
            else:
                # A client implementation MUST ignore any other
                # capabilities given that it does not understand.
                pass
        return


    def __getattr__(self, attr):
        #    Allow UPPERCASE variants of MANAGESIEVE command methods.
        if attr in commands:
            return getattr(self, attr.lower())
        raise AttributeError("Unknown MANAGESIEVE command: '%s'" % attr)


    #### Private methods ###
    def _open(self, host, port):
        """Setup 'self.sock' and 'self.file'."""
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.connect((self.host, self.port))
        self.file = self.sock.makefile('r')

    def _close(self):
        self.file.close()
        self.sock.close()

    def _read(self, size):
        """Read 'size' bytes from remote."""
        return self.file.read(size)

    def _readline(self):
        """Read line from remote."""
        return self.file.readline()

    def _send(self, data):
        return self.sock.send(data)

    def _get_line(self):
        line = self._readline()
        if not line:
            raise self.abort('socket error: EOF')
        # Protocol mandates all lines terminated by CRLF
        line = line[:-2]
        if __debug__:
            if self.debug >= 4:
                self._mesg('< %s' % line)
            else:
                self._log('< %s' % line)
        return line

    def _simple_command(self, *args):
        """Execute a command which does only return status.

        Returns (typ) with
           typ  = response type

        The responce code and text may be found in <instance>.response_code
        and <instance>.response_text, respectivly.
        """
        return self._command(*args)[0] # only return typ, ignore data


    def _command(self, name, arg1=None, arg2=None, *options):
        """
        Returns (typ, data) with
           typ  = response type
           data = list of lists of strings read (only meaningfull if OK)

        The responce code and text may be found in <instance>.response_code
        and <instance>.response_text, respectivly.
        """
        if self.state not in commands[name]:
            raise self.error(
                'Command %s illegal in state %s' % (name, self.state))
        # concatinate command and arguments (if any)
        data = " ".join([_f for _f in (name, arg1, arg2) if _f])
        if __debug__:
            if self.debug >= 4: self._mesg('> %r' % data)
            else: self._log('> %s' % data)
        try:
            self._send('%s%s' % (data, CRLF))
            for o in options:
                if __debug__:
                    if self.debug >= 4: self._mesg('> %r' % o)
                    else: self._log('> %r' % data)
                self._send('%s%s' % (o, CRLF))
        except (socket.error, OSError) as val:
            raise self.abort('socket error: %s' % val)
        return self._get_response()


    def _readstring(self, data):
        if data[0] == ' ': # space -> error
            raise self.error('Unexpected space: %r' % data)
        elif data[0] == '"': # handle double quote:
            if not self._match(re_dquote, data):
                raise self.error('Unmatched quote: %r' % data)
            snippet = self.mo.group(1)
            return re_esc_quote.sub(r'\1', snippet), data[self.mo.end():]
        elif self._match(Literal, data):
            # read a 'literal' string
            size = int(self.mo.group('size'))
            if __debug__:
                if self.debug >= 4:
                    self._mesg('read literal size %s' % size)
            return self._read(size), self._get_line()
        else:
            for i in range(len(data)):
                if data[i] == ' ':
                    return data[:i], data[i+1:]
            else:
                return data, ''

    def _get_response(self):
        """
        Returns (typ, data) with
           typ  = response type
           data = list of lists of strings read (only meaningfull if OK)

        The responce code and text may be found in <instance>.response_code
        and <instance>.response_text, respectivly.
        """

        """
    response-deletescript = response-oknobye
    response-authenticate = *(string CRLF) (response-oknobye)
    response-capability   = *(string [SP string] CRLF) response-oknobye
    response-listscripts  = *(string [SP "ACTIVE"] CRLF) response-oknobye
    response-oknobye      = ("OK" / "NO" / "BYE") [SP "(" resp-code ")"] [SP string] CRLF
    string                = quoted / literal
    quoted                = <"> *QUOTED-CHAR <">
    literal               = "{" number  "+}" CRLF *OCTET
                            ;; The number represents the number of octets
                            ;; MUST be literal-utf8 except for values

--> a response either starts with a quote-charakter, a left-bracket or
    OK, NO, BYE

"quoted" CRLF
"quoted" SP "quoted" CRLF
{size} CRLF *OCTETS CRLF
{size} CRLF *OCTETS CRLF
[A-Z-]+ CRLF

        """
        data = [] ; dat = None
        resp = self._get_line()
        while 1:
            if self._match(Oknobye, resp):
                typ, code, dat = self.mo.group('type','code','data')
                if __debug__:
                    if self.debug >= 1:
                        self._mesg('%s response: %s %s' % (typ, code, dat))
                self.response_code = code
                self.response_text = None
                if dat:
                    self.response_text = self._readstring(dat)[0]
                return typ, data
##             elif 0:
##                 dat2 = None
##                 dat, resp = self._readstring(resp)
##                 if resp.startswith(' '):
##                     dat2, resp = self._readstring(resp[1:])
##                 data.append( (dat, dat2))
##                 resp = self._get_line()
            else:
                dat = []
                while 1:
                    dat1, resp = self._readstring(resp)
                    if __debug__:
                        if self.debug >= 4:
                            self._mesg('read: %r' % (dat1,))
                        if self.debug >= 5:
                            self._mesg('rest: %r' % (resp,))
                    dat.append(dat1)
                    if not resp.startswith(' '):
                        break
                    resp = resp[1:]
                data.append(dat)
                resp = self._get_line()
        return self.error('Should not come here')


    def _match(self, cre, s):
        # Run compiled regular expression match method on 's'.
        # Save result, return success.
        self.mo = cre.match(s)
        if __debug__:
            if self.mo is not None and self.debug >= 5:
                self._mesg("\tmatched r'%s' => %s" % (cre.pattern, repr(self.mo.groups())))
        return self.mo is not None


    ### Public methods ###
    def login(self, mechanism, user, password, admin=""):
        """Authenticate command - requires response processing."""
        # command-authenticate  = "AUTHENTICATE" SP auth-type [SP string]  *(CRLF string)
        # response-authenticate = *(string CRLF) (response-oknobye)
        mech = mechanism.upper()
        if not mech in self.loginmechs:
            raise self.error("Server doesn't allow %s authentication." % mech)

        if mechanism == 'PLAIN':
            if admin != '':
                encoded = binascii.b2a_base64("%s\0%s\0%s" % (user, admin, password)).strip()
            else:
                encoded = binascii.b2a_base64("%s\0%s\0%s" % (user, user, password)).strip()

            typ, data = self._command('AUTHENTICATE', sieve_name(mech)+" {"+str(len(encoded))+"+}", None, encoded)
        elif mechanism == 'LOGIN':
            encoded = binascii.b2a_base64("%s\0%s\0%s" % (user, user, password)).strip()
            typ, data = self._command('AUTHENTICATE', sieve_name(mech)+" {"+str(len(encoded))+"+}", encoded)
        else:
            raise self.error("Authentication %s dont implemented." % mech)

        if typ == 'OK':
            self.state = 'AUTH'
            return True
        else:
            return False


    def logout(self):
        """Terminate connection to server."""
        # command-logout        = "LOGOUT" CRLF
        # response-logout       = response-oknobye
        typ = self._simple_command('LOGOUT')
        self.state = 'LOGOUT'
        self._close()
        return typ


    def listscripts(self):
        """Get a list of scripts on the server.

        (typ, [data]) = <instance>.listscripts()

        if 'typ' is 'OK', 'data' is list of (scriptname, active) tuples.
        """
        # command-listscripts   = "LISTSCRIPTS" CRLF
        # response-listscripts  = *(sieve-name [SP "ACTIVE"] CRLF) response-oknobye
        typ, data = self._command('LISTSCRIPTS')
        if typ != 'OK': return typ, data
        scripts = []
        for dat in data:
            if __debug__:
                if not len(dat) in (1, 2):
                    return False, False
#                    self.error("Unexpected result from LISTSCRIPTS: %r" (dat,))
            scripts.append( (dat[0], len(dat) == 2) )
        return typ, scripts


    def getscript(self, scriptname):
        """Get a script from the server.

        (typ, scriptdata) = <instance>.getscript(scriptname)

        'scriptdata' is the script data.
        """
        # command-getscript     = "GETSCRIPT" SP sieve-name CRLF
        # response-getscript    = [string CRLF] response-oknobye
        
        typ, data = self._command('GETSCRIPT', sieve_name(scriptname))
        if typ != 'OK': return typ, data
        if len(data) != 1:
            self.error('GETSCRIPT returned more than one string/script')
        # todo: decode data?
        return typ, data[0][0]
    

    def putscript(self, scriptname, scriptdata):
        """Put a script onto the server."""
        # command-putscript     = "PUTSCRIPT" SP sieve-name SP string CRLF
        # response-putscript    = response-oknobye
        return self._simple_command('PUTSCRIPT',
                                    sieve_name(scriptname),
                                    sieve_string(scriptdata)
                                    )

    def deletescript(self, scriptname):
        """Delete a scripts at the server."""
        # command-deletescript  = "DELETESCRIPT" SP sieve-name CRLF
        # response-deletescript = response-oknobye
        return self._simple_command('DELETESCRIPT', sieve_name(scriptname))


    def setactive(self, scriptname=''):
        """Mark a script as the 'active' one."""
        # command-setactive     = "SETACTIVE" SP sieve-name CRLF
        # response-setactive    = response-oknobye
        return self._simple_command('SETACTIVE', sieve_name(scriptname))


    def havespace(self, scriptname, size):
        # command-havespace     = "HAVESPACE" SP sieve-name SP number CRLF
        # response-havespace    = response-oknobye
        return self._simple_command('HAVESPACE',
                                    sieve_name(scriptname),
                                    str(size))


    def capability(self):
        """
        Isse a CAPABILITY command and return the result.
        
        As a side-effect, on succes these attributes are (re)set:
                self.implementation
                self.loginmechs
                self.capabilities
                self.supports_tsl
        """
        # command-capability    = "CAPABILITY" CRLF
        # response-capability   = *(string [SP string] CRLF) response-oknobye
        typ, data = self._command('CAPABILITY')
        if typ == 'OK':
            self._parse_capabilities(data)
        return typ, data

### not yet implemented: ###

    # command-starttls      = "STARTTLS" CRLF
    # response-starttls     = response-oknobye
