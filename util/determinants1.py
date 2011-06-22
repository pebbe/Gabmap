#!/usr/bin/env python3
"""
--documentation--
"""

__author__ = "Peter Kleiweg"
__version__ = "0.1"
__date__ = "2010/07/14"

#| imports

import cgitb; cgitb.enable(format="text")

import os, re ,math, sys

import u.setChar as setChar

from p.cludetparms import FastBeta2 as B2
from p.cludetparms import Limit

#| globals

clufile = 'clgroups.txt'
target = int(sys.argv[1])
datafile = sys.argv[2]

minvar = 2

#| functions

def _esc(m):
    return '_{}_'.format(ord(m.group()))

def _escape(s):
    if not s:
        return '__'
    return re.sub(r'[^-+a-zA-Z0-9]', _esc, s)

def _unquote(s):
    s = s.strip()
    if len(s) < 2:
        return s
    if s[0] != '"' or s[-1] != '"':
        return s
    return re.sub(r'\\(.)', r'\1', s[1:-1]).strip()


#| main

partition = set()

fp = open(clufile, 'rt', encoding='iso-8859-1')
for line in fp:
    a, b = line.split(None, 1)
    if int(a) == target:
        partition.add(_unquote(b))
fp.close()

variants = {}
subst = {}
inn = 0

fp = open(datafile, 'rb')
encoding = 'iso-8859-1'
ignore = re.compile('[^ a-zA-Z0-9]+')
for line in fp:
    if line.startswith(b'%utf8'):
        encoding = 'utf-8'
        ign = setChar.Vowel.union(setChar.Consonant).union(setChar.Semivowel)
        first = ''
        if os.access('accentscurrent.txt', os.F_OK):
            fp1 = open('accentscurrent.txt', 'rt')
            for line in fp1:
                c = '{:c}'.format(int(line))
                if c == '-':
                    first = '-'
                elif c == '[' or c == ']' or c == '\\':
                    ign.add('\\' + c)
                else:
                    ign.add(c)
            fp1.close()
        ignore = re.compile('[^' + first + ''.join(ign) + ']+')
    elif line[:1] == b':':
        lbl = line.decode('iso-8859-1')[1:].strip()
    elif line[:1] == b'-':
        variant1 = line.decode(encoding)[1:].strip()
        variant = ignore.sub('', variant1).strip()
        if not variant in variants:
            variants[variant] = [0, 0]
            subst[variant] = set()
        subst[variant].add(_escape(variant1))
        if lbl in partition:
            variants[variant][0] += 1
        else:
            variants[variant][1] += 1
fp.close()

allinn = 0
vs = []
for variant in variants:
    i, o = variants[variant]
    allinn += i
    if i + o >= minvar:
        vs.append((i, o, variant))

items = []
for i, o, variant in vs:
    p = (i + 1) / (i + o + 2)
    r = (i + 1) / (allinn + 2)
    f1 = (1 + B2) * p * r / (B2 * p + r)
    items.append((f1, p, r, i, o, variant))
items.sort(reverse=True)

rejected = []

oldF1 = oldP = oldR = 0.0
oldI = oldO = 0
for f1, p, r, i, o, va in items:
    if i == 0:
        rejected.append('{}  {}:{}'.format(_escape(va), i, i + o))
        continue
    inn = oldI + i
    outn = oldO + o
    sp = (inn + 1) / (inn + outn + 2)
    sr = (inn + 1) / (allinn + 2)
    sf1 = (1 + B2) * sp * sr / (B2 * sp + sr)
    if sf1 < oldF1 * Limit:
        rejected.append('{}  {}:{}'.format(_escape(va), i, i + o))
    else:
        oldF1 = sf1
        oldP = sp
        oldR = sr
        oldI = inn
        oldO = outn
        sys.stdout.write('{:.1f} {:.1f} {:.1f} {} {}:{} [ {} ]\n'.format(
            f1, p, r, _escape(va), i, i + o, ' | '.join(sorted(subst[va]))))

rejected.sort()
for r in rejected:
    sys.stdout.write('[' + r + ']\n')

sys.stdout.write('\n{:.1f} {:.1f} {:.1f} {}:{}\n'.format(oldF1, oldP, oldR, oldI, oldI + oldO))