#!/usr/bin/env python
"""
--documentation--
"""

__author__ = "Peter Kleiweg"
__version__ = "0.1"
__date__ = "2010/04/10"

#| imports

import os, re, sys, unicodedata

import u.path, u.html, u.config, u.setChar

from p.diff import _methods as methods

#| globals

title = 'alignments'

#| functions

def _toChar(m):
    return '{:c}'.format(int(m.group(1)))

def _tokens2list():
    if os.access('../data/UTF', os.F_OK):
        enc = 'utf-8'
    else:
        enc = 'iso-8859-1'
    fpin = open('../data/tokens-int.txt', 'rt', encoding=enc)
    fpout = open('tokenlist.txt', 'wt', encoding=enc)
    for line in fpin:
        line = line.strip()
        if not line:
            fpout.write('{}\t{}\n'.format(idx, s))
        elif line.startswith('TOKEN'):
            idx = int(line.split()[1])
            n = 0
            s = ''
        else:
            a, b = line.split(None, 1)
            a = int(a)
            if a > n:
                n = a
                s = b
    fpout.close()
    fpin.close()

def _charcount2list():
    fpin = open('../data/charcount.txt', 'rt')
    fpout = open('tokenlist.txt', 'wt', encoding='utf-8')
    for line in fpin:
        a = int(line.split()[0])
        if a == 32:
            aa = '[[SP]]'
        else:
            aa = '{0:c}'.format(a)
        fpout.write('{}\t{}\n'.format(a, aa))
    fpout.close()
    fpin.close()

def _num2chr(m):
    return '{:c}'.format(int(m.group(1)))

def makepage(path):
    u.path.chdir(path[:-6])
    if not os.path.isdir('align'):
        os.mkdir('align')
    os.chdir('align')

    crumbs = u.path.breadcrumbs(path)
    ltitle = path.split('-')[1].replace('_', ' ') + ' / ' + title

    pnum =  path.split('-')[-2].split('_')[-1]

    sys.stdout.write(u.html.head(ltitle))
    sys.stdout.write('''
    {}
    <div class="pgalign">
    <h2>alignments</h2>
    '''.format(crumbs))

    if os.access('../data/OK', os.F_OK):

        fp = open('../data/Method', 'rt')
        m = methods[fp.read().strip()]
        fp.close()
        sys.stdout.write('Method: {}\n'.format(m))

        if os.access('../data/tokens-int.txt', os.F_OK):
            features = True
        else:
            features = False

        if not os.access('tokenlist.txt', os.F_OK):
            if features:
                _tokens2list()
            else:
                _charcount2list()

        if os.access('current', os.F_OK):
            fp = open('current', 'rt', encoding='utf-8')
            current = fp.readline().strip()
            try:
                curplace = fp.readline().strip()
            except:
                curplace = '0'
            fp.close()
        else:
            current = ''
            curplace = '0'

        sys.stdout.write('''
        <form action="{}alignform" method="post">
        <input type="hidden" name="p" value="project_{}">
        <fieldset>
        <legend></legend>
        Item: <select name="n">
        <option>--</option>
        '''.format(u.config.binrel, pnum))
        filenames = [x[:-5] for x in os.listdir('../data/_') if x.endswith('.data')]
        lines = []
        for filename in sorted(filenames):
            itemname = re.sub('_([0-9]+)_', _num2chr, filename)
            if itemname == current:
                sel = ' selected="selected"'
            else:
                sel = ''
            lines.append((itemname.lower(), '<option value="{}"{}>{}</option>\n'.format(filename, sel, u.html.escape(itemname))))
        for a, b in sorted(lines):
            sys.stdout.write(b)
        sys.stdout.write('''
        </select><br>
        &nbsp;<br>
        Place: <select name="l">
        <option value="0"> -- random places --</option>
        ''')
        lines = []
        truelabels = {}
        pseudolabels = {}
        fp = open('../data/labels.txt', 'rt', encoding='iso-8859-1')
        fp2 = open('../data/truelabels.txt', 'rt', encoding='utf-8')
        for line in fp:
            a, b = line.split(None, 1)
            b = b.strip()
            lines.append('{}\t{}'.format(b, a))
            l = fp2.readline().strip()
            truelabels[b] = l
            pseudolabels[l.encode('iso-8859-1', 'xmlcharrefreplace').decode('iso-8859-1')] = l
        fp2.close()
        fp.close()
        lines.sort()
        for line in lines:
            b, a = line.split('\t', 1)
            if a == curplace:
                sel = ' selected="selected"'
            else:
                sel = ''
            sys.stdout.write('<option value="{}"{}>{}</option>\n'.format(a, sel, u.html.escape(truelabels[b])))

        sys.stdout.write('</select>\n<br>&nbsp;<br>\n<input type="submit" value="Show alignments">\n</fieldset>\n</form>\n')


        if current:
            sys.stdout.write('<h3>{}</h3>\n'.format(u.html.escape(current)))
            try:
                fp = open('page', 'rt')
            except:
                page = 0
                pages = 0
                fp = open('alignments.txt', 'rb')
            else:
                page = int(fp.read())
                fp.close()
                fp = open('pages', 'rt')
                pages = int(fp.read())
                fp.close()
                fp = open('alignments{}.txt'.format(page), 'rb')
            if page:
                sys.stdout.write('Page: ')
                if page == 1:
                    sys.stdout.write(' &laquo;')
                else:
                    sys.stdout.write(' <a href="alignpage?{1}-{0}">&laquo;</a>'.format(page - 1, pnum))
                for i in range(1, pages + 1):
                    if i == page:
                        sys.stdout.write(' <b>{}</b>'.format(i))
                    else:
                        sys.stdout.write(' <a href="alignpage?{1}-{0}">{0}</a>'.format(i, pnum))
                if page == pages:
                    sys.stdout.write(' &raquo;')
                else:
                    sys.stdout.write(' <a href="alignpage?{1}-{0}">&raquo;</a>'.format(page + 1, pnum))
                sys.stdout.write('<p>\n')
            intab = False
            inItem = False
            for line in fp:
                line = line.strip(b'\n')
                if not line:
                    if intab:
                        sys.stdout.write('</table>\n')
                        intab = False
                elif line[:1] == b'[':
                    line = line.decode('iso-8859-1')
                    lbl = pseudolabels[line.partition(']')[2].strip()]
                    if inItem:
                        sys.stdout.write(' &mdash; ')
                        inItem = False
                    else:
                        inItem = True
                    sys.stdout.write(u.html.escape(lbl) + '\n')
                else:
                    line = line.decode('utf-8')
                    if not intab:
                        sys.stdout.write('<table class="align">\n')
                        rownum = 0
                        intab = True
                    rownum += 1
                    if rownum < 3:
                        sys.stdout.write('<tr class="ipa2">')
                    else:
                        sys.stdout.write('<tr>')
                    prev = '0'
                    for i in line[1:].split('\t'):
                        if rownum == 3:
                            if i == prev:
                                i = ''
                            else:
                                ii = i
                                i = '{:g}'.format(float(i) - float(prev))                                
                                prev = ii
                        if i == '[[SP]]':
                            ii = '<span class="space">SP</span>'
                        else:
                            ii = u.html.escape(i)
                        sys.stdout.write('<td>&nbsp;{}&nbsp;\n'.format(ii))
                    if rownum == 3:
                        sys.stdout.write('<td class="total">&nbsp;{}&nbsp;\n'.format(line.split('\t')[-1]))
                    else:
                        sys.stdout.write('<td class="white">&nbsp;\n')
            fp.close()
            if page:
                sys.stdout.write('<p>Page: ')
                if page == 1:
                    sys.stdout.write(' &laquo;')
                else:
                    sys.stdout.write(' <a href="alignpage?{1}-{0}">&laquo;</a>'.format(page - 1, pnum))
                for i in range(1, pages + 1):
                    if i == page:
                        sys.stdout.write(' <b>{}</b>'.format(i))
                    else:
                        sys.stdout.write(' <a href="alignpage?{1}-{0}">{0}</a>'.format(i, pnum))
                if page == pages:
                    sys.stdout.write(' &raquo;')
                else:
                    sys.stdout.write(' <a href="alignpage?{1}-{0}">&raquo;</a>'.format(page + 1, pnum))
                sys.stdout.write('<p>\n')

    elif os.access('../data/QUEUED', os.F_OK):
        os.chdir('../data/')
        sys.stdout.write(u.html.busy())
    else:
        sys.stdout.write(u.html.makeError(path.split('-', 1)[1]).replace('align', 'data'))

    sys.stdout.write('\n</div>\n')
    sys.stdout.write(u.html.foot())


#| main
