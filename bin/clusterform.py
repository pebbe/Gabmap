#!/usr/bin/env python3
"""
--documentation--
"""

__author__ = "Peter Kleiweg"
__version__ = "0.1"
__date__ = "2010/05/13"

#| imports

import cgitb; cgitb.enable(format="html")

import cgi, os, re, sys, time

import u.html, u.config, u.path, u.queue
from u.login import username

#| functions

def getval(field):
    return re.sub(r'\s+', ' ', form.getvalue(field, '')).strip()

#| main

u.html.loginCheck()

form = cgi.FieldStorage()

path = getval('p')

if not path:
    sys.stdout.write('Location: home\n\n')
    sys.exit()

u.path.chdir(username + '-' + path + '-clusters')

maxnum = min(13, int(open('../data/stats.txt', 'rt').read().split()[0])) - 1

method = getval('mthd')
col = getval('col')
groups = int(getval('n'))

assert method in 'cl ga wa wm'.split()
assert col in 'col bw'.split()
if groups < 2:
    groups = 2
if groups > maxnum:
    groups = maxnum

if method == 'wm':
    expval = '.33333'
else:
    expval = 1

if col == 'bw':
    groupalt = 1
else:
    groupalt = groups

found = True
for filename in 'map{0}{1}{2}.eps den{0}{1}{2}.eps den{0}{3}{2}alt.eps'.format(method, groups, col, groupalt).split():
    if not os.access(filename, os.F_OK):
        found = False
        break

if found:
    fp = open('current.txt', 'wt')
    fp.write('{} {} {}\n'.format(method, groups, col))
    fp.close()
else:
    fp = open('{}/templates/Makefile-clusters'.format(u.config.appdir), 'r')
    make = fp.read()
    fp.close()
    u.queue.enqueue(path + '/clusters', make.format({'method': method,
                                                     'groups': groups,
                                                     'exp': expval,
                                                     'col': col,
                                                     'appdir': u.config.appdir,
                                                     'python3': u.config.python3,
                                                     'python2': u.config.python2,
                                                     'python2path': u.config.python2path}))
    u.queue.run()
    time.sleep(2)

sys.stdout.write('Location: goto?p={}-clusters\n\n'.format(path))
