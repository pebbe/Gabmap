#!/usr/bin/env python3
"""
--documentation--
"""

__author__ = "Peter Kleiweg"
__version__ = "0.1"
__date__ = "2010/05/13"

#| imports

import cgitb; cgitb.enable(format="html")

import cgi, os, re, sys, time

import u.html, u.config, u.path, u.queue
from u.login import username

#| globals



#| functions

def getval(field):
    return re.sub(r'\s+', ' ', form.getvalue(field, '')).strip()

def change(col, n, subset, method):
    try:
        os.remove('den.eps')
    except:
        pass

    assert col in 'c bw'.split()
    assert method in 'cl ga wa wm'.split()

    if col == 'bw':
        mapname = '{}{}bw'.format(method, n)
    else:
        mapname = '{}{}'.format(method, n)
    makes = ''

    grpfile = 'grp_{}_{}'.format(method, n)

    if not os.access(mapname + '.eps', os.F_OK):
        makes += '\tcluster -o tmp.m -{} ../diff/diff.txt\n'.format(method)

        if not os.access(grpfile, os.F_OK):
            makes += '\tclgroup -n {} -i -o {} tmp.m\n'.format(n, grpfile)
            makes += '\tmkoutliers {} ../diff/diff.txt\n'.format(grpfile)

        if col == 'bw':
            opt = '-b -s'
        else:
            opt = '-u {}templates/palette12.txt'.format(u.config.appdir)
        makes += '\tgrep -v ^markers: ../map/map.cfg > map.cfg\n'
        if col == 'bw':
            makes += '\techo borderwidth: 2 >> map.cfg\n'.format(grpfile)
            makes += '\tmapclust {} -o {}.eps map.cfg tmp.m {}\n'.format(opt, mapname, n)
        else:
            makes += '\techo othermarkers: {}.map >> map.cfg\n'.format(grpfile)
            makes += "\tmapclust {} map.cfg tmp.m {} | perl -p -e s'!/Graylimit .* def!/Graylimit 0 def!' > {}.eps\n".format(
                opt, n, mapname)
        makes += '\t{} {}/util/smappost {}.eps\n'.format(u.config.python3, u.config.appdir, mapname)
        makes += '\trm -f tmp.m\n'

    if col == 'bw':
        p = 'plot_{}_{}bw_{}'.format(method, n, subset)
    else:
        p = 'plot_{}_{}_{}'.format(method, n, subset)
    plotname = p.replace(' ', '_')
    if not os.access(plotname + '.eps', os.F_OK):
        fp = open(u.config.appdir + 'templates/plot_wm.cfg', 'rt')
        data = fp.read()
        fp.close()
        fp = open(plotname + '.cfg', 'wt')
        fp.write(data)
        fp.write('outfile: {}.eps\n'.format(plotname))
        fp.write('groups: {}\n'.format(n))
        fp.write('plot: {}\n'.format(subset))
        if col == 'bw':
            fp.write('colours: none\nmarkers: symbols\nbgcol: 1 1 1\n')
        else:
            fp.write('colours: standard\nmarkers: dots\nbgcol: .6 .6 .6\nsymbolline: 1\n')
            fp.write('markfile: {}.plot\n'.format(grpfile))
        fp.write('cluster: {}\n'.format(method))
        #fp.write('mds: kruskal\n')
        fp.close()
        makes += '\tPYTHONPATH={0} ; mdsplot {1}.cfg 2> {1}.log\n'.format(u.config.python2path, plotname)

    if makes:
        u.queue.enqueue(path + '/clumaps', 'OK: ../diff/OK\n' + makes + '\teps2png\n\ttouch OK\n')
        u.queue.run()
        time.sleep(2)

    fp = open('current', 'wt')
    fp.write('{} {} {}\n{}\n'.format(col, n, subset, method))
    fp.close()
    sys.stdout.write('Location: goto?p={}-clumaps\n\n'.format(path))

def setMethod():
    try:
        fp = open('current', 'rt')
        col = fp.readline().split()[0]
        fp.close()
    except:
        col = 'c'
    m = getval('m')
    if m == 'wm':
        n = 6
    else:
        n = 10
    change(col, n, 'all', m)

def setNumber():
    try:
        fp = open('current', 'rt')
        col = fp.readline().split()[0]
        try:
            method = fp.readline().split()[0]
        except:
            method = 'wm'
        fp.close()
    except:
        col = 'c'
        method = 'wm'
    n = int(getval('n'))
    assert n >= 2 and n <= 12
    change(col, n, 'all', method)

def setSubset():
    try:
        fp = open('current', 'rt')
        col, n = fp.readline().split()[:2]
        n = int(n)
        try:
            method = fp.readline().split()[0]
        except:
            method = 'wm'
        fp.close()
    except:
        col = 'c'
        n = 6
        method = 'wm'
    subset = []
    for i in range(1, n + 1):
        if getval('s{}'.format(i)):
            subset.append(i)
    if len(subset) == n or len(subset) == 0:
        subset = ['all']
    change(col, n, ' '.join([str(x) for x in subset]), method)

def setBW(bw):
    try:
        fp = open('current', 'rt')
        n, subset = fp.readline().split(None, 2)[1:]
        n = int(n)
        subset = subset.strip()
        try:
            method = fp.readline().split()[0]
        except:
            method = 'wm'
        fp.close()
    except:
        n = 6
        subset = 'all'
        method = 'wm'
    change(bw, n, subset, method)

def setLabels(s):
    fp = open('curden', 'wt')
    fp.write(s + '\n')
    fp.close()
    try:
        os.remove('den.eps')
    except:
        pass
    sys.stdout.write('Location: goto?p={}-clumaps\n\n'.format(path))
    

#| main

u.html.loginCheck()

form = cgi.FieldStorage()

path = getval('p')

if not path:
    sys.stdout.write('Location: home\n\n')
    sys.exit()

u.path.chdir(username + '-' + path + '-clumaps')

a = getval('action')

if a == 'number':
    setNumber()
elif a == 'subset':
    setSubset()
elif a == 'method':
    setMethod()
elif a == 'bw':
    setBW('bw')
elif a == 'denlabno':
    setLabels('no')
elif a == 'denlabyes':
    setLabels('yes')
else:
    setBW('c')
