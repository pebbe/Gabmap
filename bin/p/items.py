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


def makepage(path):

    u.path.chdir(path[:-6])
    if not os.path.isdir('items'):
        os.mkdir('items')
    os.chdir('items')

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


    if os.access('../data/OK', os.F_OK) and os.access('../map/OK', os.F_OK):

        items = []

        method = open('../data/Method', 'rt').read().strip()

        sys.stdout.write('''
        <div class="info">
        The map shows the total amount of data available for each location.
        <br>&nbsp;<br>
        Below the map is a list of all items &mdash; the column labels &mdash; in your data set.<br>
        The number says how many instances are available for each item.
        ''')
        if method.startswith('levfeat'):
            sys.stdout.write('''<br>&nbsp;<br>
            If there are two numbers for an item, the first is the number of instances you supplied,<br>
            the second number is the number of instances that are actually used.
            {}
            '''.format(u.html.more('items')))
        sys.stdout.write('''
        <br>&nbsp;<br>
        Click on a number to get a data map for a single item.
        </div>
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
            if method.startswith('levfeat'):
                e = '.ftr'
            else:
                e = '.data'
            p = {}
            pn = {}
            for filename in os.listdir('../data/_'):
                if not filename.endswith(e):
                    continue
                pseen = set()
                fp = open('../data/_/' + filename, 'rb')
                for line in fp:
                    if line[:1] == b':':
                        lbl = line[1:].decode('iso-8859-1').strip()
                        if not lbl in p:
                            p[lbl] = 0
                        if not lbl in pn:
                            pn[lbl] = 0
                    elif line[:1] == b'-' or line[:1] == b'+':
                        p[lbl] += 1
                        if not lbl in pseen:
                            pn[lbl] += 1
                            pseen.add(lbl)
                fp.close()
            fp = open('datacount.txt', 'wt', encoding='utf-8')
            for i in sorted(p):
                fp.write('{:6d}\t{:6d}\t{}\n'.format(pn[i], p[i], truelabels[i]))
            fp.close()
            m = max(pn.values())
            m *= m
            pp = {}
            for i in pn:
                pn[i] *= pn[i]
                pp[i] = m
            os.chdir('..')
            u.distribute.distmap(pn, pp, 'items/datacount')
            os.chdir('items')

        p = path.split('-', 1)[1]
        pnum =  path.split('-')[-2].split('_')[-1]
        sys.stdout.write(u.html.img(p + '-datacount', usemap="map1", bw=True))
        sys.stdout.write('''
        &rarr; <a href="{}bin/getdatacount?{}" target="_blank">download as list</a>
        <p>
        '''.format(u.config.appurl, pnum))

        if not os.access('list2.utxt', os.F_OK):
            for filename in os.listdir('../data/_'):
                if not filename.endswith('.data'):
                    continue
                item = re.sub('_([0-9]+)_', _num2chr, filename[:-5])
                n = 0
                fp = open('../data/_/' + filename, 'rb')
                for line in fp:
                    if line[:1] == b'-' or line[:1] == b'+':
                        n += 1
                fp.close()
                if method.startswith('levfeat'):
                    m = 0
                    fp = open('../data/_/' + filename + '.ftr', 'rb')
                    for line in fp:
                        if line[:1] == b'+':
                            m += 1
                    fp.close()
                    items.append((item.lower(), item, n, m))
                else:
                    items.append((item.lower(), item, n))
            fp = open('list2.utxt', 'wt', encoding='utf-8')
            if method.startswith('levfeat'):
                for k, item, n, m in sorted(items):
                    fp.write('{}\t{}\t{}\n'.format(n, m, item))
            else:
                for k, item, n in sorted(items):
                    fp.write('{}\t{}\n'.format(n, item))
            fp.close()

        sys.stdout.write('<table class="items" cellspacing="0" cellpadding="0" border="0">\n')
        fp = open('list2.utxt', 'rt', encoding='utf-8')
        i = -1
        if method.startswith('levfeat'):
            for line in fp:
                i += 1
                n, m, item = line.split(None, 2)
                if n == m:
                    n = ''
                if n != '' and n != '0':
                    n = '<a href="imap?{}-{}-0" target="_blank">{}</a>'.format(pnum, i, n)
                if m != '0':
                    m = '<a href="imap?{}-{}-1" target="_blank">{}</a>'.format(pnum, i, m)
                sys.stdout.write('<tr><td align="right">{}<td align="right">{}<td>{}\n'.format(n, m, u.html.escape(item)))
        else:
            for line in fp:
                i += 1
                n, item = line.split(None, 1)
                if n != '0':
                    n = '<a href="imap?{}-{}-0" target="_blank">{}</a>'.format(pnum, i, n)
                sys.stdout.write('<tr><td align="right">{}<td>{}\n'.format(n, u.html.escape(item)))
        fp.close()
        sys.stdout.write('</table>\n')

    elif os.access('../data/QUEUED', os.F_OK) or os.access('../map/QUEUED', os.F_OK):
        os.chdir('../data/')
        sys.stdout.write(u.html.busy())
    else:
        if os.access('../data/QUEUED', os.F_OK):
            p = 'map'
        else:
            p = 'data'
        sys.stdout.write(u.html.makeError(path.split('-', 1)[1]).replace('items', p))

    sys.stdout.write('\n</div>\n')
    sys.stdout.write(u.html.foot())



#| main
