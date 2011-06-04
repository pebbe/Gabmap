#!/usr/bin/env python3
"""
--documentation--
"""

__author__ = "Peter Kleiweg"
__version__ = "0.1"
__date__ = "2010/06/23"

#| imports

import cgitb; cgitb.enable(format="html")

import cgi, os, re, shutil, sys

import u.html, u.path
from u.login import username

#| functions

def getval(field):
    return re.sub(r'\s+', ' ', form.getvalue(field, '')).strip()

#| main

u.html.loginCheck()
u.path.chdir(username)


if username.startswith('demo'):
    u.html.exitMessage('Error', 'Removing a project is not allowed for demo account')


form = cgi.FieldStorage()
p = getval('p')

try:
    project = 'project_{}'.format(int(p))
    assert os.path.isdir(project)
except:
    pass
else:
    shutil.rmtree(project)

sys.stdout.write('Location: home\n\n')
