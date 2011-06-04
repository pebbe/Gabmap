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

title = 'data overview'

#| functions

def _num2chr(m):
    return '{:c}'.format(int(m.group(1)))


def makepage(path):

    u.path.chdir(path[:-8])
    os.chdir('data')

    crumbs = u.path.breadcrumbs(path)
    ltitle = path.split('-')[1].replace('_', ' ') + ' / ' + title

    p = path.split('-', 1)[1]
    pnum =  path.split('-')[-2].split('_')[-1]

    sys.stdout.write(u.html.head(ltitle))
    sys.stdout.write('''
    {}
    <div class="pgdata">
    <h2>{}</h2>
    '''.format(crumbs, title))

    if os.access('OK', os.F_OK):

        sys.stdout.write('''
        Contents:
        <ul>
        <li><a href="#overview">Overview</a>
        <li><a href="#boxplot">Box plots</a>
        </ul>
        ''')


        sys.stdout.write('<h3 id="overview">Overview{}</h3>\n'.format(u.html.help('numdataoverview')))

        if os.access('comments.txt', os.F_OK):
            sys.stdout.write('<pre class="log">\n')
            fp = open('comments.txt', 'rt', encoding='utf-8')
            for line in fp:
                sys.stdout.write(u.html.escape(line))
            fp.close()
            sys.stdout.write('</pre>\n')

        if os.access('stats.txt', os.F_OK):
            fp = open('stats.txt', 'rt')
            nPlaces, nItems, NAs = [int(x) for x in fp.read().split()]
            Total = nPlaces * nItems
            Values = Total - NAs
            sys.stdout.write('''
            <table class="stats" border="0" cellspacing="0" cellpadding="0">
            <tr><td>Places:<td align="right">{0}
            <tr><td>Items:<td align="right">{1}
            <tr><td>Values:<td align="right">{2}<td>(of {4})<td align="right">{5:.3f}%
            <tr><td>Missing:<td align="right">{3}<td>(of {4})<td align="right">{6:.3f}%
            </table>
            <p>
            '''.format(nPlaces, nItems, Values, NAs, Total, Values * 100.0 / Total, NAs * 100.0 / Total))



        sys.stdout.write('<h3 id="boxplot">Box plots{}</h3>\n'.format(u.html.help('numdataboxplot')))
        

        sys.stdout.write(u.html.img(p.replace('numdata', 'data') + '-boxplot01'))

        if os.access('boxplot02.eps', os.F_OK):
            sys.stdout.write('''
            un-normalised values
            <p>
            {}
            normalised values
            '''.format(u.html.img(p.replace('numdata', 'data') + '-boxplot02')))


    elif os.access('../diff/QUEUED', os.F_OK):
        os.chdir('../diff')
        sys.stdout.write(u.html.busy())
    else:
        sys.stdout.write(u.html.makeError(path.split('-', 1)[1].replace('numitems', 'diff')))

    sys.stdout.write('\n</div>\n')
    sys.stdout.write(u.html.foot())



#| main
