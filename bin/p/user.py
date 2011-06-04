#!/usr/bin/env python

"""
--documentation--
"""

__author__ = "Peter Kleiweg"
__version__ = "0.1"
__date__ = "2010/01/29"

#| imports

import os, re, sys

import p.project
import u.config as _c
import u.html as _h
import u.path as _p

#| globals

#| functions

def _split(s):
    m = re.match(r'(.*?)([0-9]+)$', s)
    return (m.group(1), int(m.group(2)))

def makepage(user):

    _p.chdir(user)

    projects, count = p.project.getProjects()

    if user.startswith('demo'):
        template = 'p-user-demo.html'
    elif count >= _c.maxprojects:
        template = 'p-user-full.html'
    else:
        template = 'p-user.html'

    sys.stdout.write(_h.head())
    sys.stdout.write(_h.getBody(template).format({
        'projects':projects,
        'username':user,
        'appurl':_c.appurl,
        'count':_c.maxprojects,
        'helpmap': _h.help('homemap'),
        'helpshmap': _h.help('homedisperse'),
        'helppseudo': _h.help('homepseudo'),
        'helpdata': _h.help('homedata'),
        'helptype': _h.help('hometype'),
        'helpdatatype': _h.help('homedatatype'),
        'helpmtdstring': _h.help('homemtdstring'),
        'helpmtdnum': _h.help('homemtdnum'),
        'helpmtdbin': _h.help('homemtdbin'),
        'helpuserdef': _h.help('homeuserdef'),
        'helpremove':_h.help('homeremove'),
        'helpadvca':_h.help('homeca'),
        }))
    sys.stdout.write(_h.foot())
