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

p, num = os.environ['QUERY_STRING'].split('-', 1)
p = int(p)
os.chdir('project_{}/data/_'.format(p))

nums = num.split('-')

sys.stdout.write('''Content-type: text/html; charset=utf-8
Cache-Control: no-cache
Pragma: no-cache

<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.01 Transitional//EN" "http://www.w3.org/TR/html4/loose.dtd">
<html>
  <head>
    <title>map and samples for substring</title>
    <style type="text/css">
    <!--
    body {
        margin: 2em 4em;
    }
    .sample {
      font-size: x-large;
      margin: 1em 0px .2em 0px;
      font-family: "Doulos SIL", serif;
    }
    .p { color: blue; }
    .q { color: red; }
    .tokens {
        font-size: small;
    }
    .hex {

    }
    body.show a.show,
    body.hide a.hide {
      display: none;
      visibility: hidden;      
    }
    body.hide a.show,
    body.show a.hide {
        padding: .4em .6em;
        border: 1px solid #808080;
        text-decoration: none;
        color: black;
    }
    a.show:hover, a.hide:hover {
        background-color: #c0c0FF;
    }

    body.hide .tokens, 
    body.hide a.hide {
      display: none;
      visibility: hidden;      
    }
    body.hide a.show {
      display: inline;
      visibility: visible;
    }

    body.show a.show {
      display: none;
      visibility: hidden;      
    }
    body.show a.hide {
      display: inline;
      visibility: visible;
    }
    .tip {
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
    }
    -->
    </style>
    <script language="JavaScript"><!--
    function show() {
      document.getElementById('body').className = 'show';
    }
    function hide() {
      document.getElementById('body').className = 'hide';
    }
    //--></script>
    <script type="text/javascript" src="../tip.js"></script>
  </head>
  <body class="hide" id="body">
  <h1>map and samples for substring</h1>
''')

if os.access('../../map/image.html', os.F_OK):
    fp = open('../../map/image.html', 'rt', encoding='utf-8')
    sys.stdout.write(fp.read())
    fp.close()

tokens = ''.join(['{:c}'.format(int(num)) for num in nums])
if os.access('../UTF', os.F_OK):
    enc = 'utf-8'
else:
    enc = 'iso-8859-1'
items = []
placen = {}
placeall = {}
for filename in os.listdir('.'):
    if not filename[-5:] == '.data':
        continue
    word = re.sub(r'_([0-9]+)_', toChar, filename[:-5])
    place = ''
    fp = open(filename, 'rb')
    for line in fp:
        if line[:1] == b':':
            place = line[1:].decode('iso-8859-1').strip()
            if not place in placen:
                placen[place] = 0.0
                placeall[place] = 0.0
        elif line[:1] == b'-':
            v = line[1:].decode(enc).strip()
            a, b, c = v.partition(tokens)
            if b:
                items.append((place, word, a, b, c))
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

tok = u.html.escape(tokens)
for place, word, aa, bb, cc in items[:mx]:
    sys.stdout.write('''
    <div class="sample">
    <span class="p">{}</span><span class="t">{}</span><span class="q">{}</span>
    </div>
    '''.format(u.html.escape(aa), tok, u.html.escape(cc)))
    sys.stdout.write('<div class="tokens"><span class="p">')
    for c in aa:
        if c >= '!' and c <= '~':
            sys.stdout.write(u.html.escape(c) + '\n')
        else:
            sys.stdout.write('<span class="hex">{:04X}</span> '.format(ord(c)))
    sys.stdout.write('</span><span class="t">')

    for c in bb:
        if c >= '!' and c <= '~':
            sys.stdout.write(u.html.escape(c) + '\n')
        else:
            sys.stdout.write('<span class="hex">{:04X}</span> '.format(ord(c)))

    sys.stdout.write('</span><span class="q">')
    for c in cc:
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
