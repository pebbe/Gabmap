#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
--documentation--
"""

__author__ = "Peter Kleiweg"
__version__ = "0.1"
__date__ = "2010/10/08"

#| imports

import cgitb; cgitb.enable(format="text")

import cgi, os, re, shutil, sys

import u.html, u.path
from u.login import username

#| globals

#| functions


def getval(field):
    return re.sub(r'\s+', ' ', form.getvalue(field, '')).strip()


def latin1(s):
    if s:
        if s[0] == '#':
            s = '&#35;' + s[1:]
        return s.encode('iso-8859-1', 'xmlcharrefreplace').decode('iso-8859-1')
    else:
        return ''

def pse(m):
    return '\\{:03o}'.format(ord(m.group()))

def psescape(s):
    return re.sub('[\200-\377]', pse, s.replace('\\', '\\\\').replace('(', '\\(').replace(')', '\\)'))

#| main

u.html.loginCheck()

form = cgi.FieldStorage()

path = getval('p')

if not path:
    sys.stdout.write('Location: home\n\n')
    sys.exit()

u.path.chdir(username + '-' + path + '-mdsplots')

if not os.access('plot2d.eps.in', os.F_OK):
    shutil.copy('plot2d.eps', 'plot2d.eps.in')

places = []
fp = open('../data/truelabels.txt', 'rt', encoding='utf-8')
for line in fp:
    places.append(line.strip())
fp.close()
places.sort()

labels = set()
fp = open('current', 'wt', encoding='utf-8')
for i in form.getlist('s'):
    p = places[int(i)]
    labels.add(latin1(p))
    fp.write(p + '\n')
fp.close()


fp = open('plot2d.eps.in', 'rt')
lines = fp.readlines()[:-3]
fp.close()

if labels:
    bbox = [int(i) for i in lines[1].split()[1:]]
    bbox[2] += 80
    lines[1] = '%%BoundingBox: {0[0]} {0[1]} {0[2]} {0[3]}\n'.format(bbox)

fp = open('dif3.vec2', 'rt', encoding='iso-8859-1')
fp.readline()
state = 0
for line in fp:
    if state == 0:
        s = line.strip()
        state = 1
    elif state == 1:
        x = float(line)
        state = 2
    elif state == 2:
        y = float(line)
        state = 0
        if s in labels:
            lines.append('({}) {} {} s\n'.format(psescape(s), x, y))
fp.close()

fp = open('plot2d.eps', 'wt')
for line in lines:
    fp.write(line)
fp.write('\nend\nshowpage\n%%EOF\n')
fp.close()

try:
    os.remove('plot2d.png')
except:
    pass
os.system('eps2png > /dev/null 2>&1')

sys.stdout.write('Location: goto?p={}-mdsplots\n\n'.format(path))

