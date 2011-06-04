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

if getval('revcol'):
    revcol = '1'
else:
    revcol = '0'

place  = getval('pl')
method = getval('m')

u.path.chdir(username + '-' + path + '-refmaps')

try:
    fp = open('current', 'rt')
    oldplace = fp.read().split()[0]
    fp.close()
except:
    oldplace = '-1'

fp = open('current', 'wt')
fp.write(place + '\n' + method + '\n' + revcol + '\n')
fp.close()

if os.access('curmap.eps', os.F_OK):
    os.remove('curmap.eps')

if os.access('plot01.eps', os.F_OK) and place != oldplace:
    os.remove('plot01.eps')

if os.access('plot01i.png', os.F_OK) and place != oldplace:
    os.remove('plot01i.png')

sys.stdout.write('Location: goto?p={}-refmaps\n\n'.format(path))
