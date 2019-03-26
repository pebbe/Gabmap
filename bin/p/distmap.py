#!/usr/bin/env python
"""
--documentation--
"""

__author__ = "Peter Kleiweg"
__version__ = "0.1"
__date__ = "2010/04/10"

#| imports

import os, re, sys

import u.path, u.html, u.config, u.distribute

#| globals

title = 'distribution maps'

#| functions

def _num2chr(m):
    return '{:c}'.format(int(m.group(1)))

def _xmlescape(m):
    return '_{}_'.format(ord(m.group()))

def _iname(s):
    s = re.sub(r'[^-+a-zA-Z0-9]', _xmlescape, s)
    return s

def makepage(path):
    u.path.chdir(path[:-8])

    if not os.path.isdir('distmap'):
        os.mkdir('distmap')
    os.chdir('distmap')
    
    
    crumbs = u.path.breadcrumbs(path)
    ltitle = path.split('-')[1].replace('_', ' ') + ' / ' + title

    pnum =  path.split('-')[-2].split('_')[-1]

    sys.stdout.write(u.html.head(ltitle, tip=True, maptip=True))
    sys.stdout.write('''
    {}
    <div class="pgdistmap">
    <h2>distribution maps</h2>
    '''.format(crumbs))

    if not os.access('items.txt', os.F_OK):
        items = []
        for filename in os.listdir('../data/_'):
            if not filename.endswith('.data'):
                continue
            fname = filename.replace('.data', '')
            iname = re.sub('_([0-9]+)_', _num2chr, fname)
            items.append((iname.lower(), fname, iname))
        fp = open('items.txt', 'wt', encoding='utf-8')
        for i, j, k in sorted(items):
            fp.write('{}\t{}\n'.format(j, k))
        fp.close()

    if not os.access('current.txt', os.F_OK):
        open('current.txt', 'wt').close()

    fp = open('current.txt', 'rt', encoding='utf-8')
    current = [x.strip() for x in fp.read().strip().split('\n')]
    fp.close()
    currentitem = ''
    currentvariants = set()
    currentregex = ''
    if len(current) > 0:
        currentitem = current[0]
    if len(current) > 1:
        currentvariants = set(current[1].split('\t'))
    if len(current) > 2:
        currentregex = current[2]
        REGEX = re.compile(currentregex)

    sys.stdout.write('''
    <form action="{}distmapform" method="post" enctype="multipart/form-data">
    <fieldset><legend></legend>
    <input type="hidden" name="hebci_auml"   value="&auml;">
    <input type="hidden" name="hebci_divide" value="&divide;">
    <input type="hidden" name="hebci_euro"   value="&euro;">
    <input type="hidden" name="hebci_middot" value="&middot;">
    <input type="hidden" name="hebci_oelig"  value="&oelig;">
    <input type="hidden" name="hebci_oslash" value="&oslash;">
    <input type="hidden" name="hebci_Scaron" value="&Scaron;">
    <input type="hidden" name="hebci_sect"   value="&sect;">
    <input type="hidden" name="hebci_thorn"  value="&thorn;">
    <input type="hidden" name="p" value="project_{}">
    <input type="hidden" name="var" value="">
    Item: <select name="item">
    <option>--</option>
    '''.format(u.config.binrel, pnum))

    found = False
    fp = open('items.txt', 'rt', encoding='utf-8')
    for line in fp:
        a, b = line.strip().split('\t')
        if a == currentitem:
            sel = ' selected="selected"'
            currenthtml = u.html.escape(b)
            found = True
        else:
            sel = ''
        sys.stdout.write('<option value="{}"{}>{}</option>\n'.format(a, sel, u.html.escape(b)))
    fp.close()
    sys.stdout.write('''
    </select>
    <input type="submit" value="Select item">
    </fieldset>
    </form>
    ''')

    if not found:
        sys.stdout.write('\n</div>\n')
        sys.stdout.write(u.html.foot())
        return

    if os.access('../data/UTF', os.F_OK):
        encoding = 'utf-8'
    else:
        encoding = 'iso-8859-1'
    if not os.access('currentlist.txt', os.F_OK):
        variants = {}
        fp = open('../data/_/' + currentitem + '.data', 'rb')
        for line in fp:
            if line[:1] == b'-':
                v = line[1:].strip().decode(encoding)
                if not v in variants:
                    variants[v] = 0
                variants[v] += 1
        fp.close()
        fp = open('currentlist.txt', 'wt', encoding='utf-8')
        for v in sorted(variants):
            fp.write('{}\t{}\n'.format(variants[v], v))
        fp.close()

    fp = open('currentlist.txt', 'rt', encoding='utf-8')
    lines = fp.readlines()
    fp.close()

    sys.stdout.write('''
    <p>
    <form action="{}distmapform" method="post" enctype="multipart/form-data">
    <fieldset>
    <legend></legend>
    <input type="hidden" name="p" value="project_{}">
    <input type="hidden" name="item" value="{}">
    There are {} variants for <em>{}</em><br>
    Select one or more variants:<br><select name="var" multiple="multiple" size="10" class="ipa2">
    '''.format(u.config.binrel, pnum, currentitem, len(lines), currenthtml))

    for line in lines:
        ii, b = line.strip().split('\t', 1)
        a = _iname(b)
        if a in currentvariants:
            sel = ' selected="selected"'
            found = True
        else:
            sel = ''
        sys.stdout.write('<option value="{}"{}>{} ({})</option>\n'.format(a, sel, u.html.escape(b), ii))
    sys.stdout.write('''
    </select><br>
    &nbsp;<br>
    &nbsp;&nbsp;&nbsp;&nbsp;&mdash;&nbsp;or&nbsp;&mdash;<br>
    &nbsp;<br>
    Regular expression:{}
    <input type="hidden" name="hebci_auml"   value="&auml;">
    <input type="hidden" name="hebci_divide" value="&divide;">
    <input type="hidden" name="hebci_euro"   value="&euro;">
    <input type="hidden" name="hebci_middot" value="&middot;">
    <input type="hidden" name="hebci_oelig"  value="&oelig;">
    <input type="hidden" name="hebci_oslash" value="&oslash;">
    <input type="hidden" name="hebci_Scaron" value="&Scaron;">
    <input type="hidden" name="hebci_sect"   value="&sect;">
    <input type="hidden" name="hebci_thorn"  value="&thorn;">
    <input type="text" name="regex" size="60" class="ipa2">
    <br>
    &nbsp;<br>
    <input type="submit" value="Show distribution map">
    </fieldset>
    </form>
    '''.format(u.html.help('regex')))


    if not (currentvariants or currentregex):
        sys.stdout.write('\n</div>\n')
        sys.stdout.write(u.html.foot())
        return

    item = re.sub('_([0-9]+)_', _num2chr, currentitem)
    variantset = set([re.sub('_([0-9]+)_', _num2chr, x) for x in currentvariants])
    if not os.access('distmap.eps', os.F_OK):
        placen = {}
        placeall = {}
        variants = {}
        fp = open('../data/_/{}.data'.format(currentitem), 'rb')
        for line in fp:
            if line[:1] == b':':
                place = line[1:].decode('iso-8859-1').strip()
                if not place in placen:
                    placen[place] = 0
                    placeall[place] = 0
            elif line[:1] == b'-':
                if currentregex:
                    l = line[1:].strip().decode(encoding)
                    if REGEX.search(l):
                        placen[place] += 1
                        if not l in variants:
                            variants[l] = 0
                        variants[l] += 1
                elif line[1:].strip().decode(encoding) in variantset:
                    placen[place] += 1
                placeall[place] += 1
        fp.close()
        os.chdir('..')
        u.distribute.distmap(placen, placeall, 'distmap/distmap', normalise=False)
        os.chdir('distmap')

        if currentregex:
            fp = open('currentvariants.txt', 'wt', encoding='utf-8')
            for i in sorted(variants):
                fp.write('{} ({})\n'.format(i, variants[i]))
            fp.close()
            

    if currentregex:
        v = currentregex
        r = ' RE'
    else:
        if len(currentvariants) == 1:
            v = list(variantset)[0]
            r = ''
        else:
            v = '*'
            r = ' SET'
    sys.stdout.write('''
    <h3>Distribution map for{} &quot;<span  class="ipa">{}</span>&quot; in {}</h3>
    '''.format(r, u.html.escape(v), u.html.escape(item)))

    if currentregex:
        sys.stdout.write('<ul>\n')
        fp = open('currentvariants.txt', 'rt', encoding='utf-8')
        for line in fp:
            sys.stdout.write('<li><span class="ipa2">{0[0]}</span> {0[1]}\n'.format(u.html.escape(line.strip()).rsplit(None, 1)))
        fp.close()
        sys.stdout.write('</ul>\n')

    sys.stdout.write(u.html.img('project_{}-distmap-distmap'.format(pnum), True, usemap="map1"))

    sys.stdout.write('\n</div>\n')
    sys.stdout.write(u.html.foot())


#| main
