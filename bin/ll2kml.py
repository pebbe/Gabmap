#!/usr/bin/env python3
"""
--documentation--
"""

__author__ = "Peter Kleiweg"
__version__ = "0.1"
__date__ = "2010/05/02"

#| imports

import cgitb; cgitb.enable(format="html")

import codecs, os, re, sys

import u.myCgi, u.hebci

#| functions

def escape(s):
    return s.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;').replace('"', '&quot;')

#| main

assert sys.stdout.encoding.lower() == 'utf-8'

data = u.myCgi.data.get('file', '')
if data:
    if data.startswith(codecs.BOM_UTF8):
        enc = 'utf-8-sig'
    elif data.startswith(codecs.BOM_UTF16_BE) or data.startswith(codecs.BOM_UTF16_LE):
        enc = 'utf-16'
    elif re.match(br'[\x00-\x7F]*$', data):
        enc = 'us-ascii'
    elif re.match(br'([\x00-\x7F]|[\xC0-\xDF][\x80-\xBF]|[\xE0-\xEF][\x80-\xBF]{2}|[\xF0-\xF7][\x80-\xBF]{3}|[\xF8-\xFB][\x80-\xBF]{4}|[\xFC-\xFD][\x80-\xBF]{5})*$', data):
        enc = 'utf-8'
    else:
        enc = 'iso-8859-1'  # fall-back
    data = data.decode(enc)
else:
    cp = u.hebci.cp(u.myCgi.data)
    data = u.myCgi.data.get('text', '').decode(cp)

items = []

j = len(data)
splitter = '\n'
for sp in ['\n\r', '\n', '\r\n', '\r']:
    i = data.find(sp)
    if i >= 0 and i < j:
        splitter = sp
        j = i

for line in data.split(splitter):
    line = line.strip()
    if not line or line[0] == '#':
        continue
    longitude, latitude, placename = line.split(None, 2)
    longitude = float(longitude)
    latitude = float(latitude)
    assert -180.0 <= longitude <= 180.0
    assert -90.0 <= latitude <= 90.0
    items.append((longitude, latitude, placename))

if not items:
    sys.stdout.write('Content-type: text/plain\n\nNo items found\n')
    sys.exit()

sys.stdout.write('''Content-type: application/vnd.google-earth.kml+xml; charset=utf-8
Content-Disposition: attachment; filename="nameless.kml"

<?xml version="1.0" encoding="UTF-8"?>
<kml xmlns="http://earth.google.com/kml/2.2">
  <Document>
    <name>nameless</name>
''')

for x, y, p in items:
    sys.stdout.write('''    <Placemark>
      <name>{}</name>
      <Point>
        <coordinates>{},{},0</coordinates>
      </Point>
    </Placemark>
'''.format(escape(p), x, y))

sys.stdout.write('  </Document>\n</kml>\n')

