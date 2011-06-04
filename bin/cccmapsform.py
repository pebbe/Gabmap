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

#| main

u.html.loginCheck()

form = cgi.FieldStorage()

path = getval('p')
if not path:
    sys.stdout.write('Location: home\n\n')
    sys.exit()

u.path.chdir(username + '-' + path + '-cccmaps')

n = int(getval('n'))

if not os.access('DONE{}'.format(n), os.F_OK):
    m = 'OK: ../diff/OK\n'
    m += '\tcluster -wm ../diff/diff.txt | clgroup -n {} -i -o tmp.grp\n'.format(n)
    for i in range(1, n + 1):
        m += '\t-rm -f tmp{0}.dif tmp1 tmp2 tmp tmp.vec1 tmp.vec\n'.format(i)
        m += '\t-subgroup {0} tmp.grp tmp{0}.tbl\n'.format(i)
        m += '\t-difmod -o tmp{0}.dif ../diff/diff.txt tmp{0}.tbl\n'.format(i)
        m += '\t-cluster -wa -c -N .5 -r 50 -o tmp1 tmp{}.dif\n'.format(i)
        m += '\t-cluster -ga -c -N .5 -r 50 -o tmp2 tmp{}.dif\n'.format(i)
        m += '\t-difsum -a -o tmp tmp1 tmp2\n'
        m += '\t-mds -o tmp.vec1 3 tmp\n'
        m += '\t-PYTHONPATH={} ; {} {}util/recolor -m tmp.vec1 tmp.vec\n'.format(u.config.python2path,
                                                                                u.config.python2,
                                                                                u.config.appdir)
        m += '\t-maprgb -r -o ccc_{0}_{1}.eps ../map/map.cfg tmp.vec || rm -f ccc_{0}_{1}.eps\n'.format(n, i)
        m += '\t-{} {}util/smappost ccc_{}_{}.eps\n'.format(u.config.python3, u.config.appdir, n, i)
    m += '\teps2png\n\trm -f tmp*\n\ttouch DONE{}\n\ttouch OK\n'.format(n)
    u.queue.enqueue(path + '/cccmaps', m)
    u.queue.run()
    time.sleep(2)

fp = open('current', 'wt')
fp.write('{}\n'.format(n))
fp.close()
sys.stdout.write('Location: goto?p={}-cccmaps\n\n'.format(path))
