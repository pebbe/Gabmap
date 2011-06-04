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

title = 'fuzzy cluster maps'

#| functions

def makepage(path):
    u.path.chdir(path)
    crumbs = u.path.breadcrumbs(path)
    ltitle = path.split('-')[1].replace('_', ' ') + ' / ' + title

    p = path.split('-', 1)[1]
    project = path.split('-')[1]

    sys.stdout.write(u.html.head(ltitle, tip=True, maptip=True))
    sys.stdout.write('''
    {}
    <div class="pgcccmaps">
    <h2>{}</h2>
    '''.format(crumbs, title))

    if os.access('OK', os.F_OK):
        open('reset', 'wt').close()

        try:
            fp = open('current', 'rt')
            current = int(fp.read())
            fp.close()
        except:
            current = 2
        sys.stdout.write('''
        {}
        <p>
        Above: Stochastic clustering followed by multidimensional scaling shows the major cluster divisions.
        <p>
        Below: Omit parts of the data to see more detail in the remaining part.
        '''.format(u.html.img(p + '-ccc', usemap="map1", idx=999)))
        for i in range(current):
            if os.access('ccc_{}_{}.eps'.format(current, i + 1), os.F_OK):
                sys.stdout.write('<p>\n{}\n'.format(u.html.img(p + '-ccc_{}_{}'.format(current, i + 1), usemap="map1", idx=i)))
            else:
                sys.stdout.write('<div class="warn">Missing: failed map #{}{}</div>\n'.format(i + 1, u.html.help('cccmapsmissing')))
        sys.stdout.write('''
        <p>
        <form action="{}bin/cccmapsform" method="post">
        <input type="hidden" name="p" value="{}">
        Number of groups:
        <select name="n">
        '''.format(u.config.appurl, project))
        for i in range(2, 9):
            if i == current:
                sys.stdout.write('<option selected="selected">{}</option>\n'.format(i))
            else:
                sys.stdout.write('<option>{}</option>\n'.format(i))
        sys.stdout.write('''
        </select>
        <input type="submit" value="Change">
        </form>
        ''')

    elif os.access('QUEUED', os.F_OK):
        sys.stdout.write(u.html.busy())
    else:
        tooSmall = False
        if os.access('reset', os.F_OK):            
            reset = True
        else:
            reset = False

        if reset:
            fp = open('current', 'rt')
            cur = fp.read().strip()
            fp.close()
            pref = 'ccc_{}_'.format(cur)
            for filename in os.listdir('.'):
                if filename.endswith('.tbl'):
                    n = 0
                    fp = open(filename, 'rt', encoding='iso-8859-1')
                    for line in fp:
                        if line[0] == ':':
                            n += 1
                    fp.close()
                    if n < 4:
                        tooSmall = True
                if filename.startswith('current') or filename.startswith('tmp') or filename.startswith(pref):
                    os.remove(filename)

        if tooSmall:            
            sys.stdout.write('Error: clusters too small' + u.html.help('cccmapserror'))
        else:
            sys.stdout.write(u.html.makeError(path.split('-', 1)[1]))

        if reset:
            sys.stdout.write('<p>\n<a href="">Continue</a>\n')
            open('OK', 'wt').close()


    sys.stdout.write('\n</div>\n')
    sys.stdout.write(u.html.foot())


#| main
