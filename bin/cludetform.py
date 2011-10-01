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
from p.cludetparms import *

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
    u.queue.enqueue(path + '/cludet', make.format({'appdir': u.config.appdir, 'python3': u.config.python3, 'n': n}))
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
    fp = open('version', 'wt')
    fp.write(mm + '\n')
    fp.close()

    makes = 'OK: ../diff/OK\n'
    makes += '\tdetpre.py\n'
    if mm == 'fast':
        params = '{} {}'.format(FastBeta, Limit)
        makes += '\tfor i in ../data/_/*.data; do determinants1 $$i {} > _/`basename $$i .data`.utxt; done\n'.format(params)
    else:
        params = '{} {} {}'.format(SlowBeta, Limit, Sep)
        makes += '\tfor i in ../data/_/*.data; do determinants2 $$i {} > _/`basename $$i .data`.utxt; done\n'.format(params)
    makes += '\t( for i in _/*.utxt; do echo `tail -n 1 $$i` $$i; done ) | cdsort > score.txt\n'
    makes += '\ttouch OK\n'
    u.queue.enqueue(path + '/cludet', makes)
    u.queue.run()
    time.sleep(2)
    fp = open('currentparms', 'wt')
    fp.write(params + '\n')
    fp.close()
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

    matches = {}
    matchesin = {}

    mtd = open('version', 'rt').read().strip()
    if mtd == 'fast':

        fp = open('currentparms', 'rt')
        params = fp.read().split()
        fp.close()
        beta = float(params[0])

        TP = 0
        FP = 0
        FN = 0
        TN = 0

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
                        matchesin[item] = 0
                    matches[item] += 1
                    if lbl in partition:
                        matchesin[item] += 1
                        TP += 1
                    else:
                        FP += 1
                else:
                    if lbl in partition:
                        FN += 1
                    else:
                        TN += 1
        fp.close()

        fp = open('reresults.txt', 'wt')

        if TP + FP == 0:
            fp.write('0.00 0.00 0.00\n')
        else:
            p = (TP + 1) / (TP + FP + 2)
            r = (TP + 1) / (TP + FN + 2)
            bp = (TP + FN + 2) / (TP + FN + FP + TN + 4)
            br = (TP + FP + 2) / (TP + FN + FP + TN + 4)
            ap = (p - bp) / (1 - bp)
            ar = (r - br) / (1 - br)
            if ap < 0 or ar < 0:
                af = 0
            else:
                af = (ap + beta * ar) / (1 + beta)
            fp.write('{:.2f} {:.2f} {:.2f}\n'.format(af, ap, ar))

        fp.close()

    else: # mtd == 'slow'
        import math, pickle

        fp = open('currentparms', 'rt')
        params = fp.read().split()
        fp.close()

        beta = float(params[0])
        Sep = float(params[2])

        fp = open('dst.pickle', 'rb')
        labels, idx, dst = pickle.load(fp)
        fp.close()

        nPlaces = len(labels)
        nPlacesIn = len(partition)

        RelSize = nPlacesIn / nPlaces

        Counts = []
        for i in range(nPlaces):
            Counts.append([0, 0])

        fp = open('../data/_/' + datafile + '.data', 'rb')
        encoding = 'iso-8859-1'
        for line in fp:
            if line.startswith(b'%utf8'):
                encoding = 'utf-8'
            elif line[:1] == b':':
                lbl = idx[line.decode('iso-8859-1')[1:].strip()]
            elif line[:1] == b'-':
                Counts[lbl][1] += 1
                item = line.decode(encoding)[1:].strip()
                if RE.search(item):
                    Counts[lbl][0] += 1
                    if not item in matches:
                        matches[item] = 0
                        matchesin[item] = 0
                    matches[item] += 1
                    if labels[lbl] in partition:
                        matchesin[item] += 1
        fp.close()

        missing = [False] * nPlaces
        for i in range(nPlaces):
            if Counts[i][1] == 0:
                missing[i] = True

        for i in range(nPlaces):
            if missing[i]:
                sum0 = 0
                sum1 = 0
                for j in range(nPlaces):
                    if not missing[j]:
                        d = math.pow(dst[i][j], Sep)
                        sum0 += Counts[j][0] / d
                        sum1 += Counts[j][1] / d
                Counts[i][0] = sum0
                Counts[i][1] = sum1

        TP = FP = FN = TN = 0.0
        for i in range(nPlaces):
            lbl = labels[i]
            if lbl in partition:
                tp = Counts[i][0] / Counts[i][1]
                TP += tp
                FN += 1 - tp
            else:
                fp = Counts[i][0] / Counts[i][1]
                FP += fp
                TN += 1 - fp

        p = TP / (TP + FP)
        r = TP / (TP + FN)
        bp = (TP + FN) / (TP + FN + FP + TN)
        br = (TP + FP) / (TP + FN + FP + TN)
        ap = (p - bp) / (1 - bp)
        ar = (r - br) / (1 - br)
        if ap < 0 or ar < 0:
            af = 0
        else:
            af = (ap + beta * ar) / (1 + beta)

        fp = open('reresults.txt', 'wt')
        fp.write('{:.2f} {:.2f} {:.2f}\n'.format(af, ap, ar))
        fp.close()


    fp = open('rematches.txt', 'wt', encoding='utf-8')
    for i in sorted(matches):
        fp.write('{}:{}\t{}\n'.format(matchesin[i], matches[i], i))
    fp.close()


#| main

u.html.loginCheck()

codepage = 'us-ascii'
path = getval('p')

if not path:
    sys.stdout.write('Location: home\n\n')
    sys.exit()

u.path.chdir(username + '-' + path + '-cludet')

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

sys.stdout.write('Location: goto?p={}-cludet{}\n\n'.format(path, target))
