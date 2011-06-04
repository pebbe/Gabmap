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

import u.html, u.path, u.queue
from u.login import username

#| globals



#| functions

def getval(field, default=''):
    return re.sub(r'\s+', ' ', form.getvalue(field, default)).strip()

#| main

u.html.loginCheck()

form = cgi.FieldStorage()

path = getval('p')
if not path:
    sys.stdout.write('Location: home\n\n')
    sys.exit()

u.path.chdir(username + '-' + path + '-prob')

if os.access('reset', os.F_OK):
    fp = open('reset')
    defnoise, deflimit, defexponent, defcolor, defmethod = fp.read().split()
    fp.close()
else:
    defnoise, deflimit, defexponent, defcolor, defmethod = ''

noise    = getval('noise', defnoise)
limit    = getval('limit', deflimit)
exponent = getval('exp'  , defexponent)
color    = getval('col'  , defcolor)
method   = getval('mthd' , defmethod)

try:
    fp = open('current.txt', 'rt')
    oldnoise, oldlimit, oldexp, oldcol, oldmethod = fp.read().split()
    fp.close()
except:
    oldnoise = oldlimit = oldexp = oldcol = oldmethod = ''


fp = open('current.txt', 'wt')
fp.write(noise + ' ' + limit + ' ' + exponent + ' ' + color + ' ' + method + '\n')
fp.close()

if noise != oldnoise or limit != oldlimit or exponent != oldexp or method != oldmethod:
    if os.access('prob.eps', os.F_OK):
        os.remove('prob.eps')
    if os.access('probbw.eps', os.F_OK):
        os.remove('probbw.eps')
    fp = open('{}/templates/Makefile-prob'.format(u.config.appdir), 'r')
    make = fp.read()
    fp.close()
    if method == 'ga' or method == 'wa':
        m = '-m {} -r 100'.format(method)
    else:
        m = '-m wa -m ga -r 50'
    u.queue.enqueue(path + '/prob', make.format({'noise': noise, 'limit': limit, 'exp': exponent, 'method': m}))
    u.queue.run()
    time.sleep(2)

sys.stdout.write('Location: goto?p={}-prob\n\n'.format(path))
