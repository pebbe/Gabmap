#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
--documentation--
"""

__author__ = "Peter Kleiweg"
__version__ = "0.1"
__date__ = "2010/10/23"

#| imports

import cgitb; cgitb.enable(format="html")

import os, sys

import u.html, u.path
from u.login import username


#| main

u.html.loginCheck()
u.path.chdir(username)

p, num = [int(x) for x in os.environ['QUERY_STRING'].split('-')]
os.chdir('project_{}/align'.format(p))

fp = open('page', 'wt')
fp.write('{}\n'.format(num))
fp.close()

sys.stdout.write('Location: goto?p=project_{}-align\n\n'.format(p))
