#!/usr/bin/env python3
"""
--documentation--
"""

__author__ = "Peter Kleiweg"
__version__ = "0.1"
__date__ = "2010/05/13"

#| imports

import cgitb; cgitb.enable(format="html")

import cgi, os, re, sys

import u.html, u.path
from u.login import username

#| globals



#| functions

def getval(field):
    return re.sub(r'\s+', ' ', form.getvalue(field, '')).strip()

#| main


u.html.loginCheck()

form = cgi.FieldStorage()

path = getval('p')

if not path:
    sys.stdout.write('Location: home\n\n')
    sys.exit()

u.path.chdir(username + '-' + path + '-nummap')

item = int(getval('item'))

fp = open('current.txt', 'rt')
i = int(fp.read())
fp.close()

if i != item:

    fp = open('current.txt', 'wt')
    fp.write('{}\n'.format(item))
    fp.close()

    if os.access('nummap.eps', os.F_OK):
        os.remove('nummap.eps')

sys.stdout.write('Location: goto?p={}-nummap\n\n'.format(path))
