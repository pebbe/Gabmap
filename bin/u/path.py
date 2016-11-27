#!/usr/bin/env python
"""
--documentation--
"""

__author__ = "Peter Kleiweg"
__version__ = "0.1"
__date__ = "2010/02/18"

#| imports

import os, re

import u.config as _c

#| globals

#| functions

def chdir(path):
    os.chdir(_c.datadir)
    for p in path.split('-'):
        assert _c.usermode == 'single' or re.match(r'[a-z][a-z0-9_]*$', p)
        os.chdir(p)

def breadcrumbs(path):
    path = path.split('-')
    try:
        fp = open('{}{}/{}/description'.format(_c.datadir, path[0], path[1]), 'rt', encoding='utf-8')
        title = fp.readline().strip()
        fp.close()
    except:
        title = ''

    return '''
    <div id="crumbs">
    <a href="{}bin/goto?p={}">{}</a> &mdash; {}
    </div>
    '''.format(_c.appurl, path[1], path[1].replace('_', ' '), title)

#| main




#| if main
if __name__ == "__main__":
    pass

