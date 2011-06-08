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

#| main

u.html.loginCheck()

p = int(os.environ['QUERY_STRING'])

u.path.chdir('{}-project_{}-data'.format(username, p))

sys.stdout.write('''Content-type: text/plain; charset=utf-8
Cache-Control: no-cache
Pragma: no-cache

''')

m = open('Method', 'rt').read()
if m.startswith('num'):
    data = open('datacount.txt', 'rt', encoding='utf-8').read()
else:
    data = open('../items/datacount.txt', 'rt', encoding='utf-8').read()
    sys.stdout.write('''# first column: number of items with data for place
# second column: total data for place
''')
sys.stdout.write(data)
