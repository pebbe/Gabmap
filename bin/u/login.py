#!/usr/bin/env python
"""
--documentation--
"""

__author__ = "Peter Kleiweg"
__version__ = "0.1"
__date__ = "2010/01/29"

#| imports

import hashlib, os, sys
from http import cookies

import u.config as _c

#| globals

username = ''

#| functions

def mkString(user, passwd):
    # TO DO: Better to drop the REMOTE_IP and HTTP_X_FORWARDED_FOR altogether?
    addr = ''
    if _c.tryxforwardedfor == 'yes':
        addr = os.environ.get('HTTP_X_FORWARDED_FOR', '')
        if addr.startswith("'") and addr.endswith("'"):
            addr = addr[1:-1]
            addr = addr.split()[-1]
    if not addr:
        addr = os.environ.get('REMOTE_ADDR', '')
    data = passwd + addr + _c.secret
    hashed = hashlib.sha224(data.encode('utf-8')).hexdigest()
    return user + '-' + hashed


def _init():
    global username
    cs = ''
    if 'HTTP_COOKIE' in os.environ:
        c = cookies.SimpleCookie()
        c.load(os.environ['HTTP_COOKIE'])
        if 'L04u' in c:
            cs = c['L04u'].value

    if not cs:
        return

    try:
        user = cs.split('-')[0]
    except:
        return

    try:
        fp = open(_c.datadir + user + '/passwd', 'rt', encoding='utf-8')
        passwd = fp.readline().strip()
        fp.close()
    except:
        return

    if cs == mkString(user, passwd):
        username = user
        open(_c.datadir + user + '/TIMESTAMP', 'w').close()
        try:
            os.remove(_c.datadir + user + '/mailsent')
        except:
            pass


#| main

_init()

#| if main
if __name__ == "__main__":
    pass


