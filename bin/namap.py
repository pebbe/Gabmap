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

import os, re, sys

import u.html, u.path, u.distribute
from u.login import username


#| globals

#| functions

def unquote(s):
    s = s.strip()
    if len(s) < 2:
        return s
    if s[0] != '"' or s[-1] != '"':
        return s
    return re.sub(r'\\(.)', r'\1', s[1:-1]).strip()

#| main

u.html.loginCheck()
u.path.chdir(username)

p, num = [int(x) for x in os.environ['QUERY_STRING'].split('-')]
os.chdir('project_{}/data'.format(p))

fp = open('NAs.txt', 'rt', encoding='utf-8')
lines = fp.readlines()
fp.close()
item = lines[num].split('\t')[1].strip()

sys.stdout.write('''Content-type: text/html; charset=utf-8
Cache-Control: no-cache
Pragma: no-cache

<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.01 Transitional//EN" "http://www.w3.org/TR/html4/loose.dtd">
<html>
  <head>
    <title>map of missing values for: {0}</title>
    <style type="text/css">
    <!--
    body {{
        margin: 2em 4em;
        background-color: #ffffff;
        color: #000000;
    }}
    .t0, .t1, .t2, .t3 {{
        margin: 1px 1em 1px 0px;
        border: 1px solid #000000;
        padding: .2em 3em;
    }}
    .t0 {{ background-color: #ffffff; }}
    .t1 {{ background-color: #e60000; }}
    .tip {{
      display: block;
      /* font: 14px Courier,fixed; */
      border: solid 1px #000000;
      padding: .3em 2em;
      position: absolute;
      z-index: 100;
      visibility: hidden;
      color: #000000;
      top: 20px;
      left: 90px;
      background-color: #ffffc0;
      layer-background-color: #e8e8e8;
    }}
    -->
    </style>
    <script type="text/javascript" src="../tip.js"></script>
  </head>
  <body class="hide" id="body">
  <h1>map of missing values for: {0}</h1>
'''.format(u.html.escape(item)))

if os.access('../map/image.html', os.F_OK):
    fp = open('../map/image.html', 'rt', encoding='utf-8')
    sys.stdout.write(fp.read())
    fp.close()


placeall = {}
placen = {}

fp = open('table.txt', 'rt', encoding='iso-8859-1')
fp.readline()
for line in fp:
    i = line.split('\t')
    lbl = unquote(i[0])
    placeall[lbl] = 5
    if i[num + 1] == 'NA':
        placen[lbl] = 3
    else:
        placen[lbl] = 0;

os.chdir('..')
u.distribute.distmap(placen, placeall, normalise=False, red=True, imgpath='project_{}'.format(p))

sys.stdout.write('''
<p>
<span class="t0">&nbsp;</span> Value available
<p>
<span class="t1">&nbsp;</span> Missing value

</body>
</html>
''')
