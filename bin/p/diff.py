#!/usr/bin/env python
"""
--documentation--
"""

__author__ = "Peter Kleiweg"
__version__ = "0.1"
__date__ = "2010/04/10"

#| imports

import os, sys, unicodedata

import u.path, u.html, u.config

#| globals

title = 'statistics and difference maps'

_methods = {
    'lev'             : 'String Edit Distance &mdash; Plain',
    'levfeat-tok'     : 'String Edit Distance &mdash; Tokenized',
    'levfeat-user'    : 'String Edit Distance &mdash; User defined',
    'bin'             : 'Binary comparison',
    'giw'             : 'Gewichteter Identit&auml;tswert',
    'num'             : 'Numeric distance &mdash; not normalised',
    'numnorm'         : 'Numeric distance &mdash; normalised by column',
    'dif'             : 'User supplied differences &mdash; Method unknown',
}

#| functions

def _number(s):
    try:
        f = '{:.2f}'.format(float(s))
    except:
        f = u.html.escape(s)
    return f

def makepage(path):
    u.path.chdir(path)
    crumbs = u.path.breadcrumbs(path)
    ltitle = path.split('-')[1].replace('_', ' ') + ' / ' + title

    pnum =  path.split('-')[-2].split('_')[-1]

    p = path.split('-', 1)[1]

    sys.stdout.write(u.html.head(ltitle, tip=True, maptip=True))
    sys.stdout.write('''
    {}
    <div class="pgdiff">
    <h2>{}</h2>
    '''.format(crumbs, title))

    if os.access('OK', os.F_OK):

        fp = open('ca.txt', 'r')
        ca = fp.read().strip()
        fp.close()

        if os.access('../map/PSEUDOMAP', os.F_OK):
            linc = 'undefined for pseudomap'
        else:
            fp = open('linc.txt', 'r')
            linc = fp.read()
            fp.close()

        try:
            fp = open('../data/Method', 'rt')
            m = fp.readline().strip()
            fp.close()
        except:
            pass
        else:
            mt = 'Method: {}\n<p>'.format(_methods[m])

        sys.stdout.write(mt + '\n')

        sys.stdout.write('Cronbach\'s alpha: {}{}\n<p>\n'.format(_number(ca), u.html.help('ca')))
                
        sys.stdout.write('''
        Local incoherence: {0}{1}
        <p>
        &rarr; <a href="{2}bin/getdiff?p=project_{3}&f=L04" target="_blank">download differences</a> (RuG/L04 format) 
        <p>
        &rarr; <a href="{2}bin/getdiff?p=project_{3}&f=tab" target="_blank">download differences</a> (table format)
        '''.format(_number(linc), u.html.help('linc'), u.config.appurl, pnum))

        if m.startswith('levfeat'):
            sys.stdout.write('''
            <p>
            &rarr; <a href="{}bin/getfeat?p=project_{}" target="_blank">download feature definition</a>
            '''.format(u.config.appurl, pnum))


        sys.stdout.write('''
        <p>
        {}
        <p>
        {}
        <p>
        {}
        '''.format(u.html.img(p + '-diff01'),
                   u.html.img(p + '-diff1', usemap="map1", idx=1),
                   u.html.img(p + '-diff', usemap="map1", idx=2)))

    elif os.access('QUEUED', os.F_OK):
        sys.stdout.write(u.html.busy())
    else:
        sys.stdout.write(u.html.makeError(path.split('-', 1)[1]))

    sys.stdout.write('\n</div>\n')
    sys.stdout.write(u.html.foot())


#| main
