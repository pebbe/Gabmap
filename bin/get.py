#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
--documentation--
"""

__author__ = "Peter Kleiweg"
__version__ = "0.1"
__date__ = "2010/03/27"

#| imports

import cgitb; cgitb.enable(format="html")

import cgi, os, random, re, stat, sys, time

import u.html, u.path
from u.login import username


#| globals

#| functions

def running(pid):
    try:
        pid = int(pid)
    except:
        return False
    fp = os.popen('ps h -p {} -o s'.format(pid), 'r')
    s = fp.read().strip()
    fp.close()
    return len(s) == 1 and 'DRS'.find(s) > -1

def getlock():
    dest = '{}'.format(os.getpid())
    while True:
        try:
            os.symlink(dest, lockfile)
            s = os.readlink(lockfile)
            assert s == dest
        except:
            pass
        else:
            return

        try:
            s = os.readlink(lockfile)
            assert not running(s)
            os.remove(lockfile)
        except:
            pass
        else:
            continue

        time.sleep(.3 + .4 * random.random())

def unlock():
    os.remove(lockfile)


def needupdate(filename):
    if not os.access(filename, os.F_OK):
        return True
    if os.stat(filename)[stat.ST_MTIME] < os.stat(eps1name)[stat.ST_MTIME]:
        return True
    return False


def getval(field):
    return re.sub(r'\s+', ' ', form.getvalue(field, '')).strip()

def doFile(filename, mimetype, asAtt):
    if asAtt:
        attach = '\nContent-disposition: attachment; filename=' + filename
    else:
        attach = ''
    fp = open(filename, 'rb')
    data = fp.read()
    fp.close()
    sys.stdout.write('''Content-type: {}{}
Cache-Control: no-cache
Pragma: no-cache

'''.format(mimetype, attach))
    sys.stdout.flush()
    fp = sys.stdout.detach()
    fp.write(data)
    fp.close()


#| main


u.html.loginCheck()

form = cgi.FieldStorage()

path, filename = getval('p').rsplit('-', 1)

asAtt = getval('i')

asBW = getval('b')

u.path.chdir(username + '-' + path)

basename, ext = filename.split('.')
eps1name = epsname = basename + '.eps'

assert re.match(r'[a-zA-Z][a-zA-Z0-9_]*$', basename)
assert ext in 'eps pdf png'.split()
assert os.access(basename + '.eps', os.F_OK)

lockfile = basename + '.lock'

getlock()

if asBW:
    basename = basename + '-bw'
    epsname = basename + '.eps'
    filename = basename + '.' + ext
    if not os.access(epsname, os.F_OK) or os.stat(epsname)[stat.ST_MTIME] < os.stat(eps1name)[stat.ST_MTIME]:
        os.system('map2grey {} {}'.format(eps1name, epsname))

if ext == 'eps':
    doFile(filename, 'application/postscript', asAtt)
elif ext == 'pdf':
    if needupdate(filename):
        os.system('epstopdf ' + basename + '.eps')
    doFile(filename, 'application/pdf', asAtt)
elif ext == 'png':
    if needupdate(filename):
        os.system('ps2ppm -o -t -g -r 100 {}.eps > /dev/null 2> /dev/null'.format(basename))
        os.system('pnmtopng {}.01.ppmraw > {} 2> /dev/null'.format(basename, filename))
        os.remove(basename + '.01.ppmraw')
    doFile(filename, 'image/png', asAtt)

unlock()
