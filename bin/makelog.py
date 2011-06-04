#!/usr/bin/env python3
"""
--documentation--
"""

__author__ = "Peter Kleiweg"
__version__ = "0.1"
__date__ = "2010/04/12"

#| imports

import cgitb; cgitb.enable(format="text")

import cgi, os, re, sys

import u.html, u.path, u.login, u.config

#| functions

def getval(field):
    return re.sub(r'\s+', ' ', form.getvalue(field, '')).strip()

#| main

u.html.loginCheck()

form = cgi.FieldStorage()
path = getval('p')

u.path.chdir(u.login.username + '-' + path)

try:
    method = open('../data/Method', 'rt').read().strip()
except:
    method = '???'

sys.stdout.write('''Content-type: text/plain

===================================================================

If you see this file, something went wrong that should not go wrong.

Near the end of this file you can see what went wrong.
Please look at http://www.gabmap.nl/?page_id=178 to see if this is
a known problem.

Otherwise, please send this file to {}

===================================================================

Server: {}

Task: {}/{}

Method: {}

'''.format(u.config.contact, u.config.appurl, u.login.username, path.replace('-', '/'), method))

sys.stdout.flush()
stdout = sys.stdout.detach()

queue = ['make.log']
while True:
    if not queue:
        break
    f = queue[0]
    queue = queue[1:]

    stdout.write(b'>>> ' + f.encode('ascii') + b'\n\n')
    fp = open(f, 'rb')
    for line in fp:
        l = re.sub(b'.*\r', b'', line).replace(b'\a', b'')
        stdout.write(l)
        m = re.search(b'(\\.\\./[a-zA-Z0-9]+)/OK', l)
        if m:
            queue.append(m.group(1).decode('ascii') + '/make.log')
    fp.close()
    stdout.write(b'\n\n')

stdout.write(b'done\n')
