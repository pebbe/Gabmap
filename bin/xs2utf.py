#!/usr/bin/env python
"""

"""

__author__ = "Peter Kleiweg"
__version__ = "0.01"
__date__ = "2010/11/18"

#| imports

import cgitb; cgitb.enable(format="html")

import codecs, cgi, os, re, sys

import u.html, u.myCgi

#| globals

#| functions

def decode(data):
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

    return [x.decode(enc).replace('\n', '').replace('\r', '') for x in data.rstrip(splitter).split(splitter)]

def translate(s):
    s2 = ''
    s1 = ''
    while s:
        m = RE.match(s)
        ss = m.group()
        if not ss in tr:
            return True, '{}<span style="color:#FF0000">{}</span>'.format(u.html.escape(s1), u.html.escape(s))
        s = s[len(ss):]
        s1 += ss
        s2 += tr[ss]
    return False, s2

def hex2chr(m):
    return '{:c}'.format(int(m.group(1), 16))

def code2unicode(s):
    return re.sub(r'U\+([0-9A-Fa-f]{4})', hex2chr, s)

#| main

data = u.myCgi.data.get('data', '')
if not data:
    u.html.exitMessage('Error', 'Missing or empty data file')

data = decode(data)

trans = u.myCgi.data.get('trans', '')
if trans:
    trans = decode(trans)
else:
    fp = open('../tools/XSampaTable.txt', 'rt', encoding='utf-8')
    trans = fp.readlines()
    fp.close()

tr = {}
for line in trans:
    a = line.split()
    if len(a) < 2:
        continue
    if a[0][0] == '#':
        continue
    tr[code2unicode(a[0])] = code2unicode(a[1])

k = list(tr.keys())
k.sort(reverse=True)

RE = re.compile('|'.join([re.escape(x) for x in k]) + '|.')

result = []
errors = []
state = 0
lineno = 0
for line in data:
    lineno += 1
    if not line or line[0] == '#':
        result.append(line)
        continue
    items = line.split('\t')
    if state == 0:
        if not items[0]:
            items = items[1:]
        itemNames = items
        nItems = len(items)
        result.append(line)
        state = 1
    else:
        try:
            lbl = items[0]
        except:
            lbl = ''
        cells = items[1:]
        if len(cells) != nItems:
            errors.append('Line {} &quot;{}&quot; has {} data cells (should be {})'.format(
                lineno, u.html.escape(lbl), len(cells), nItems))
            continue
        for i in range(nItems):
            values = []
            for value in cells[i].split(' / '):
                value = re.sub('^(/ +)*(.*?)( +/)*$', '\\2', value)
                if not value:
                    continue
                err, txt = translate(value)
                if err:
                    errors.append('Parse error for &quot;{}&quot; - &quot;{}&quot, unknown token: {}'.format(
                        u.html.escape(lbl), u.html.escape(itemNames[i]), txt))
                else:
                    values.append(txt)
            cells[i] = ' / '.join(values)
        result.append(lbl + '\t' + '\t'.join(cells))


if errors:
    if len(errors) == 1:
        e = 'Error'
    else:
        e = 'Errors'
    u.html.exitMessage(e, '<ul>\n<li>' + '\n<li>'.join(errors) + '\n</ul>')


if u.myCgi.data.get('outenc', '') == b'utf16':
    enc = 'utf-16'
else:
    enc = 'utf-8'

fp = sys.stdout.detach()
fp.write('''Content-type: text/plain; charset={}
Content-Disposition: attachment; filename="nameless.txt"

'''.format(enc).encode('us-ascii'))
fp.write(('\n'.join(result) + '\n').encode(enc))
