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

title = 'cluster validation'

methods = {
    'cl': 'Complete Link',
    'ga': 'Group Average',
    'wa': 'Weighted Average',
    'wm': "Ward's Method"
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

    p = path.split('-', 1)[1]
    project = path.split('-')[1]

    sys.stdout.write(u.html.head(ltitle, tip=True, maptip=True))
    sys.stdout.write('''
    {}
    <div class="pgclumaps">
    <h2>{}</h2>
    '''.format(crumbs, title))

    if os.access('OK', os.F_OK):        

        sys.stdout.write('''
        <div class="info">
        The results of clustering can be deceptive. So,
        the purpose of this page is not just to devide your data into dialects groups, but to test the validity of each group.<br>
        &nbsp;<br>
        For an introduction, read <a href="{}doc/ClusterValidation" target="_blank">this demonstration</a>
        </div>
        '''.format(u.config.appurls))


        open('reset', 'wt').close()
        current2 = ['wm']
        try:
            fp = open('current', 'rt')
            lines = fp.readlines()
            fp.close()
            current = lines[0].split()
            if len(lines)> 1:
                current2 = lines[1].split()
        except:
            current = ['c', '6', 'all']
        if current[0] == 'c':
            bw = ''
        else:
            bw = 'bw'
        method = current2[0]
        n = int(current[1])
        current = current[2:]
        logfile = 'plot_{}_{}{}_{}.log'.format(method, n, bw, '_'.join(current))
        if os.access(logfile, os.F_OK):
            corr = '<small><i>r</i> = ' + _number(open(logfile, 'rt').read().strip().split()[-1]) + '</small>'
        else:
            corr = ''
        sys.stdout.write('''
        {}
        <p>
        Above: Clustering using <b>{}</b>.
        <p>
        Below: An MDS-plot of the clusters from the map shows what major cluster divisions are "real".
        You can omit one major group of clusters to inspect the divisions of the remaining clusters.
        {}
        {}
        <p>
        '''.format(u.html.img(p + '-{}{}{}'.format(method, n, bw), usemap="map1", pseudoforce=True),
                   methods[method],
                   u.html.img((p + '-plot_{}_{}{}_{}'.format(method, n, bw, '_'.join(current)))),
                   corr))

        sys.stdout.write('''
	<form action="{}clumapsform" method="post">
	<input type="hidden" name="p" value="{}">
	<input type="hidden" name="action" value="method">
        <em>Note: each of the following buttons changes a single option</em>
        <p>
	Clustering method:
	<select name="m">
        '''.format(u.config.binurls, project))
        for i in sorted(methods):
            if i == method:
                sys.stdout.write('<option selected="selected" value="{}">{}</option>\n'.format(i, methods[i]))
            else:
                sys.stdout.write('<option value="{}">{}</option>\n'.format(i, methods[i]))
        sys.stdout.write('''
	  </select>
	<input type="submit" value="Change method">
	</form>
        <p>
        ''')

        sys.stdout.write('''
	<form action="{}clumapsform" method="post">
	<input type="hidden" name="p" value="{}">
	<input type="hidden" name="action" value="number">
	Number of clusters:
	<select name="n">
        '''.format(u.config.binurls, project))
        for i in range(2, 13):
            if i == n:
                sys.stdout.write('<option selected="selected">{}</option>\n'.format(i))
            else:
                sys.stdout.write('<option>{}</option>\n'.format(i))
        sys.stdout.write('''
	  </select>
	<input type="submit" value="Change number">
	</form>
        <p>
        ''')

        sys.stdout.write('''
	<form action="{}clumapsform" method="post">
	<input type="hidden" name="p" value="{}">
	<input type="hidden" name="action" value="subset">
	Clusters in plot:
        '''.format(u.config.binurls, project))

        if current[0] == 'all':
            subset = set(range(1, n + 1))
        else:
            subset = set(int(x) for x in current)

        if bw == 'bw':
            for i in range(1, n + 1):
                if i in subset:
                    sys.stdout.write('<span class="sym"><input type="checkbox" name="s{0}" checked="checked"><img src="{1}img/sym{0:02d}.png"></span>\n'.format(i, u.config.appurl))
                else:
                    sys.stdout.write('<span class="sym"><input type="checkbox" name="s{0}"><img src="{1}img/sym{0:02d}.png"></span>\n'.format(i, u.config.appurl))
        else:
            for i in range(1, n + 1):
                if i in subset:
                    sys.stdout.write('<span class="s{0}"><input type="checkbox" name="s{0}" checked="checked"></span>\n'.format(i))
                else:
                    sys.stdout.write('<span class="s{0}"><input type="checkbox" name="s{0}"></span>\n'.format(i))
        sys.stdout.write('''
	<input type="submit" value="Change subset">
	</form>
        <p>
        ''')

        if bw == 'bw':
            sys.stdout.write('''
            <form action="{}clumapsform" method="post">
            <input type="hidden" name="p" value="{}">
            <input type="hidden" name="action" value="col">
            <input type="submit" value="Switch to colour">
            </form>
            '''.format(u.config.binurls, project))
        else:
            sys.stdout.write('''
            <form action="{}clumapsform" method="post">
            <input type="hidden" name="p" value="{}">
            <input type="hidden" name="action" value="bw">
            <input type="submit" value="Switch to black/white">
            </form>
            '''.format(u.config.binurls, project))

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
