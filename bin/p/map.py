#!/usr/bin/env python
"""
--documentation--
"""

__author__ = "Peter Kleiweg"
__version__ = "0.1"
__date__ = "2010/04/10"

#| imports

#import locale
import os, re, sys, unicodedata

import u.path, u.html, u.config

#| globals

title = 'places'

#| functions

def _unquote(s):
    s = s.strip()
    if len(s) < 2:
        return s
    if s[0] != '"' or s[-1] != '"':
        return s
    return re.sub(r'\\(.)', r'\1', s[1:-1]).strip()

def makepage(path):
    u.path.chdir(path)
    crumbs = u.path.breadcrumbs(path)
    ltitle = path.split('-')[1].replace('_', ' ') + ' / ' + title

    p = path.split('-', 1)[1]
    pnum =  path.split('-')[-2].split('_')[-1]

    sys.stdout.write(u.html.head(ltitle, tip=True, maptip=True))
    sys.stdout.write('''
    {}
    <div class="pgmap">
    <h2>{}</h2>
    '''.format(crumbs, title))

    if os.access('OK', os.F_OK):

        if not os.access('mapcoo.eps', os.F_OK):
            os.system('$PYTHON3 $APPDIR/util/ps2coo')
        if not os.access('mapcoo.png', os.F_OK):
            os.system('eps2png > /dev/null 2>&1')
        if not os.access('image.html', os.F_OK):
            os.system('$PYTHON3 $APPDIR/util/mkmap')

        fp = open('image.html', 'rt', encoding='utf-8')
        for line in fp:
            sys.stdout.write(line)
        fp.close()

        sys.stdout.write(u.html.img(p + '-mapcoo', usemap="map1", idx=1, noover=True))

        if not os.access('PSEUDOMAP', os.F_OK):
            sys.stdout.write('''
            <p>
            &rarr; <a href="mapdstget?p={0}&f=tbl">download distances in table format</a><br>
            &rarr; <a href="mapdstget?p={0}&f=l04">download distances in L04 format</a><br>
            note: these are <em>geographic</em> distances in kilometers
            <p>
            '''.format(pnum))

        sys.stdout.write(u.html.img(p + '-mapidx', usemap="map1", idx=2, noover=True))

        if os.access('WARNINGS.txt', os.F_OK):
            sys.stdout.write('<pre class="log">\n')
            fp = open('WARNINGS.txt', 'rt', encoding='iso-8859-1')
            for line in fp:
                sys.stdout.write(u.html.escape(line))
            fp.close()
            sys.stdout.write('</pre>\n')

        lines = []
        sys.stdout.write('<table width="100%"><tr><td><pre>\n')
        labels = set()
        truelabels = {}
        fp = open('../data/labels.txt', 'rt', encoding='iso-8859-1')
        fp2 = open('../data/truelabels.txt', 'rt', encoding='utf-8')
        for line in fp:
            lbl = line.strip().split(None, 1)[1]
            labels.add(lbl)
            truelabels[lbl] = fp2.readline().strip()
        fp2.close()
        fp.close()
        fp = open('map.lbl', 'rt', encoding='iso-8859-1')
        for line in fp:
            a, b = line.strip().split(None, 1)
            b = _unquote(b)
            if b in labels:
                b = u.html.escape(truelabels[b])
                lines.append((b, a))
                sys.stdout.write('{:8d}    {}\n'.format(int(a), b))
        fp.close()
        #loc = locale.getlocale()
        #locale.setlocale(locale.LC_COLLATE, 'en_US')
        sys.stdout.write('</pre>\n<td><pre>\n')
        for b, a in sorted(lines):
            sys.stdout.write('{:8d}    {}\n'.format(int(a), b))
        sys.stdout.write('</pre>\n</table>\n')
        #locale.setlocale(locale.LC_COLLATE, loc)

    elif os.access('QUEUED', os.F_OK):
        sys.stdout.write(u.html.busy())
    else:
        sys.stdout.write(u.html.makeError(path.split('-', 1)[1]))

    sys.stdout.write('\n</div>\n')
    sys.stdout.write(u.html.foot())


#| main
