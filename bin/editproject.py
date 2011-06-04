#!/usr/bin/env python3
"""
--documentation--
"""

__author__ = "Peter Kleiweg"
__version__ = "0.1"
__date__ = "2010/05/02"

#| imports

import cgitb; cgitb.enable(format="html")

import re, sys

import u.config, u.html, u.path, u.myCgi, u.hebci
from u.login import username

#| main

u.html.loginCheck()

if username.startswith('demo'):
    u.html.exitMessage('Error', 'Changing description is not allowed for demo account')

cp = u.hebci.cp(u.myCgi.data)

path = u.myCgi.data.get('p', '').decode(cp)

if not path:
    sys.stdout.write('Location: home\n\n')
    sys.exit()

u.path.chdir('{}-project_{}'.format(username, int(path)))

text = re.sub(r'\s+', ' ', u.myCgi.data.get('description', '').decode(cp).strip())

if not text:
    u.html.exitMessage('Error', 'Missing description')

fp = open('description', 'wt', encoding='utf-8')
fp.write(u.html.escape(text) + '\n')
fp.close()

sys.stdout.write('Location: {}bin/goto?p=project_{}\n\n'.format(u.config.appurl, path))
