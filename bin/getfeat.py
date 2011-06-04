#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
--documentation--
"""

__author__ = "Peter Kleiweg"
__version__ = "0.1"
__date__ = "2010/03/27"

#| imports

import cgitb; cgitb.enable(format="text")

import cgi, os, re, stat, sys

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

f = getval('f')

u.path.chdir(username + '-' + path + '-data')

if os.access('UTF', os.F_OK):
    e = 'utf-8'
else:
    e = 'iso-8859-1'

fp = sys.stdout.detach()
fp.write('''Content-type: text/plain; charset={}
Cache-Control: no-cache
Pragma: no-cache

'''.format(e).encode(e))
data = open('features.def', 'rb').read()
fp.write(data)

