#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
--documentation--
"""

__author__ = "Peter Kleiweg"
__version__ = "0.1"
__date__ = "2020/08/05"

#| imports

import cgitb; cgitb.enable(format="text")

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

u.path.chdir(username + '-' + path + '-data')

utf8 = os.access('UTF', os.F_OK)

if utf8:
    charset = 'utf-8'
else:
    charset = 'iso-8859-1'

sys.stdout.buffer.write(('''Content-type: text/plain; charset={}
Cache-Control: no-cache
Pragma: no-cache

# encoding: {}
'''.format(charset, charset)).encode('utf-8'))

fp1 = open('features-float.txt', 'rb')
fp1.readline()
n = int(fp1.readline()) + 1
sys.stdout.buffer.write(('{}\n'.format(n)).encode('utf-8'))

sys.stdout.buffer.write(b'INDEL\n')

fp2 = open('tokens-float.txt', 'rb')
t = []
for line in fp2:
    if line.startswith(b'TOKEN'):
        continue
    a = line.split()
    if len(a) == 0:
        sys.stdout.buffer.write(b' / '.join(t) + b'\n')
        t = []
    else:
        t.append(a[1])
fp2.close()

for line in fp1:
    sys.stdout.buffer.write(line)

fp1.close()
