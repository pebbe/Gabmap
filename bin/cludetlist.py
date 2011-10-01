#!/usr/bin/env python3
"""
--documentation--
"""

__author__ = "Peter Kleiweg"
__version__ = "0.1"
__date__ = "2010/05/13"

#| imports

import cgitb; cgitb.enable(format="text")

import cgi, re, sys

import u.html, u.path
from u.login import username

def num2chr(m):
    return '{:c}'.format(int(m.group(1)))

def getval(field):
    return re.sub(r'\s+', ' ', form.getvalue(field, '')).strip()

#| main

u.html.loginCheck()

form = cgi.FieldStorage()

path = getval('p')

if not path:
    sys.stdout.write('Location: home\n\n')
    sys.exit()

u.path.chdir(username + '-' + path + '-cludet')

sys.stdout.write('''Content-type: text/plain; charset=utf-8
Cache-Control: no-cache
Pragma: no-cache

''')

fp = open('score.txt', 'rt')
for line in fp:
    a, b, c, d, e = line.split()
    sys.stdout.write('{} - {} - {}  |  {}  {}\n'.format(a, b, c, re.sub('_([0-9]+)_', num2chr, e[2:-5]), d))
fp.close()

