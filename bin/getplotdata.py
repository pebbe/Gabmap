#!/usr/bin/env python
"""
--documentation--
"""

__author__ = "Peter Kleiweg"
__version__ = "0.1"
__date__ = "2011/09/04"

#| imports

import cgitb; cgitb.enable(format="text")

import os, sys

import u.html, u.path
from u.login import username


#| globals

#| functions

#| main

u.html.loginCheck()

p = int(os.environ['QUERY_STRING'])

u.path.chdir('{}-project_{}-plot'.format(username, p))

if not os.access('gabmap.Rdata', os.F_OK):
    try:
        os.remove('OK')
    except:
        pass
    os.system('make > make.log 2>&1')

fp = sys.stdout.detach()
fp.write(b'''Content-type: application/octet-stream
Content-disposition: attachment; filename=gabmap.Rdata
Cache-Control: no-cache
Pragma: no-cache

''')

d = open('gabmap.Rdata', 'rb').read()
fp.write(d)
