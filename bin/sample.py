#!/usr/bin/env python
"""
--documentation--
"""

__author__ = "Peter Kleiweg"
__version__ = "0.1"
__date__ = "2010/04/27"

#| imports

import cgitb; cgitb.enable(format="html")

import os, random, re, sys, unicodedata

import u.html, u.path, u.distribute
from u.login import username

#| globals

#| functions

def toChar(m):
    return '{:c}'.format(int(m.group(1)))

#| main

u.html.loginCheck()
u.path.chdir(username)

p, num = [int(x) for x in os.environ['QUERY_STRING'].split('-')]
os.chdir('project_{}/data/_'.format(p))

if num > 32 and num < 127:
    t = u.html.escape('{:c}'.format(num))
else:
    t = 'u{:04X}'.format(num)

h2 = unicodedata.name('{:c}'.format(num), '')
if h2:
    h2 = '<h3>' + h2 + '</h3>'

sys.stdout.write('''Content-type: text/html; charset=utf-8
Cache-Control: no-cache
Pragma: no-cache

<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.01 Transitional//EN" "http://www.w3.org/TR/html4/loose.dtd">
<html>
  <head>
    <title>map and samples for {0}</title>
    <style type="text/css">
    <!--
    body {{
        margin: 2em 4em;
        background-color: #ffffff;
        color: #000000;
    }}
    .sample {{
      font-size: x-large;
      margin: 1em 0px .2em 0px;
      font-family: "Doulos SIL", serif;
    }}
    .p {{ color: blue; }}
    .q {{ color: red; }}
    .tokens {{
        font-size: small;
    }}
    .hex {{

    }}
    body.show a.show,
    body.hide a.hide {{
      display: none;
      visibility: hidden;
    }}
    body.hide a.show,
    body.show a.hide {{
        padding: .4em .6em;
        border: 1px solid #808080;
        text-decoration: none;
        color: black;
    }}
    a.show:hover, a.hide:hover {{
        background-color: #c0c0FF;
    }}

    body.hide .tokens,
    body.hide a.hide {{
      display: none;
      visibility: hidden;
    }}
    body.hide a.show {{
      display: inline;
      visibility: visible;
    }}

    body.show a.show {{
      display: none;
      visibility: hidden;
    }}
    body.show a.hide {{
      display: inline;
      visibility: visible;
    }}
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
    <script language="JavaScript"><!--
    function show() {{
      document.getElementById('body').className = 'show';
    }}
    function hide() {{
      document.getElementById('body').className = 'hide';
    }}
    //--></script>
    <script type="text/javascript" src="../tip.js"></script>
  </head>
  <body class="hide" id="body">
  <h1>map and samples for {0}</h1>
  {1}
'''.format(t, h2))

if os.access('../../map/image.html', os.F_OK):
    fp = open('../../map/image.html', 'rt', encoding='utf-8')
    sys.stdout.write(fp.read())
    fp.close()

token = '{:c}'.format(num)
items = []
placen = {}
placeall = {}
for filename in os.listdir('.'):
    if not filename[-5:] == '.data':
        continue
    word = re.sub(r'_([0-9]+)_', toChar, filename[:-5])
    enc = 'iso-8859-1'
    place = ''
    fp = open(filename, 'rb')
    for line in fp:
        if line.startswith(b'%utf8'):
            enc = 'utf-8'
        elif line[:1] == b':':
            place = line[1:].strip().decode('iso-8859-1')
            if not place in placen:
                placen[place] = 0.0
                placeall[place] = 0.0
        elif line[:1] == b'-':
            v = line[1:].strip().decode(enc)
            if v.find(token) > -1:
                items.append((place, word, v))
                placen[place] += 1
            placeall[place] += 1
    fp.close()

if len(items):
    os.chdir('../..')
    u.distribute.distmap(placen, placeall, imgpath='project_{}'.format(p))

random.shuffle(items)

mx = len(items)
s = 'all'
if mx > 200:
    mx = 200
    s = mx
sys.stdout.write('found {} items, showing {}'.format(len(items), s))

sys.stdout.write('''
<p>
<a href="javascript:show()" class="show">show codes</a>
<a href="javascript:hide()" class="hide">hide codes</a>
<p>
''')



tok = u.html.escape(token)
for place, word, v in items[:mx]:
    idx = v.find(token)
    p = v[:idx]
    q = v[idx+1:]
    sys.stdout.write('''
    <div class="sample">
    <span class="p">{}</span><span class="t">{}</span><span class="q">{}</span>
    </div>
    '''.format(u.html.escape(p), tok, u.html.escape(q)))
    sys.stdout.write('<div class="tokens"><span class="p">')
    for c in p:
        if c >= '!' and c <= '~':
            sys.stdout.write(u.html.escape(c) + '\n')
        else:
            sys.stdout.write('<span class="hex">{:04X}</span> '.format(ord(c)))
    sys.stdout.write('</span><span class="t">')
    if token >= '!' and token <= '~':
        sys.stdout.write(tok + '\n')
    else:
        sys.stdout.write('<span class="hex">{:04X}</span> '.format(ord(tok)))
    sys.stdout.write('</span><span class="q">')
    for c in q:
        if c >= '!' and c <= '~':
            sys.stdout.write(u.html.escape(c) + ' ')
        else:
            sys.stdout.write('<span class="hex">{:04X}</span> '.format(ord(c)))
    sys.stdout.write('</span></div>\n')

    sys.stdout.write('''
    <div class="src">
    {} &mdash; {}
    </div>
    '''.format(u.html.escape(place).replace('&amp;#', '&#'), u.html.escape(word)))


sys.stdout.write('  </body>\n</html>\n')
