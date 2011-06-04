#!/usr/bin/env python
"""
--documentation--
"""

__author__ = "Peter Kleiweg"
__version__ = "0.1"
__date__ = "2010/04/10"

#| imports

import os, sys

import u.path, u.html, u.config

#| globals

title = 'cluster maps and dendrograms'

methods = {
    'cl': 'Complete Link',
    'ga': 'Group Average',
    'wa': 'Weighted Average',
    'wm': "Ward's Method"
    }

colors = {
    'col': 'yes',
    'bw' : 'no'
    }


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
    <div class="pgclusters">
    <h2>{}</h2>
    '''.format(crumbs, title))

    if os.access('OK', os.F_OK):        

        sys.stdout.write('''
        <div class="info">
        Warning: the type of clustering used on this page can be unreliable.<br>
        Go to <a href="goto?p={}-clumaps">this page</a> to test the validity of the clusters you see here.
        </div>
        '''.format(project))


        fp = open('current.txt', 'rt')
        method, groups, col = fp.read().split()
        fp.close()

        sys.stdout.write('''
        {}
        <p>
        {}
        '''.format(u.html.img('{}-map{}{}{}'.format(p, method, groups, col), usemap="map1"),
                   u.html.img('{}-den{}{}{}'.format(p, method, groups, col))))

        sys.stdout.write('''
        <p>
	<form action="{}bin/clusterform" method="post">
        <fieldset><legend></legend>
	<input type="hidden" name="p" value="{}">
	Clustering method:
	<select name="mthd">
        '''.format(u.config.appurl, project))
        for i in sorted(methods):
            if i == method:
                sys.stdout.write('<option selected="selected" value="{}">{}</option>\n'.format(i, methods[i]))
            else:
                sys.stdout.write('<option value="{}">{}</option>\n'.format(i, methods[i]))
        sys.stdout.write('''
        </select><br>
        &nbsp;<br>
	Number of clusters:
	<select name="n">
        ''')
        n = int(groups)
        maxnum = min(13, int(open('../data/stats.txt', 'rt').read().split()[0]))
        for i in range(2, maxnum):
            if i == n:
                sys.stdout.write('<option selected="selected">{}</option>\n'.format(i))
            else:
                sys.stdout.write('<option>{}</option>\n'.format(i))
        sys.stdout.write('''
        </select><br>
        &nbsp;<br>
        Use color:
	<select name="col">
        ''')
        for i in sorted(colors):
            if i == col:
                sys.stdout.write('<option selected="selected" value="{}">{}</option>\n'.format(i, colors[i]))
            else:
                sys.stdout.write('<option value="{}">{}</option>\n'.format(i, colors[i]))
        sys.stdout.write('''
        </select><br>
        &nbsp;<br>
        <input type="submit" value="Change settings">
        </fieldset>
        </form>
        <p>
        ''')

        if col == 'bw':
            groups = 1
        sys.stdout.write(u.html.img('{}-den{}{}{}alt'.format(p, method, groups, col)))


    elif os.access('QUEUED', os.F_OK):
        sys.stdout.write(u.html.busy())
    else:
        sys.stdout.write(u.html.makeError(path.split('-', 1)[1]))
        if os.access('reset', os.F_OK):
            for filename in os.listdir('.'):
                if filename.startswith('current') or filename.startswith('tmp'):
                    os.remove(filename)
            open('OK', 'wt').close()
            sys.stdout.write('<p>\n<a href="">Continue</a>\n')

    sys.stdout.write('\n</div>\n')
    sys.stdout.write(u.html.foot())


#| main
