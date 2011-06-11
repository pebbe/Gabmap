#!/usr/bin/env python
"""
--documentation--
"""

__author__ = "Peter Kleiweg"
__version__ = "0.1"
__date__ = "2010/04/10"

#| imports

import os, sys

import u.path, u.html

#| globals

title = 'mds maps'

#| functions

def _getcor(filename, varname='r'):
    if os.access(filename, os.F_OK):
        fp = open(filename, 'rt')
        s = '<i>{}</i> = {:.2f}'.format(varname, float(fp.read()))
        fp.close()
        return s
    else:
        return ''

def makepage(path):
    u.path.chdir(path)
    crumbs = u.path.breadcrumbs(path)
    ltitle = path.split('-')[1].replace('_', ' ') + ' / ' + title

    p = path.split('-', 1)[1]
    project = path.split('-')[1]

    sys.stdout.write(u.html.head(ltitle, tip=True, maptip=True))
    sys.stdout.write('''
    {}
    <div class="pgmdsmaps">
    <h2>mds maps</h2>
    '''.format(crumbs))

    if os.access('OK', os.F_OK):
        corr = _getcor('standard03c.cor')
        sys.stdout.write('''
        {}
        <small>{}</small>
        <p>
        Above: Classical MDS in three dimensions mapped onto RGB color space.
        <p>
        Below: Classical MDS into multiple dimensions, one map per dimension.
        '''.format(u.html.img(p + '-standard', usemap='map1', idx=999), corr))

        for i in range(1, 7):
            if not os.access('standard{:02d}.eps'.format(i), os.F_OK):
                continue
            cor1 = _getcor('standard{:02d}.cor'.format(i))
            cor2 = _getcor('standard{:02d}c.cor'.format(i))
            stress = _getcor('standard{:02d}.stress'.format(i), 'stress')
            sys.stdout.write('\n<p>\n' + u.html.img(p + '-standard{:02d}'.format(i), True, usemap='map1', idx=i))
            if i == 1:
                e = 'st'
            elif i == 2:
                e = 'nd'
            elif i == 3:
                e = 'rd'
            else:
                e = 'th'
            sys.stdout.write('<small>{}{} dimension: {}'.format(i, e, cor1))
            if i > 1:
                sys.stdout.write('<br>\n{} dimensions: {}'.format(i, cor2))
            if stress:
                if i > 1:
                    pl = 's'
                else:
                    pl = ''
                sys.stdout.write('<br>\n{} dimension{}: {}'.format(i, pl, stress))
            sys.stdout.write('</small>\n')
                
            

        sys.stdout.write('<p>\n' + u.html.img(p + '-plot01'))

        if os.access('plot02.eps', os.F_OK):
            sys.stdout.write('<p>\n' + u.html.img(p + '-plot02'))



    elif os.access('QUEUED', os.F_OK):
        sys.stdout.write(u.html.busy())
    else:
        sys.stdout.write(u.html.makeError(path.split('-', 1)[1]))

    sys.stdout.write('\n</div>\n')
    sys.stdout.write(u.html.foot())


#| main
