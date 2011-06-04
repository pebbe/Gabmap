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

#| globals



#| functions

def getval(field):
    return re.sub(r'\s+', ' ', form.getvalue(field, '')).strip()

def _num2chr(m):
    return '{:c}'.format(int(m.group(1)))

#| main

u.html.loginCheck()

form = cgi.FieldStorage()

path = getval('p')
if not path:
    sys.stdout.write('Location: home\n\n')
    sys.exit()

u.path.chdir(username + '-' + path + '-align')

filename = getval('n')
itemname = re.sub('_([0-9]+)_', _num2chr, filename)

assert re.match('[-+a-zA-Z0-9_]+$', filename)

if os.access('../data/_/' + filename + '.data', os.F_OK):

    for fn in os.listdir('.'):
        if fn.startswith('alignments') or fn == 'page' or fn == 'pages':
            os.remove(fn)

    if os.access('../data/features-float.txt', os.F_OK):
        subst = '-s ../data/features-float.txt'
        ext = '.ftr'
    else:
        subst = ''
        ext = ''

    fp1in = open('../data/_/{}.data{}'.format(filename, ext), 'rb')
    fp1out = open('current.data{}'.format(ext), 'wb')
    if ext:
        fp2in = open('../data/_/{}.data.ftr.tok'.format(filename), 'rb')
        fp2out = open('current.data.ftr.tok', 'wb')
    c = set()
    for line1 in fp1in:
        if ext:
            line2 = fp2in.readline()
        if line1[:1] == b':':
            c = set()
            fp1out.write(line1)
            if ext:
                fp2out.write(line2)
        elif line1[:1] == b'-' or line1[:1] == b'+':
            if not line1 in c:
                fp1out.write(line1)
                if ext:
                    fp2out.write(line2)
                c.add(line1)
        else:
            fp1out.write(line1)
            if ext:
                fp2out.write(line2)
    fp1in.close()
    fp1out.close()
    if ext:
        fp2in.close()
        fp2out.close()

    column = '-r'
    placeidx = int(getval('l'))
    if placeidx > 0:
        place = ''
        fp = open('../data/labels.txt', 'rt', encoding='iso-8859-1')
        for line in fp:
            line = line.strip()
            a, b = line.split(None, 1)
            if int(a) == placeidx:
                place = b
                break
        fp.close()
        if place:
            fp = open('alignlabel.txt', 'wt', encoding='iso-8859-1')
            fp.write(place + '\n')
            fp.close()
            column = '-L alignlabel.txt'.format(place)

    if column == '-r':
        placeidx = 0

    os.system('auleven-r {} -m 4 -n -t tokenlist.txt {} current.data{} > alignments.txt 2> alignerrors.txt'.format(
        column,
        subst,
        ext))

    if ext:
        tokens = []
        fp = open('current.data.ftr.tok'.format(filename), 'rb')
        for line in fp:
            tokens.append(line.split()[1:])
        fp.close()
        fp = open('alignments.txt', 'rb')
        lines = fp.readlines()
        fp.close()
        os.rename('alignments.txt', 'alignments.txt.ori')
        fp = open('alignments.txt', 'wb')
        state = 0
        for line in lines:
            if (state == 0 or state == 2) and line[:1] == b'[':
                line1 = int(line.split(b']', 1)[0][1:]) - 1
                state = 1
            elif state == 1:
                line2 = int(line.split(b']', 1)[0][1:]) - 1
                state = 2
            elif state == 2 or state == 3:
                if line.strip():
                    if state == 2:
                        l = line1
                    else:
                        l = line2
                    items = [x.strip() for x in line.split(b'\t')]
                    j = 0
                    for i in range(len(items)):
                        if items[i]:
                            items[i] = tokens[l][j]
                            j += 1
                    line = b'\t'.join(items) + b'\n'
                    state += 1
            elif state == 4:
                state = 2
            fp.write(line)
        fp.close()

    pagenum = 0
    linecount = 0
    state = 0
    fpin = open('alignments.txt', 'rb')
    infile = False
    for line in fpin:
        linecount -= 1
        if line[:1] == b'[':
            state = 1 - state
        if linecount < 0 and state == 1:
            if infile:
                fp.close()
            pagenum += 1
            fp = open('alignments{}.txt'.format(pagenum), 'wb')
            infile = True
            linecount = 500
        fp.write(line)
    if infile:
        fp.close()
    fpin.close()
    if pagenum:
        fp = open('page', 'wt')
        fp.write('1\n')
        fp.close()
        fp = open('pages', 'wt')
        fp.write('{}\n'.format(pagenum))
        fp.close()

    fp = open('current', 'wt', encoding='utf-8')
    fp.write('{}\n{}\n'.format(itemname, placeidx))
    fp.close()
else:
    if os.access('current', os.F_OK):
        os.remove('current')
sys.stdout.write('Location: goto?p={}-align\n\n'.format(path))
