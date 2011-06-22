#!/usr/bin/env python
"""
--documentation--
"""

__author__ = "Peter Kleiweg"
__version__ = "0.1"
__date__ = "2010/04/10"

#| imports

import os, re, sys

import u.path, u.html, u.config, u.distribute

#| globals

title = 'value maps'

#| functions

def _unquote(s):
    s = s.strip()
    if len(s) < 2:
        return s
    if s[0] != '"' or s[-1] != '"':
        return s
    return re.sub(r'\\(.)', r'\1', s[1:-1]).strip()


def makepage(path):
    u.path.chdir(path[:-7])

    if not os.path.isdir('nummap'):
        os.mkdir('nummap')
    os.chdir('nummap')


    crumbs = u.path.breadcrumbs(path)
    ltitle = path.split('-')[1].replace('_', ' ') + ' / ' + title

    pnum =  path.split('-')[-2].split('_')[-1]

    sys.stdout.write(u.html.head(ltitle, tip=True, maptip=True))
    sys.stdout.write('''
    {}
    <div class="pgdistmap">
    <h2>value maps</h2>
    '''.format(crumbs))

    if not os.access('current.txt', os.F_OK):
        fp = open('current.txt', 'wt')
        fp.write('-1\n')
        fp.close()

    fp = open('current.txt', 'rt', encoding='utf-8')
    current = int(fp.read())
    fp.close()

    items = []
    n = -1
    fp = open('../data/NAs.txt', 'rt', encoding='utf-8')
    for line in fp:
        n += 1
        items.append((line.split(None, 1)[1].strip(), n))
    fp.close()
    items.sort()

    sys.stdout.write('''
    <form action="{}bin/nummapform" method="post">
    <fieldset><legend></legend>
    <input type="hidden" name="p" value="project_{}">
    Item: <select name="item">
    <option value="-1">--</option>
    '''.format(u.config.appurl, pnum))

    for item, i in items:
        if i == current:
            sel = ' selected="selected"'
            found = True
        else:
            sel = ''
        sys.stdout.write('<option value="{}"{}>{}</option>\n'.format(i, sel, u.html.escape(item)))
    fp.close()
    sys.stdout.write('''
    </select>
    <input type="submit" value="Select item">
    </fieldset>
    </form>
    ''')

    if current < 0:
        sys.stdout.write('\n</div>\n')
        sys.stdout.write(u.html.foot())
        return

    if not os.access('limits', os.F_OK):
        fp = open('../data/table.txt', 'rt', encoding='iso-8859-1')
        fp.readline()
        hasF = False
        for line in fp:
            line = line.strip()
            v = [float(x) for x in line.split('\t')[1:] if x != 'NA']
            if v:
                ff1 = min(v)
                ff2 = max(v)                
                if hasF:
                    if ff1 < f1:
                        f1 = ff1
                    if ff2 > f2:
                        f2 = ff2
                else:
                    f1 = ff1
                    f2 = ff2
                    hasF = True
        fp.close()
        fp = open('limits', 'wt')
        fp.write('{:g} {:g}\n'.format(f1, f2))
        fp.close()

    if not os.access('nummap.eps', os.F_OK):
        placen = {}
        placeall = {}
        fp = open('../data/table.txt', 'rt', encoding='iso-8859-1')
        fp.readline()
        for line in fp:
            i = line.split('\t')
            lbl = _unquote(i[0])
            if i[current + 1] == 'NA':
                continue
            value = float(i[current + 1])
            placen[lbl] = value
            placeall[lbl] = 1
        fp.close()
        fp = open('limits', 'rt')
        f1, f2 = [float(x) for x in fp.read().split()]
        fp.close()
        if f1 == f2:
            for p in placen:
                placen[p] = 0.5
        else:
            for p in placen:
                placen[p] = (placen[p] - f1) / (f2 - f1)

        os.chdir('..')
        u.distribute.distmap(placen, placeall, 'nummap/nummap')
        os.chdir('nummap')

        """
    sys.stdout.write('''
    <h3>Value map for{} &quot;<span  class="ipa">{}</span>&quot; in {}</h3>
    '''.format(r, u.html.escape(v), u.html.escape(item)))

    if currentregex:
        sys.stdout.write('<ul>\n')
        fp = open('currentvariants.txt', 'rt', encoding='utf-8')
        for line in fp:
            sys.stdout.write('<li><span class="ipa2">{0[0]}</span> {0[1]}\n'.format(u.html.escape(line.strip()).rsplit(None, 1)))
        fp.close()
        sys.stdout.write('</ul>\n')
        """

    sys.stdout.write(u.html.img('project_{}-nummap-nummap'.format(pnum), True, usemap="map1"))

    sys.stdout.write('\n</div>\n')
    sys.stdout.write(u.html.foot())


#| main
