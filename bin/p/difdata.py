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
        <div class="todo">
        <h3>To do</h3>
        </div>
        ''')


        if os.access('comments.txt', os.F_OK):
            sys.stdout.write('<pre class="log">\n')
            fp = open('comments.txt', 'rt', encoding='utf-8')
            for line in fp:
                sys.stdout.write(u.html.escape(line))
            fp.close()
            sys.stdout.write('</pre>\n')

    elif os.access('QUEUED', os.F_OK):
        sys.stdout.write(u.html.busy())
    else:
        sys.stdout.write(u.html.makeError(path.split('-', 1)[1].replace('difitems', 'diff')))

    sys.stdout.write('\n</div>\n')
    sys.stdout.write(u.html.foot())



#| main
