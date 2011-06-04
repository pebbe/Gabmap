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

def xmlescape(m):
    return '_{}_'.format(ord(m.group()))

def fname(s):
    s = re.sub(r'[^-+a-zA-Z0-9]', xmlescape, s)
    return s + '.data'

#| main

u.html.loginCheck()
u.path.chdir(username)

p, num, ftr = [int(x) for x in os.environ['QUERY_STRING'].split('-')]
os.chdir('project_{}/data/_'.format(p))

method = open('../Method', 'rt').read().strip()
if method.startswith('levfeat'):
    i = 2
else:
    i = 1

fp = open('../../items/list2.utxt', 'rt', encoding='utf-8')
lines = fp.readlines()
fp.close()
item = lines[num].split(None, i)[i].strip()
itemfile = fname(item)
if ftr:
    itemfile += '.ftr'

sys.stdout.write('''Content-type: text/html; charset=utf-8
Cache-Control: no-cache
Pragma: no-cache

<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.01 Transitional//EN" "http://www.w3.org/TR/html4/loose.dtd">
<html>
  <head>
    <title>data map for: {0}</title>
    <style type="text/css">
    <!--
    body {{
        margin: 2em 4em;
        background-color: #ffffff;
        color: #000000;
    }}
    .t0, .t1, .t2, .t3 {{
        margin: 1px 1em 1px 0px;
        border: 1px solid #c0c0c0;
        padding: .2em 3em;
    }}
    .t0 {{ background-color: #ffffff; }}
    .t1 {{ background-color: #54bfc1; }}
    .t2 {{ background-color: #215fad; }}
    .t3 {{ background-color: #081d5b; }}
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
  <h1>data map for: {0}</h1>
'''.format(u.html.escape(item)))

if os.access('../../map/image.html', os.F_OK):
    fp = open('../../map/image.html', 'rt', encoding='utf-8')
    sys.stdout.write(fp.read())
    fp.close()

placen = {}
placeall = {}

fp = open('../labels.txt', 'rt', encoding='iso-8859-1')
for line in fp:
    lbl = line.split(None, 1)[1].strip()
    placen[lbl] = 0
    placeall[lbl] = 4

fp = open(itemfile, 'rb')
for line in fp:
    if line[:1] == b':':
        place = line.decode('iso-8859-1')[1:].strip()
    elif line[:1] == b'-' or line[:1] == b'+':
        if placen[place] == 0:
            placen[place] = 2
        elif placen[place] < 4:
            placen[place] += 1
fp.close()

os.chdir('../..')
u.distribute.distmap(placen, placeall, normalise=False, imgpath='project_{}'.format(p))

sys.stdout.write('''
<p>
<span class="t0">&nbsp;</span> 0 instances
<p>
<span class="t1">&nbsp;</span> 1 instance
<p>
<span class="t2">&nbsp;</span> 2 instances
<p>
<span class="t3">&nbsp;</span> 3 instances or more

</body>
</html>
''')
