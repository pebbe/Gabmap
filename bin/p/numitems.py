#!/usr/bin/env python
"""
--documentation--
"""

__author__ = "Peter Kleiweg"
__version__ = "0.1"
__date__ = "2010/04/10"

#| imports

#import locale
import os, re, sys

import u.path, u.html, u.config, u.distribute

#| globals

title = 'items'

#| functions

def _num2chr(m):
    return '{:c}'.format(int(m.group(1)))


def _unquote(s):
    s = s.strip()
    if len(s) < 2:
        return s
    if s[0] != '"' or s[-1] != '"':
        return s
    return re.sub(r'\\(.)', r'\1', s[1:-1]).strip()

def _num2chr(m):
    return '{:c}'.format(int(m.group(1)))

def _iso2utf(s):
    if not s:
        return ''
    return re.sub('&#([0-9]+);', _num2chr, s)

def makepage(path):

    u.path.chdir(path[:-9])
    os.chdir('data')

    crumbs = u.path.breadcrumbs(path)
    ltitle = path.split('-')[1].replace('_', ' ') + ' / ' + title

    p = path.split('-', 1)[1]
    pnum =  path.split('-')[-2].split('_')[-1]

    sys.stdout.write(u.html.head(ltitle, tip=True, maptip=True))
    sys.stdout.write('''
    {}
    <div class="pgitems">
    <h2>{}</h2>
    '''.format(crumbs, title))

    if os.access('OK', os.F_OK) and os.access('../map/OK', os.F_OK):

        sys.stdout.write('''
        <div class="info">
        The map shows the total amount of data available for each location.
        <br>&nbsp;<br>
        Below the map is a list of all items &mdash; the column labels &mdash; in your data set.<br>
        The number (if any) says how many values are missing for each item.
        <br>&nbsp;<br>
        Click on a number to get a map of missing values.
        </div>
        <table class="items" cellspacing="0" cellpadding="0" border="0">
        ''')

        if not os.access('datacount.txt', os.F_OK):
            truelabels = {}
            fp1 = open('../data/labels.txt', 'rt', encoding='iso-8859-1')
            fp2 = open('../data/truelabels.txt', 'rt', encoding='utf-8')
            for line in fp1:
                lbl = line.split(None, 1)[1].strip()
                truelabels[lbl] = fp2.readline().strip()
            fp2.close()
            fp1.close()
            p = {}
            fp = open('table.txt', 'rt', encoding='iso-8859-1')
            fp.readline()
            for line in fp:
                i, j = line.rsplit('"', 1)
                lbl = re.sub('\\\\(.)', '\\1', i[1:])
                n = len([True for i in j.split() if i != 'NA'])
                p[lbl] = n
            fp.close()
            fp = open('datacount.txt', 'wt', encoding='utf-8')
            for i in sorted(p):
                fp.write('{:6d}\t{}\n'.format(p[i], truelabels[i]))
            fp.close()
            m = max(p.values())
            m *= m
            pp = {}
            for i in p:
                p[i] *= p[i]
                pp[i] = m
            os.chdir('..')
            u.distribute.distmap(p, pp, 'data/datacount')
            os.chdir('data')

        p = path.split('-', 1)[1].replace('numitems', 'data')
        pnum =  path.split('-')[-2].split('_')[-1]
        sys.stdout.write(u.html.img(p + '-datacount', usemap="map1", bw=True))
        sys.stdout.write('''
        &rarr; <a href="{}bin/getdatacount?{}" target="_blank">download as list</a>
        <p>
        '''.format(u.config.appurl, pnum))

        lines = []
        fp = open('NAs.txt', 'rt', encoding='utf-8')
        n = -1
        for line in fp:
            n += 1
            a = line.split('\t')
            lines.append((a[1].strip(), int(a[0]), n))
        fp.close()
        lines.sort()

        for item, i, n in lines:
            if i == 0:
                i = ''
            else:
                i = '<a href="namap?{}-{}" target="_blank">{}</a>'.format(pnum, n, i)
            sys.stdout.write('<tr><td align="right">{}<td>{}\n'.format(i, u.html.escape(item.strip())))
        sys.stdout.write('</table>\n')


    elif os.access('QUEUED', os.F_OK) or os.access('../map/QUEUED', os.F_OK):
        sys.stdout.write(u.html.busy())
    else:
        if os.access('QUEUED', os.F_OK):
            p = 'map'
        else:
            p = 'data'
        sys.stdout.write(u.html.makeError(path.split('-', 1)[1].replace('numitems', p)))

    sys.stdout.write('\n</div>\n')
    sys.stdout.write(u.html.foot())



#| main
