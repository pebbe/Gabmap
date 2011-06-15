#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
--documentation--
"""

__author__ = "Peter Kleiweg"
__version__ = "0.1"
__date__ = "2010/03/27"

#| imports

import cgitb; cgitb.enable(format="text")

import cgi, os, re, stat, sys

import u.html, u.path
from u.login import username


#| globals

#| functions

def getval(field):
    return re.sub(r'\s+', ' ', form.getvalue(field, '')).strip()

def _getline(fp, required = False):
    while True:
        line = fp.readline()
        if not line:
            assert not required
            return ''
        line = line.strip()
        if line and line[0] != '#':
            return line

def _nan2NA(s):
    if s.lower() == 'nan':
        return 'NA'
    return s

def _NA2nan(s):
    if s.upper() == 'NA':
        return 'nan'
    return s

def num2chr(m):
    return '{:c}'.format(int(m.group(1)))

def iso2utf(s):
    if not s:
        return ''
    return re.sub('&#([0-9]+);', num2chr, s)


#| main functions

def difread(filename):
    """
    Reads a difference file, such as created by 'leven' program and others.
    Returns: tablesize, labels, table
    - filename: string
    - tablesize: integer
    - labels: list of strings
    - table: list of lists of floats (symmetric difference table)
    """

    fp = open(filename, 'rt', encoding='iso-8859-1')

    n = int(_getline(fp, True))

    lbls = []
    for i in range(n):
        lbls.append(iso2utf(_getline(fp, True)))

    dif = [[] for x in range(n)]
    for i in range(n):
        dif[i] = [0 for x in range(n)]
    for i in range(n):
        for j in range(i):
            dif[i][j] = dif[j][i] = float(_NA2nan(_getline(fp, True)))

    fp.close()

    return n, lbls, dif


#| main


u.html.loginCheck()

form = cgi.FieldStorage()

path = getval('p')

f = getval('f')

u.path.chdir(username + '-' + path + '-diff')

if f == 'L04':

    fp = sys.stdout.detach()
    fp.write('''Content-type: text/plain; charset=iso-8859-1
Cache-Control: no-cache
Pragma: no-cache

'''.encode('iso-8859-1'))
    data = open('diff.txt', 'rt', encoding='iso-8859-1').read()
    fp.write(data.encode('iso-8859-1'))

    sys.exit()


sys.stdout.write('''Content-type: text/plain; charset=utf-8
Cache-Control: no-cache
Pragma: no-cache

''')

n, lbls, dif = difread('diff.txt')

lbls = []
fp = open('../data/truelabels.txt', 'rt', encoding='utf-8')
for line in fp:
    lbls.append(line.strip())
fp.close()

sys.stdout.write('\t' + '\t'.join(lbls) + '\n')
for i in range(n):
    sys.stdout.write(lbls[i] + '\t' + '\t'.join(['{:g}'.format(x) for x in dif[i]]) + '\n')
