#!/usr/bin/env python
"""
--documentation--
"""

__author__ = "Peter Kleiweg"
__version__ = "0.1"
__date__ = "2010/02/05"

#| imports

import cgitb; cgitb.enable(format="html")

import cgi, re, sys

import u.html, u.config, u.queue
from u.login import username

#| globals

#| functions

def getval(field):
    return re.sub(r'\s+', ' ', form.getvalue(field, '')).strip()

#| main

u.html.loginCheck()

u.queue.run()

form = cgi.FieldStorage()

path = getval('p')

if not path:
    sys.stdout.write('Location: home\n\n')
    sys.exit()

path = username + '-' + path
p0 = path.split('-')[-1]

if p0.startswith('project'):
    import p.project
    p.project.makepage(path)
elif p0.startswith('map'):
    import p.map
    p.map.makepage(path)
elif p0.startswith('items'):
    import p.items
    p.items.makepage(path)
elif p0.startswith('numitems'):
    import p.numitems
    p.numitems.makepage(path)
elif p0.startswith('data'):
    import p.data
    p.data.makepage(path)
elif p0.startswith('numdata'):
    import p.numdata
    p.numdata.makepage(path)
elif p0.startswith('difdata'):
    import p.difdata
    p.difdata.makepage(path)
elif p0.startswith('align'):
    import p.align
    p.align.makepage(path)
elif p0.startswith('distmap'):
    import p.distmap
    p.distmap.makepage(path)
elif p0.startswith('nummap'):
    import p.nummap
    p.nummap.makepage(path)
elif p0.startswith('diff'):
    import p.diff
    p.diff.makepage(path)
elif p0.startswith('mdsplots'):
    import p.mdsplots
    p.mdsplots.makepage(path)
elif p0.startswith('mdsmaps'):
    import p.mdsmaps
    p.mdsmaps.makepage(path)
elif p0.startswith('cccmaps'):
    import p.cccmaps
    p.cccmaps.makepage(path)
elif p0.startswith('clusters'):
    import p.clusters
    p.clusters.makepage(path)
elif p0.startswith('clumaps'):
    import p.clumaps
    p.clumaps.makepage(path)
elif p0.startswith('cludet'):
    import p.cludet
    p.cludet.makepage(path)
elif p0.startswith('prob'):
    import p.prob
    p.prob.makepage(path)
elif p0.startswith('plot'):
    import p.plot
    p.plot.makepage(path)
elif p0.startswith('refmaps'):
    import p.refmaps
    p.refmaps.makepage(path)
else:
    u.html.exitMessage('Error', 'Invalid path')


#| if main
if __name__ == "__main__":
    pass


