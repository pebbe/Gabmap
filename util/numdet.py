#!/usr/bin/env python3
"""
    This is numdet.py
    Copyright (C) 2011 Peter Kleiweg

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <http://www.gnu.org/licenses/>.
"""

__author__ = "Peter Kleiweg"
__version__ = "0.1"
__date__ = "2011/06/22"


#| imports

import cgitb; cgitb.enable(format="text")

import os, sys

#| globals

target = int(sys.argv[1])

nBags = 40

#| functions

def _unquote(s):
    s = s.strip()
    if len(s) < 2:
        return s
    if s[0] != '"' or s[-1] != '"':
        return s
    return re.sub(r'\\(.)', r'\1', s[1:-1]).strip()

#| main


data = []
fp = open('../data/table.txt', 'rt', encoding='iso-8859-1')
nItems = len(fp.readline().split('\t'))
for line in fp:
    line = line.replace('\n', '').replace('\r', '')
    a = line.split('\t')[1:]
    for i in range(nItems):
        if a[i] == 'NA':
            a[i] = None
        else:
            a[i] = float(a[i])
    data.append(a)
fp.close()

partition = set()
labels = []
fp = open('clgroups.txt', 'rt', encoding='iso-8859-1')
for line in fp:
    a, b = line.split(None, 1)
    lbl = _unquote(b)
    labels.append(lbl)
    if int(a) == target:
        partition.add(lbl)
fp.close()
nLabels = len(labels)

inpart = [False] * nLabels
for i in range(nLabels):
    if labels[i] in partition:
        inpart[i] = True

fp = open('currentparms', 'rt')
Beta, Limit = [float(x) for x in fp.read().split()]
fp.close()
B2 = Beta * Beta

for item in range(nItems):
    column = [data[i][item] for i in range(nLabels)]
    vals = []
    for i in range(nLabels):
        if type(column[i]) == type(None):
            continue
        if inpart[i]:
            vals.append((column[i], True))
        else:
            vals.append((column[i], False))

    vals.sort()
    nVals = len(vals)
    bags = []
    TPFN = len([1 for x in vals if x[1]])
    for i in range(nBags):
        i1 = int( i      * nVals / nBags + .5)
        i2 = int((i + 1) * nVals / nBags + .5)
        if i1 < 0:
            i1 = 0
        if i2 > nVals:
            i2 = nVals
        f1 = vals[i1][0]
        f2 = vals[i2 - 1][0]
        TP = len([1 for x in vals[i1:i2] if x[1]])
        FP = len([1 for x in vals[i1:i2] if not x[1]])
        FN = TPFN - TP
        P = TP / (TP + FP)
        R = TP / (TP + FN)
        if P or R:
            F = (1 + B2) * P * R / (B2 * P + R)
        else:
            F = 0
        bags.append((F, TP, FP, i,
                     '{:.2f} {:.2f} {:.2f} {:g} {:g} {}:{}'.format(
                         F, P, R, f1, f2, TP, TP + FP)))


    bags.sort(reverse=True)

    lines = []

    F = 0
    P = 0
    R = 0
    TP = 0
    FP = 0
    for f, tp, fp, i, s in bags:
        TP2 = TP + tp
        FP2 = FP + fp
        FN2 = TPFN - TP2
        P2 = TP2 / (TP2 + FP2)
        R2 = TP2 / (TP2 + FN2)
        if P2 or R2:
            F2 = (1 + B2) * P2 * R2 / (B2 * P2 + R2)
        else:
            F2 = 0
        if F2 <= F * Limit:
            u = '- '
        else:
            u = '+ '
            F = F2
            P = P2
            R = R2
            TP = TP2
            FP = FP2
        lines.append((i, u + s))

    fp = open('_/{}'.format(item), 'wt')    
    for i, line in sorted(lines):
        fp.write(line + '\n')
    fp.write('\n{:.2f} {:.2f} {:.2f} {}:{}\n'.format(F, P, R, TP, TP + FP))
    fp.close()
