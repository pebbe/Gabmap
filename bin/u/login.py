#!/usr/bin/env python3
"""
--documentation--
"""

__author__ = "Peter Kleiweg"
__version__ = "0.1"
__date__ = "2010/01/29"

#| imports

import hashlib, os
from http import cookies
from datetime import datetime, timedelta
import u.config as _c

#| globals

username = ''

#| functions

def mkString(user, passwd, expires=''):
    if expires == '':
        expires = (datetime.utcnow() + timedelta(hours=12)).strftime('%Y%m%d%H')
    data = user + passwd + expires + _c.secret
    hashed = hashlib.sha224(data.encode('utf-8')).hexdigest()
    return expires + '-' + user + '-' + hashed


def _init():
    global username

    if _c.usermode == 'single':
        username = 'User'
        return

    cs = ''
    if 'HTTP_COOKIE' in os.environ:
        c = cookies.SimpleCookie()
        c.load(os.environ['HTTP_COOKIE'])
        if 'L04u' in c:
            cs = c['L04u'].value

    if not cs:
        return

    try:
        aa = cs.split('-')
        expires = aa[0]
        user = aa[1]
    except:
        return

    ex = datetime.utcnow().strftime('%Y%m%d%H')
    if ex > expires:
        return

    try:
        fp = open(_c.datadir + user + '/passwdh', 'rt', encoding='utf-8')
        passwd = fp.readline().strip()
        fp.close()
    except:
        return

    if cs == mkString(user, passwd, expires):
        username = user
        open(_c.datadir + user + '/TIMESTAMP', 'w').close()


#| main

_init()

#| if main
if __name__ == "__main__":
    pass
