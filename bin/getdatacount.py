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

m = open('Method', 'rt').read()
if not m.startswith('num'):
    os.chdir('../items')

fp = sys.stdout.detach()
fp.write(b'''Content-type: text/plain; charset=iso-8859-1
Cache-Control: no-cache
Pragma: no-cache

''')
data = open('datacount.txt', 'rb').read()
fp.write(data)
