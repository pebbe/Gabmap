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

import u.path, u.html, u.config

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

    sys.stdout.write(u.html.head(ltitle))
    sys.stdout.write('''
    {}
    <div class="pgitems">
    <h2>{}</h2>
    '''.format(crumbs, title))


    if os.access('../data/OK', os.F_OK):

        items = []

        method = open('../data/Method', 'rt').read().strip()

        sys.stdout.write('''
        <div class="info">
        This is a list of all items &mdash; the column labels &mdash; in your data set.<br>
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
        Click on a number to get a data map.
        </div>
        ''')


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
                    items.append((item, n, m))
                else:
                    items.append((item, n))
            fp = open('list2.utxt', 'wt', encoding='utf-8')
            if method.startswith('levfeat'):
                for item, n, m in sorted(items):
                    fp.write('{}\t{}\t{}\n'.format(n, m, item))
            else:
                for item, n in sorted(items):
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

    elif os.access('../data/QUEUED', os.F_OK):
        os.chdir('../data/')
        sys.stdout.write(u.html.busy())
    else:
        sys.stdout.write(u.html.makeError(path.split('-', 1)[1]).replace('items', 'data'))

    sys.stdout.write('\n</div>\n')
    sys.stdout.write(u.html.foot())



#| main
