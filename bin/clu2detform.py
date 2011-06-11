#!/usr/bin/env python3
"""
--documentation--
"""

__author__ = "Peter Kleiweg"
__version__ = "0.1"
__date__ = "2010/05/13"

#| imports

import cgitb; cgitb.enable(format="html")

import os, re, sys, time

import u.html, u.config, u.path, u.queue, u.myCgi, u.hebci
from u.login import username

#| globals

target = ''

#| functions

def _unquote(s):
    s = s.strip()
    if len(s) < 2:
        return s
    if s[0] != '"' or s[-1] != '"':
        return s
    return re.sub(r'\\(.)', r'\1', s[1:-1]).strip()

def _num2chr(m):
    return '{:c}'.format(int(m.group(1)))

def getval(field):
    return u.myCgi.data.get(field, b'').decode(codepage).strip()

def setNumber():
    n = int(getval('n'))
    assert n >= 2 and n <= 12
    fp = open('{}/templates/Makefile-cludet'.format(u.config.appdir), 'r')
    make = fp.read()
    fp.close()
    u.queue.enqueue(path + '/clu2det', make.format({'appdir': u.config.appdir, 'python3': u.config.python3, 'n': n}))
    for i in 'score.txt currentlist.txt currentselect.txt distmap.eps currentregex.txt'.split():
        if os.access(i, os.F_OK):
            os.remove(i)
    u.queue.run()
    time.sleep(2)

def setCluster():
    c = getval('c')
    if not c:
        return
    c = int(c)
    fp = open('current', 'rt')
    n = int(fp.read().split()[0])
    fp.close()
    assert c >= 1 and c <= n
    fp = open('current', 'wt')
    fp.write('{} {}\n'.format(n, c))
    fp.close()
    if os.access('accents.txt', os.F_OK):
        fpin = open('accents.txt', 'rt')
        fpout = open('accentscurrent.txt', 'wt')
        for line in fpin:
            if getval('chr{}'.format(line.strip())):
                fpout.write(line)
        fpout.close()
        fpin.close()        

    mm = getval('method')
    if mm == 'fast':
        m = 1
    else:
        m = 2
    fp = open('version', 'wt')
    fp.write(mm + '\n')
    fp.close()

    makes = 'OK: ../diff/OK\n'
    makes += '\tfor i in ../data/_/*.data; do determinants{} {} $$i > _/`basename $$i .data`.utxt; done\n'.format(m, c)
    makes += '\t( for i in _/*.utxt; do echo `tail -n 1 $$i` $$i; done ) | grep -v ^_ | cdsort > score.txt\n'.format(c)
    makes += '\ttouch OK\n'
    u.queue.enqueue(path + '/clu2det', makes)
    u.queue.run()
    time.sleep(2)
    for i in 'currentlist.txt currentselect.txt distmap.eps distmap.ex currentregex.txt'.split():
        if os.access(i, os.F_OK):
            os.remove(i)

def setItem():
    item = getval('item')
    fp = open('current', 'rt')
    n, c = fp.read().split()[:2]
    fp.close()
    fp = open('current', 'wt')
    fp.write('{} {} {}\n'.format(n, c, item))
    fp.close()
    for i in 'currentlist.txt currentselect.txt distmap.eps currentregex.txt'.split():
        if os.access(i, os.F_OK):
            os.remove(i)

def setRegex():
    global codepage
    codepage = u.hebci.cp(u.myCgi.data)
    regex = getval('regex')
    if not regex:
        u.html.exitMessage('Error', 'Missing regular expression')
    try:
        RE = re.compile(regex)
    except:
        u.html.exitMessage('Error', 'Invalid regular expression: ' + u.html.escape(str(sys.exc_info()[1])))
    fp = open('currentregex.txt', 'wt', encoding='utf-8')
    fp.write(regex + '\n')
    fp.close()
    for i in 'redistmap.eps redistmap.eps'.split():
        if os.access(i, os.F_OK):
            os.remove(i)

    fp = open('current', 'rt')
    target, datafile = fp.read().split()[1:]
    fp.close()

    partition = set()

    fp = open('clgroups.txt', 'rt', encoding='iso-8859-1')
    for line in fp:
        a, b = line.split(None, 1)
        if a == target:
            partition.add(_unquote(b))
    fp.close()

    imatch = 0
    omatch = 0
    iother = 0
    oother = 0

    matches = {}

    fp = open('../data/_/' + datafile + '.data', 'rb')
    encoding = 'iso-8859-1'
    for line in fp:
        if line.startswith(b'%utf8'):
            encoding = 'utf-8'
        elif line[:1] == b':':
            lbl = line.decode('iso-8859-1')[1:].strip()
        elif line[:1] == b'-':
            item = line.decode(encoding)[1:].strip()
            if RE.search(item):
                if not item in matches:
                    matches[item] = 0
                matches[item] += 1
                if lbl in partition:
                    imatch += 1
                else:
                    omatch += 1
            else:
                if lbl in partition:
                    iother += 1
                else:
                    oother += 1
    fp.close()

    fp = open('reresults.txt', 'wt')

    if imatch + omatch == 0:
        fp.write('0.000 0.000 0.000\n')
    else:
        p = (imatch + 1) / (imatch + omatch + 2)
        r = (imatch + 1) / (imatch + iother + 2)
        f1 = 2 * p * r / (p + r)
        fp.write('{:.3f} {:.3f} {:.3f}\n'.format(f1, p, r))

    fp.close()

    fp = open('rematches.txt', 'wt', encoding='utf-8')
    for i in sorted(matches):
        fp.write('{}\t{}\n'.format(matches[i], i))
    fp.close()
                


#| main

u.html.loginCheck()

codepage = 'us-ascii'
path = getval('p')

if not path:
    sys.stdout.write('Location: home\n\n')
    sys.exit()

u.path.chdir(username + '-' + path + '-clu2det')

a = getval('action')

if not os.access('QUEUED', os.F_OK):

    if a == 'number':
        setNumber()
        target = '#s1'
    elif a == 'cluster':
        setCluster()
        target = '#s2'
    elif a == 'item':
        setItem()
        target = '#s3'
    elif a == 'regex':
        setRegex()
        target = '#s4'

sys.stdout.write('Location: goto?p={}-clu2det{}\n\n'.format(path, target))
