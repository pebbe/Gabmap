#!/usr/bin/env python
"""

"""

__author__ = "Peter Kleiweg"
__version__ = "0.99"
__date__ = "2010/03/10"

#| imports

import cgitb; cgitb.enable(format="html")

import codecs, cgi, glob, math, os, re, stat, sys, tempfile, time, urllib.request, zipfile

import xml.etree.cElementTree as ET

from pyproj import Geod, Proj

import p.project
import u.html, u.path, u.myCgi, u.config, u.queue, u.setChar

#| globals

mapname = ''
places = []
polygons = []
lines = []

externals = []

mapplaces = {}
dataplaces = {}

mapcfg = """# Example configuration file for the programs 'mapclust', 'mapdiff', 'maplink', 'mapmap', 'maprgb', and 'mapvec'

# Filenames, the first three are required
transform: {0[curpath]}/map.trn
labels: {0[curpath]}/map.lbl
coordinates: {0[curpath]}/map.coo
clipping: {0[curpath]}/map.clp
map: {0[curpath]}/map.map
othermarkers: {0[curpath]}/map.ex

# Background colour for areas without data, red green and blue value
backrgb: .9 .9 .9

# Aspect ratio between X and Y, must be 1 or greater
aspect: 1

# Type of markers to put at locations
# Any number of: dot label number poly
# You shouldn't mix dot and number
markers:

# What to do with locations without data, one of: ignore preserve
missing: preserve

# How far to extend filling beyond extreme data points,
# as a fraction of distance between extreme data points
fillmargin: .5

# Radius for filling if file for clipping is missing
limit: 50

# Use limit, even if file for clipping is not missing: yes or no
uselimit: yes

### PostScript options
boundingbox: {0[bbox]}
fontname: Helvetica
fontmatrix: [ 10 0 0 10 0 0 ]
pslevel: 2
# one of: fill eofill
fillstyle: eofill

# Markers dot and label
# Size of black dot
radius: 2.5
# Width of white line around black dot
white: 1
# Horizontal distance of label from center of location, for dx = 1 or dx = -1
xgap: 4
# Vertical distance of label from center of location, for dy = 1 or dy = -1
ygap: 4

# Line width in polygons
linewidth: .5

### Options for 'mapclust' and 'maprgb'
islandr: 10
islandlw: 1

### Options for 'mapclust' and 'mapdiff'

# Width of lines between clusters
borderwidth: 3

### Options for 'mapclust' only

# Colour of lines between clusters, red green and blue value
borderrgb: 0 0 1

# Size of symbols
symbolsize: 5
# Line width in symbols
symbollinewidth: .3
"""

#| functions

def polyfix(s):
    return re.sub(r'![\r\n]+ ', '', s)

def xmlescape(m):
    return '_{}_'.format(ord(m.group()))

def fname(s):
    s = re.sub(r'[^-+a-zA-Z0-9]', xmlescape, s)
    return s + '.data'

def latin1(s):
    if s:
        if s[0] == '#':
            s = '&#35;' + s[1:]
        return s.encode('iso-8859-1', 'xmlcharrefreplace').decode('iso-8859-1')
    else:
        return ''

def ascii(s):
    if not s:
        return ''
    return s.encode('us-ascii', 'replace').decode('us-ascii')

def quote(s):
    return '"' + s.strip().replace('\\', '\\\\').replace('"', '\\"') + '"'

def sstrip(s):
    try:
        s2 = s.strip()
    except:
        s2 = s
    return s2

def readkmlfile(filename):
    global mapname, places, polygons, lines, externals

    try:
        tree = ET.parse(filename)
    except:
        u.html.exitMessage('Error', 'This file is not valid XML')

    ns = tree.getroot().tag
    if ns[0] != '{' or ns[-4:] != '}kml':
        u.html.exitMessage('Error', 'Invalid name space in {}<br>This is not valid KML'.format(cgi.escape(ns)))
    ns = ns[1:-4]

    if not mapname:
        mapname = sstrip(tree.findtext('.//{{{0[ns]}}}Folder/{{{0[ns]}}}name'.format(vars())))

    for pm in tree.findall('.//{{{0[ns]}}}Placemark'.format(vars())):
        name = sstrip(pm.findtext('./{{{0[ns]}}}name'.format(vars())))

        coo = sstrip(pm.findtext('./{{{0[ns]}}}Point/{{{0[ns]}}}coordinates'.format(vars())))
        if coo:
            c = coo.split(',')
            lng = float(c[0])
            lat = float(c[1])
            lngrad = lng / 180.0 * math.pi
            latrad = lat / 180.0 * math.pi
            xx = math.cos (lngrad) * math.cos (latrad);
            yy = math.sin (lngrad) * math.cos (latrad);
            zz = math.sin (latrad);
            places.append((name, lng, lat, xx, yy, zz))
            if not name in mapplaces:
                mapplaces[name] = 0
            mapplaces[name] += 1

        for ob in pm.findall('.//{%(ns)s}Polygon/{%(ns)s}outerBoundaryIs' % vars()):
            coo = sstrip(ob.findtext('./{%(ns)s}LinearRing/{%(ns)s}coordinates' % vars()))
            if coo:
                polygons.append((name, polyfix(coo)))

        for ib in pm.findall('./{{{0[ns]}}}Polygon/{{{0[ns]}}}innerBoundaryIs'.format(vars())):
             coo = sstrip(ib.findtext('./{{{0[ns]}}}LinearRing/{{{0[ns]}}}coordinates'.format(vars())))
             if coo:
                 polygons.append((name + ' [inner boundary]', polyfix(coo)))

        for ls in pm.findall('.//{%(ns)s}LineString' % vars()):
            coo = sstrip(ls.findtext('./{%(ns)s}coordinates' % vars()))
            if coo:
                lines.append((name, polyfix(coo)))

    for nl in tree.findall('.//{{{0[ns]}}}NetworkLink/{{{0[ns]}}}Link'.format(vars())):
        externals.append(sstrip(nl.findtext('./{{{0[ns]}}}href'.format(vars()))))


#| main

#|| user logged in?

u.html.loginCheck()
u.path.chdir(u.login.username)

if u.login.username.startswith('demo'):
    u.html.exitMessage('Error', 'You cannot create your own project in a demo account.')

#|| make project

p.project.cleanup()

description = u.myCgi.data.get('description', b'').decode('utf-8')
if not description:
    u.html.exitMessage('Error', 'No description given')

pseudo = False
if u.myCgi.data.get('pseudo', None):
    pseudo = True

if not pseudo:
    mapdata = u.myCgi.data.get('map', None)
    if not mapdata:
        u.html.exitMessage('Error', "Missing or empty map file")

data = u.myCgi.data.get('data', '')
if not data:
    u.html.exitMessage('Error', 'Missing or empty data file')

method = u.myCgi.data.get('allmethod', b'-').decode('us-ascii')
if method == '-':
    u.html.exitMessage('Error', 'No method selected')

mx = 0
filenames = [int(x.split('_')[1]) for x in os.listdir('.') if x.startswith('project')]
if filenames:
    mx = max(filenames)
path = 'project_{}'.format(mx + 1)
os.mkdir(path)
os.chdir(path)
fp = open('description', 'wt', encoding='utf-8')
fp.write(u.html.escape(description) + '\n')
fp.close()

#|| do the map

try:
    os.mkdir('map')
except:
    pass

if pseudo:
    open('map/PSEUDOMAP', 'wt').close()
else:
    os.chdir('map')
    assert not os.access('OK', os.F_OK)
    for filename in os.listdir('.'):
        os.remove(filename)

    curpath = os.getcwd()

    fp = open('datafile', 'wb')
    fp.write(mapdata)
    fp.close()

    #|| read kml/kmz files

    fd, tmpname = tempfile.mkstemp()
    os.close(fd)
    fd, tmpname2 = tempfile.mkstemp()
    os.close(fd)
    try:

        if zipfile.is_zipfile('datafile'):
            zp = zipfile.ZipFile('datafile', 'r')
            for zf in zp.namelist():
                fp = open(tmpname, 'wb')
                fp.write(zp.read(zf))
                fp.close()
                readkmlfile(tmpname)
            zp.close()
        else:
            readkmlfile('datafile')

        extdone = {}
        while externals:
            external = externals.pop(0)

            # prevent multiple includes of same source
            if external in extdone:
                continue
            extdone[external] = True

            url = urllib.request.URLopener()
            fp = url.open(external)
            d = fp.read()
            fp.close()
            url.close()

            fp = open(tmpname2, 'wb')
            fp.write(d)
            fp.close()

            if zipfile.is_zipfile(tmpname2):
                zp = zipfile.ZipFile(tmpname2, 'r')
                for zf in zp.namelist():
                    fp = open(tmpname, 'wb')
                    fp.write(zp.read(zf))
                    fp.close()
                    readkmlfile(tmpname)
                zp.close()
            else:
                readkmlfile(tmpname2)

    finally:
        os.remove(tmpname)
        os.remove(tmpname2)
        if zipfile.is_zipfile('datafile'):
            os.rename('datafile', 'map.kmz')
        else:
            os.rename('datafile', 'map.kml')

    #|| check input

    if len(places) == 0:
        u.html.exitMessage('Error', "No placemarks found")

    if '' in mapplaces:
        u.html.exitMessage('Error', 'Empty placemark label(s)')

    errs = ''
    for p in mapplaces:
        if mapplaces[p] > 1:
            errs += '<br>{}'.format(cgi.escape(p))
    if errs:
        u.html.exitMessage('Error', 'Placemark label(s) used more than once:' + errs)

    if len(polygons) == 0:
        u.html.exitMessage('Error', "No polygons found")

    if not mapname:
        mapname = 'untitled'

    #||| isn't the map too complex?

    n = 0
    for name, polygon in polygons:
        n += len(polygon.split())
    for name, line in lines:
        n += len(line.split())

    m = 10000
    if n > m:
        u.html.exitMessage('Error', '''
        The map is too complex.
        <p>
        There are {} points in polygons and lines.<br>
        There are {} points allowed.<br>
        Please simplify your map, and try again.
        '''.format(n, m))

    #|| find average place coordinates

    x = 0.0
    y = 0.0
    z = 0.0
    for n, lng, lat, xx, yy, zz in places:
        x += xx
        y += yy
        z += zz
    lng = math.atan2(y, x) / math.pi * 180.0
    r = math.sqrt(x * x + y * y)
    lat = math.atan2(z, r) / math.pi * 180.0

    #|| choose UTM zone

    if lat < -80.0 or lat > 84.0:
        u.html.exitMessage('Error', "Arctic and antarctic region are not supported")

    xzone = 1 + int((lng + 180.0) / 6.0)

    if lat > 72.0 and lng > 0.0 and lng < 42.0:
        if lng < 9.0:
            xzone = 31
        elif lng < 21.0:
            xzone = 33
        elif lng < 33.0:
            xzone = 35
        else:
            xzone = 37

    if lat > 56.0 and lat < 64.0 and lng > 3.0 and lng < 12.0:
        xzone = 32

    yzone = 'CDEFGHJKLMNPQRSTUVWXX'[int((lat + 80.0) / 8.0)]

    p = Proj(proj = 'utm', zone = xzone, ellps='WGS84')

    pstring = 'Projection: UTM {}{} (WGS84)'.format(xzone, yzone)

    #|| enough places?

    place, lng, lat, xx, yy, zz = places[0]
    x1, y1 = p(lng, lat)
    x2 = x1
    y2 = y1
    for place, lng, lat, xx, yy, zz in places[1:]:
        x, y = p(lng, lat)
        if x < x1: x1 = x
        if x > x2: x2 = x
        if y < y1: y1 = y
        if y > y2: y2 = y
    if x2 - x1 < 1 or y2 - y1 < 1:
        u.html.exitMessage('Error', "Not enough placemarks")

    #|| limit for (near-)identical locations

    limit = math.sqrt((x2 - x1) * (x2 - x1) + (y2 - y1) * (y2 - y1)) * 0.00005

    #|| write label file

    fp = open('map.lbl', 'wt', encoding='iso-8859-1')
    n = 1
    for place, lng, lat, xx, yy, zz in places:
        fp.write('{:4d}\t{}\n'.format(n, quote(latin1(place))))
        n += 1
    fp.close()

    #|| write coordinate file

    xyplaces = []
    fp = open('map.coo', 'wt', encoding='iso-8859-1')
    fp.write('# {}\n'.format(pstring))
    for place, lng, lat, xx, yy, zz in places:
        x, y = p(lng, lat)
        fp.write('{:g}\t{:g}\t1\t0\t{}\n'.format(x, y, quote(latin1(place))))
        xyplaces.append((place, x, y))
    fp.close()

    #|| write exception file

    warnings = []
    skipped = set()
    fp = open('map.ex', 'wt', encoding='iso-8859-1')
    for i in range(len(xyplaces) - 1):
        if i in skipped:
            continue
        for j in range(i + 1, len(xyplaces)):
            if j in skipped:
                continue
            dx = xyplaces[i][1] - xyplaces[j][1]
            dy = xyplaces[i][2] - xyplaces[j][2]
            d = math.sqrt(dx * dx + dy * dy)
            if d < limit:
                skipped.add(j)
                fp.write('-1 {}\n'.format(latin1(xyplaces[j][0])))
                warnings.append('(near-)identical coordinates for "{0}" and "{1}", ignoring "{1}"\n'.format(xyplaces[i][0], xyplaces[j][0]))
    fp.close()
    if warnings:
        fp = open('WARNINGS.txt', 'wt', encoding="utf-8")
        fp.write(''.join(warnings))
        fp.close()

    #|| write file with geo distances

    geod = Geod(ellps='WGS84')
    fp = open('map.geo', 'wt', encoding='iso-8859-1')
    fp.write('# geographic distances in kilometer\n')
    fp.write('{}\n'.format(len(places)))
    for place in places:
        fp.write(latin1(place[0]) + '\n')
    for i in range(len(places)):
        for j in range(i):
            # d = places [i][3] * places [j][3] +  places [i][4] * places [j][4] + places [i][5] * places [j][5]
            # if d < -1.0:
            #     d = -1.0
            # if d > 1.0:
            #     d = 1.0
            # d = math.acos (d) / math.pi * 20000.0;
            d = geod.inv(places [i][1], places [i][2], places [j][1], places [j][2])[2] / 1000.0
            fp.write('{:g}\n'.format(d))
    fp.close()

    #|| write borders file:

    fp = open('R-map.borders', 'wt', encoding='us-ascii')
    fp2 = open('R-map.both', 'wt', encoding='us-ascii')
    fp.write('# {}\n'.format(pstring))
    fp2.write('# {}\n'.format(pstring))
    divider = ''
    for name, polygon in polygons:
        fp.write(divider)
        fp2.write(divider)
        divider = 'NA NA\n'
        fp.write("# begin area: {}\n".format(ascii(name)))
        fp2.write("# begin area: {}\n".format(ascii(name)))
        for coo in polygon.split():
            c = coo.split(',')
            x, y = p(float(c[0]), float(c[1]))
            fp.write('{:g} {:g}\n'.format(x, y))
            fp2.write('{:g} {:g}\n'.format(x, y))
        fp.write("# end area: {}\n".format(ascii(name)))
        fp2.write("# end area: {}\n".format(ascii(name)))
    fp.close()

    #|| write lines file:

    fp = open('R-map.lines', 'wt', encoding='us-ascii')
    fp.write('# {}\n'.format(pstring))
    if lines:
        fp2.write('NA NA\n')
    divider = ''
    for name, line in lines:
        fp.write(divider)
        fp2.write(divider)
        divider = 'NA NA\n'
        fp.write("# begin line: {}\n".format(ascii(name)))
        fp2.write("# begin line: {}\n".format(ascii(name)))
        for coo in line.split():
            c = coo.split(',')
            x, y = p(float(c[0]), float(c[1]))
            fp.write('{:g} {:g}\n'.format(x, y))
            fp2.write('{:g} {:g}\n'.format(x, y))
        fp.write("# end line: {}\n".format(ascii(name)))
        fp2.write("# end line: {}\n".format(ascii(name)))
    fp.close()
    fp2.close()

    #|| do map set-up

    os.system('mapsetup -c R-map.borders -m R-map.both > /dev/null')
    os.rename('out.clp',  'map.clp')
    os.rename('out.map',  'map.map')
    os.rename('out.trn',  'map.trn')

    #|| write configuration file

    bbox = '0 0 595 842'

    fp = open('map.cfg', 'wt', encoding='us-ascii')
    fp.write(mapcfg.format(vars()))
    fp.close()

    # fix BoundingBox

    os.system('mapmap -o Example.eps map.cfg 2> /dev/null')

    fp = os.popen('gs -sDEVICE=bbox -dNOPAUSE -dBATCH -dQUIET Example.eps 2>&1', 'r')
    lines = fp.readlines()
    fp.close()

    for line in lines:
        if line.startswith('%%BoundingBox:'):
            s, x1, y1, x2, y2 = line.split()
            bbox = '{} {} {} {}'.format(int(x1) - 8, int(y1) - 8, int(x2) + 8, int(y2) + 8)

    # rewrite configuration file

    fp = open('map.cfg', 'wt', encoding='us-ascii')
    fp.write(mapcfg.format(vars()))
    fp.close()

    #|| make example map

    os.system('mapmap -o Example.eps map.cfg 2> /dev/null')

    #|| write info files

    fp = open('description', 'wt', encoding='utf-8')
    fp.write('{} \N{EM DASH} {} locations'.format(u.html.escape(mapname), len(places)))
    fp.close()

    os.chdir('..')

################################################################

#|| process data

#||| check data

fp = open('test', 'wb')
fp.write(data)
fp.close()
fp = os.popen('file test 2>&1', 'r')
filetest = fp.read()
fp.close()
os.remove('test')
if re.search('office|excel|spreadsheet', filetest, re.I):
    s = filetest.split(None, 1)[1]
    u.html.exitMessage('Error', '''
    Illegal file format: {}
    <p>
    You need to convert your data to plain text.<br>
    See:
    <a href="http://www.gabmap.nl/~app/doc/preparing/" target="_blank">Preparing dialect data for Gabmap</a>
    '''.format(u.html.escape(s)))

if data.startswith(codecs.BOM_UTF8):
    enc = 'utf-8-sig'
elif data.startswith(codecs.BOM_UTF16_BE) or data.startswith(codecs.BOM_UTF16_LE):
    enc = 'utf-16'
else:
    enc = 'us-ascii'
    if data.find(b'\n') >= 0:
        splitter = b'\n'
    else:
        splitter = b'\r'
    for line in data.split(splitter):
        if enc == 'us-ascii':
            if re.match(br'[\x00-\x7F]*$', line):
                continue
            else:
                enc = 'utf-8'
        if enc == 'utf-8':
            if re.match(br'([\x00-\x7F]|[\xC0-\xDF][\x80-\xBF]|[\xE0-\xEF][\x80-\xBF]{2}|[\xF0-\xF7][\x80-\xBF]{3}|[\xF8-\xFB][\x80-\xBF]{4}|[\xFC-\xFD][\x80-\xBF]{5})*$', line):
                continue
            else:
                enc = 'iso-8859-1'  # fall-back
                break

if enc.startswith('utf') and enc != 'utf-8':
    try:
        data = data.decode(enc).encode('utf-8')
        enc = 'utf-8'
    except:
        u.html.exitMessage('Error', 'Decoding of data failed.')

j = len(data)
for sp in [b'\n\r', b'\n', b'\r\n', b'\r']:
    i = data.find(sp)
    if i >= 0 and i < j:
        splitter = sp
        j = i

comments = []
lines = []
for line in data.split(splitter):
    if line[:1] == b'#':
        comments.append(line.decode(enc).expandtabs().rstrip())
    elif line.strip():
        lines.append(line)
    elif comments:
        comments.append('')
while comments:
    if not comments[-1]:
        comments.pop()
    else:
        break

items = [i.strip() for i in lines[0].decode(enc).split('\t')]
if not items[0]:
    items.pop(0)
nItems = len(items)
nPlaces = len(lines) - 1

if method == 'dif':
    if nItems == 1:
        n = 0
        nPlaces = int(items[0])
        lplaces = []
        for i in range(nPlaces):
            n += 1
            lplaces.append(lines[n].decode(enc).strip())
        data = []
        for i in range(nPlaces):
            s = ['0'] * nPlaces
            data.append(s)
        for i in range(nPlaces):
            for j in range(i):
                n += 1
                data[i][j] = data[j][i] = lines[n].decode(enc).strip()
    else:
        lplaces = []
        data = []
        for line in lines[1:]:
            a = [i.decode(enc).strip() for i in line.split(b'\t')]
            lplaces.append(a[0])
            data.append(a[1:])
        nPlaces = len(lplaces)

        errs = False
        for i in range(nPlaces):
            if errs:
                break
            if len(data[i]) != nPlaces:
                errs = True
                continue
            if data[i][i] != '0':
                errs = True
                continue
            for j in range(i):
                if data[i][j] != data[j][i]:
                    errs = True
                    break
        if errs:
            u.html.exitMessage('Error', 'Difference table is not symmetrical')

    for i in range(nPlaces):
        for j in range(i):
            if data[i][j] != 'NA':
                try:
                    assert float(data[i][j]) >= 0.0
                except:
                    u.html.exitMessage('Error', 'Invalid data for "{}" - "{}"'.format(u.html.escape(lplaces[j]), u.html.escape(lplaces[i])))

else:
    errs = ''
    for i in range(nItems):
        if not items[i]:
            u.html.exitMessage('Error', 'Empty item label(s) in data file')
        for j in range(i):
            if items[i] == items[j]:
                errs += '<br>{}'.format(cgi.escape(items[i]))
    if errs:
        u.html.exitMessage('Error', 'Item label(s) used more than once:' + errs)

    nVars= 0
    nChar = 0
    nChars = {}
    lplaces = []
    data = []
    errs = ''
    for line in lines[1:]:
        a = [i.strip() for i in line.split(b'\t')]
        if len(a) != nItems + 1:
            errs += '<li>row {} &quot;{}&quot; : {} data cells\n'.format(len(data) + 1, u.html.escape(a[0].decode(enc)), len(a) - 1)
        lplaces.append(a[0].decode(enc))
        data.append(a[1:])
    if errs:
        u.html.exitMessage('Error', '''
        Data failure.
        <p>
        There should be {} data cells in each data row (not counting comments and labels),<br>
        but the following data row(s) has/have a different number of data cells:
        <ul>
        {}
        </ul>
        '''.format(nItems, errs))

    errs = ''
    for p in lplaces:
        if not p:
            u.html.exitMessage('Error', 'Empty data place(s)')
        if not p in dataplaces:
            dataplaces[p] = 0
        dataplaces[p] += 1
        if not pseudo and not p in mapplaces:
            errs += '<br>{}'.format(cgi.escape(p))
    if errs:
        u.html.exitMessage('Error', 'Data place(s) not on the map:' + errs)

    errs = ''
    for p in dataplaces:
        if dataplaces[p] > 1:
            errs += '<br>{}'.format(cgi.escape(p))
    if errs:
        u.html.exitMessage('Error', 'Data place(s) used more than once:' + errs)


#||| check data format

if method.startswith('num'):
    NAs = 0
    NAc = [0] * nItems
    for i in range(nItems):
        for j in range(nPlaces):
            dd = data[j][i].decode(enc)
            try:
                if dd == 'NA':
                    NAs += 1
                    NAc[i] += 1
                else:
                    d = float(dd)
            except:
                u.html.exitMessage('Error', 'Missing or illegal data in column "{}", row "{}": "{}"'.format(
                    u.html.escape(items[i]),
                    u.html.escape(latin1(lplaces[j])),
                    u.html.escape(dd)))

#||| write data

try:
    os.mkdir('data')
except:
    pass
os.chdir('data')

assert not os.access('OK', os.F_OK)

if os.access('_', os.F_OK):
    for filename in os.listdir('_'):
        os.remove('_/' + filename)

for filename in os.listdir('.'):
    if filename[0] != '_':
        os.remove(filename)

try:
    if method.startswith('num') or method.startswith('dif'):
        os.rmdir('_')
    else:
        os.mkdir('_')
except:
    pass

if comments:
    fp = open('comments.txt', 'wt', encoding='utf-8')
    for line in comments:
        fp.write(line + '\n')
    fp.close()

n = 0
fp = open('labels.txt', 'wt', encoding='iso-8859-1')
fp2 = open('truelabels.txt', 'wt', encoding='utf-8')
for p in lplaces:
    n += 1
    fp.write('{:4d}\t{}\n'.format(n, latin1(p)))
    fp2.write(p + '\n')
fp2.close()
fp.close()

if method.startswith('num'):
    fp = open('table.txt', 'wt', encoding='iso-8859-1')
    t = ''
    for i in items:
        fp.write(t + quote(latin1(i)))
        t = '\t'
    fp.write('\n')
    for j in range(nPlaces):
        fp.write(quote(latin1(lplaces[j])))
        for i in range(nItems):
            fp.write('\t' + data[j][i].decode(enc))
        fp.write('\n')
    fp.close()
elif not method.startswith('dif'):
    for i in range(nItems):
        fp = open('_/' + fname(items[i]), 'wb')
        if enc.startswith('utf'):
            fp.write(b'%utf8\n')
        for j in range(nPlaces):
            if not data[j][i]:
                continue
            fp.write(b': ' + lplaces[j].encode('iso-8859-1', 'xmlcharrefreplace') + b'\n')
            for k in [re.sub(b'^(/ +)*(.*?)( +/)*$', b'\\2', x.strip()) for x in data[j][i].split(b' / ')]:
                if k:
                    fp.write(b'- ' + k + b'\n')
                    nVars += 1
                    if enc.startswith('utf'):
                        cc = [ord(c) for c in k.decode(enc)]
                    else:
                        cc = k
                    for c in cc:
                        if not c in nChars:
                            nChars[c] = 0
                        nChars[c] += 1
                        nChar += 1
        fp.close()

if method.startswith('num'):
    fp = open('stats.txt', 'wt')
    fp.write('{} {} {}\n'.format(nPlaces, nItems, NAs))
    fp.close()
    fp = open('NAs.txt', 'wt', encoding='utf-8')
    for i in range(nItems):
        fp.write('{}\t{}\n'.format(NAc[i], items[i]))
    fp.close()
elif method.startswith('dif'):
    fp = open('stats.txt', 'wt')
    fp.write('{}\n'.format(nPlaces))
    fp.close()
else:
    fp = open('stats.txt', 'wt')
    fp.write('{} {} {} {}\n'.format(nPlaces, nItems, nVars, nChar))
    fp.close()
    fp = open('charcount.txt', 'wt')
    for i in sorted(nChars):
        fp.write('{}\t{}\n'.format(i, nChars[i]))
    fp.close()

fp = open('Method', 'wt')
fp.write(method + '\n')
fp.close()

if method.startswith('levfeat'):
    if method.endswith('user'):
        featdef = u.myCgi.data.get('featdef', None)
        if not featdef:
            u.html.exitMessage('Error', 'User defined string edit distance is missing')
        if featdef.startswith(codecs.BOM_UTF8):
            featdef = featdef[3:]
        elif featdef.startswith(codecs.BOM_UTF16_BE) or featdef.startswith(codecs.BOM_UTF16_LE):
            featdef = featdef.decode('utf-16').encode('utf-8')
        fp = open('features.def', 'wb')
        fp.write(featdef)
        fp.close()
    else:
        import u.features
        if enc.startswith('utf'):
            u.features.makedef(nChars, 'utf-8')
        else:
            u.features.makedef(nChars, 'iso-8859-1')

if enc.startswith('utf'):
    open('UTF', 'wt').close()

if method.startswith('dif'):
    open('OK', 'wt').close()

s = u.myCgi.data.get('ca', b'auto').decode('utf-8')
if s == 'yes':
    cronbachalpha = True
elif s == 'no':
    cronbachalpha = False
else:
    cronbachalpha = True
    if nItems > 200:
        cronbachalpha = False


#|| do shift map

if not pseudo:
    if u.myCgi.data.get('shmap', None):
        os.chdir('../map')
        os.system('$PYTHON3 $APPDIR/util/smappre')

#|| finish and return to web

os.chdir('..')

for i in 'cccmaps clusters clumaps diff mdsplots mdsmaps prob plot'.split():
    os.mkdir(i)
if not method.startswith('num') and not method.startswith('dif'):
    for i in 'cludet cludet/_'.split():
        os.mkdir(i)

if method.startswith('dif'):
    fp = open('diff/diff.txt', 'wt', encoding='iso-8859-1')
    fp.write('{}\n'.format(nPlaces))
    for i in range(nPlaces):
        fp.write('{}\n'.format(latin1(lplaces[i])))
    for i in range(nPlaces):
        for j in range(i):
            fp.write(data[i][j] + '\n')
    fp.close()

fp = open('{}templates/plot_wm_6_all.cfg'.format(u.config.appdir), 'rb')
d = fp.read()
fp.close()
fp = open('clumaps/plot_wm_6_all.cfg', 'wb')
fp.write(d)
fp.close()

if not pseudo:
    fp = open('{}/templates/Makefile-map'.format(u.config.appdir), 'r')
    make = fp.read()
    fp.close()
    u.queue.enqueue(path + '/map', make.format({'appdir': u.config.appdir, 'python3': u.config.python3}))

if method.startswith('levfeat'):
    fp = open('{}/templates/Makefile-data'.format(u.config.appdir), 'r')
    make = fp.read()
    fp.close()
    u.queue.enqueue(path + '/data', make.format({'appdir': u.config.appdir,
                                                 'python3': u.config.python3,
                                                 'python3path': u.config.python3path}))
elif not method.startswith('num'):
    open('data/OK', 'w').close()


if method.startswith('num'):
    fp = open('{}/templates/Makefile-diffnum'.format(u.config.appdir), 'r')
    make = fp.read()
    fp.close()
    u.queue.enqueue(path + '/diff', make.format({'appdir': u.config.appdir,
                                                 'python3': u.config.python3,
                                                 'python3path': u.config.python3path}))

elif method.startswith('lev'):
    fp = open('{}templates/Makefile-diff'.format(u.config.appdir), 'r')
    make = fp.read()
    fp.close()
    if method.startswith('levfeat'):
        feat = ''
        plain = '# '
    else:
        feat = '# '
        plain = ''
    if cronbachalpha:
        ca1 = ''
        ca0 = '# '
    else:
        ca1 = '# '
        ca0 = ''
    u.queue.enqueue(path + '/diff', make.format({'nplaces': nPlaces,
                                                 'appdir': u.config.appdir,
                                                 'python3': u.config.python3,
                                                 'feat': feat,
                                                 'plain': plain,
                                                 'ca1': ca1,
                                                 'ca0': ca0}))
elif method.startswith('dif'):
    fp = open('{}templates/Makefile-diff-diff'.format(u.config.appdir), 'r')
    make = fp.read()
    fp.close()
    u.queue.enqueue(path + '/diff', make.format({'nplaces': nPlaces,
                                                 'appdir': u.config.appdir,
                                                 'python3': u.config.python3}))
else:
    fp = open('{}/templates/Makefile-diff-other'.format(u.config.appdir), 'r')
    make = fp.read()
    fp.close()
    c2 = ''
    if method == 'bin':
        command = 'leven -B'
    else:
        command = 'giw'
        c2 = '-C -4'
    if cronbachalpha:
        ca1 = ''
        ca0 = '# '
    else:
        ca1 = '# '
        ca0 = ''
    u.queue.enqueue(path + '/diff', make.format({'nplaces': nPlaces,
                                                 'appdir': u.config.appdir,
                                                 'python3': u.config.python3,
                                                 'command': command,
                                                 'c': c2,
                                                 'ca1': ca1,
                                                 'ca0': ca0}))

if pseudo:
    fp = open('{}/templates/Makefile-pseudomap'.format(u.config.appdir), 'r')
    make = fp.read()
    fp.close()
    u.queue.enqueue(path + '/map', make.format({'appdir': u.config.appdir,
                                                 'python3': u.config.python3}))

fp = open('{}/templates/Makefile-mdsplots'.format(u.config.appdir), 'r')
make = fp.read()
fp.close()
u.queue.enqueue(path + '/mdsplots', make.format({'appdir': u.config.appdir,
                                                 'python3': u.config.python3,
                                                 'python3path': u.config.python3path}))

fp = open('{}/templates/Makefile-mdsmaps'.format(u.config.appdir), 'r')
make = fp.read()
fp.close()
u.queue.enqueue(path + '/mdsmaps', make.format({'appdir': u.config.appdir,
                                                'python3': u.config.python3,
                                                'python2': u.config.python2,
                                                'python2path': u.config.python2path}))

fp = open('{}/templates/Makefile-cccmaps'.format(u.config.appdir), 'r')
make = fp.read()
fp.close()
u.queue.enqueue(path + '/cccmaps', make.format({'appdir': u.config.appdir,
                                                'python3': u.config.python3,
                                                'python2': u.config.python2,
                                                'python2path': u.config.python2path}))

n = max(2, min(8, nPlaces - 1))
fp = open('{}/templates/Makefile-clusters'.format(u.config.appdir), 'r')
make = fp.read()
fp.close()
u.queue.enqueue(path + '/clusters', make.format({'method': 'wa',
                                                 'groups': n,
                                                 'exp': 1,
                                                 'col': 'col',
                                                 'appdir': u.config.appdir,
                                                 'python3': u.config.python3,
                                                 'python2': u.config.python2,
                                                 'python2path': u.config.python2path}))

fp = open('{}/templates/Makefile-clumaps'.format(u.config.appdir), 'r')
make = fp.read()
fp.close()
u.queue.enqueue(path + '/clumaps', make.format({'appdir': u.config.appdir,
                                                'python3': u.config.python3,
                                                'python2': u.config.python2,
                                                'python2path': u.config.python2path}))

if not method.startswith('num') and not method.startswith('dif'):
    fp = open('{}/templates/Makefile-cludet'.format(u.config.appdir), 'r')
    make = fp.read()
    fp.close()
    u.queue.enqueue(path + '/cludet', make.format({'appdir': u.config.appdir,
                                                   'python3': u.config.python3,
                                                   'n': 6}))

fp = open('{}/templates/Makefile-prob'.format(u.config.appdir), 'r')
make = fp.read()
fp.close()
if method == 'giw':
    pp = '6'
else:
    pp = '1.5'
defaults = '0.2 60 {} col gawa'.format(pp)
fp = open('prob/current.txt', 'wt')
fp.write(defaults + '\n')
fp.close()
u.queue.enqueue(path + '/prob',
                make.format({'noise': '0.2', 'limit': '60', 'exp': pp, 'method': '-m wa -m ga -r 50'}) +
                '\techo ' + defaults + ' > reset\n')

if not pseudo:
    fp = open('{}/templates/Makefile-plot'.format(u.config.appdir), 'r')
    make = fp.read()
    fp.close()
    u.queue.enqueue(path + '/plot', make.format({'appdir': u.config.appdir}))

u.queue.enqueue(path, 'OK:\n\ttouch OK\n')

u.queue.run()

sys.stdout.write('Location: {}bin/goto?p={}\n\n'.format(u.config.appurl, path))
