#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
--documentation--
"""

__author__ = "Peter Kleiweg"
__version__ = "0.1"
__date__ = "2010/07/20"

import cgitb; cgitb.enable(format="html")

import cgi, re, sys

import u.html, u.config

def getval(field):
    return re.sub(r'\s+', ' ', form.getvalue(field, '')).strip()

form = cgi.FieldStorage()

s = getval('s')
assert re.match('^[a-zA-Z0-9]+$', s)

try:
    b, title = u.html.getBody(s + '.html', 'help/', True)
except:
    b = 'Missing help page'
    title = s

sys.stdout.write(u.html.head('help: ' + title))
sys.stdout.write('''
<div class="help">
<h2>Help</h2>
<h3>{}</h3>
'''.format(title))
sys.stdout.write(b)
sys.stdout.write('</div>\n')
sys.stdout.write(u.html.foot())
