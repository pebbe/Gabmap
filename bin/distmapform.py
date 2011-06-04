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

import u.html, u.path, u.myCgi, u.hebci
from u.login import username

#| globals



#| functions


#| main

u.html.loginCheck()

cp = u.hebci.cp(u.myCgi.data)

path = u.myCgi.data.get('p', b'').decode(cp)
if not path:
    sys.stdout.write('Location: home\n\n')
    sys.exit()

item    = u.myCgi.data.get('item',  b'').decode(cp)
variant = u.myCgi.data.get('var',   b'').decode(cp).replace('\n', '\t')
regex   = u.myCgi.data.get('regex', b'').decode(cp)

if regex:
    variant = ''
    try:
        re.compile(regex)
    except:
        u.html.exitMessage('Error', 'Invalid regular expression: ' + u.html.escape(str(sys.exc_info()[1])))

u.path.chdir(username + '-' + path + '-distmap')

fp = open('current.txt', 'wt', encoding='utf-8')
fp.write(item + '\n' + variant + '\n' + regex + '\n')
fp.close()

if not (variant or regex):
    if os.access('currentlist.txt', os.F_OK):
        os.remove('currentlist.txt')
    if os.access('currentvariants.txt', os.F_OK):
        os.remove('currentvariants.txt')

if os.access('distmap.eps', os.F_OK):
    os.remove('distmap.eps')

sys.stdout.write('Location: goto?p={}-distmap\n\n'.format(path))
