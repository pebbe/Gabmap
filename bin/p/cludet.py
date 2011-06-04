#!/usr/bin/env python
"""
--documentation--
"""

__author__ = "Peter Kleiweg"
__version__ = "0.1"
__date__ = "2010/04/10"

#| imports

import os, re, sys, unicodedata

import u.path, u.html, u.config, u.distribute, u.setChar

#| globals

title = 'cluster determinants'

defaults = '''
02B0  MODIFIER LETTER SMALL H
02B1  MODIFIER LETTER SMALL H WITH HOOK
02B2  MODIFIER LETTER SMALL J
02B3  MODIFIER LETTER SMALL R
02B4  MODIFIER LETTER SMALL TURNED R
02B5  MODIFIER LETTER SMALL TURNED R WITH HOOK
02B6  MODIFIER LETTER SMALL CAPITAL INVERTED R
02B7  MODIFIER LETTER SMALL W
02B8  MODIFIER LETTER SMALL Y
02C0  MODIFIER LETTER GLOTTAL STOP
02C1  MODIFIER LETTER REVERSED GLOTTAL STOP
02E0  MODIFIER LETTER SMALL GAMMA
02E1  MODIFIER LETTER SMALL L
02E2  MODIFIER LETTER SMALL S
02E3  MODIFIER LETTER SMALL X
02E4  MODIFIER LETTER SMALL REVERSED GLOTTAL STOP
0363  COMBINING LATIN SMALL LETTER A
0364  COMBINING LATIN SMALL LETTER E
0365  COMBINING LATIN SMALL LETTER I
0366  COMBINING LATIN SMALL LETTER O
0367  COMBINING LATIN SMALL LETTER U
0368  COMBINING LATIN SMALL LETTER C
0369  COMBINING LATIN SMALL LETTER D
036A  COMBINING LATIN SMALL LETTER H
036B  COMBINING LATIN SMALL LETTER M
036C  COMBINING LATIN SMALL LETTER R
036D  COMBINING LATIN SMALL LETTER T
036E  COMBINING LATIN SMALL LETTER V
036F  COMBINING LATIN SMALL LETTER X
207F  SUPERSCRIPT LATIN SMALL LETTER N
'''.strip().split('\n')


#| functions

def _num2chr(m):
    return '{:c}'.format(int(m.group(1)))

def _toStrHtml(s, em=False):
    if s == '__':
        if em:
            return '<em>(empty)</em>'
        else:
            return ''
    return u.html.escape(re.sub('_([0-9]+)_', _num2chr, s))

def makepage(path):
    u.path.chdir(path)
    crumbs = u.path.breadcrumbs(path)
    ltitle = path.split('-')[1].replace('_', ' ') + ' / ' + title

    p = path.split('-', 1)[1]
    project = path.split('-')[1]

    pnum =  path.split('-')[-2].split('_')[-1]

    if not os.access('items.txt', os.F_OK):
        items = {}
        for filename in os.listdir('../data/_'):
            if not filename.endswith('.data'):
                continue
            fname = filename.replace('.data', '')
            iname = re.sub('_([0-9]+)_', _num2chr, fname)
            items[fname] = iname
        fp = open('items.txt', 'wt', encoding='utf-8')
        for i in sorted(items):
            fp.write('{}\t{}\n'.format(i, items[i]))
        fp.close()

        
    sys.stdout.write(u.html.head(ltitle, tip=True, maptip=True))
    sys.stdout.write('''
    {}
    <div class="pgcludet">
    <h2>cluster determinants</h2>
    '''.format(crumbs))

    if os.access('OK', os.F_OK):

        if os.access('../data/UTF', os.F_OK):
            encoding = 'utf-8'
        else:
            encoding = 'iso-8859-1'

        sys.stdout.write('''<div class="info">
        Here you can discover what linguistic features are characteristic for certain areas.<br>
        &nbsp;<br>
        For an introduction, read <a href="../doc/ClusterDeterminants" target="_blank">this demonstration</a>
        </div>''')

        accents = {}
        if encoding == 'utf-8':
            if not os.access('accents.txt' ,os.F_OK):
                fpin = open('../data/charcount.txt', 'rt')
                fpout = open('accents.txt', 'wt')
                for line in fpin:
                    i = int(line.split()[0])
                    c = u.setChar.ci(i)
                    if c != 'V' and c != 'S' and c != 'C':
                        fpout.write('{}\n'.format(i))
                fpout.close()
                fpin.close()

            fp = open('accents.txt', 'rt')
            for line in fp:
                accents[int(line)] = False
            fp.close()

            if not os.access('accentscurrent.txt' ,os.F_OK):
                fp = open('accentscurrent.txt', 'wt')
                for j in defaults:
                    i = int(j.split()[0], 16)
                    if i in accents:
                        fp.write('{}\n'.format(i))
                fp.close()

            fp = open('accentscurrent.txt', 'rt')
            for line in fp:
                accents[int(line)] = True
            fp.close
        
        sys.stdout.write('<h3 id="s1">Step 1: select number of clusters</h3>\n' + u.html.img(p + '-clmap', usemap="map1", idx=1, pseudoforce=True) + '\n')


        fp = open('current', 'rt')
        current = fp.read().split()
        fp.close()

        sys.stdout.write('''
        <p>
	<form action="{}bin/cludetform" method="post" enctype="multipart/form-data">
	<input type="hidden" name="p" value="{}">
	<input type="hidden" name="action" value="number">
	Number of clusters:
	<select name="n">
        '''.format(u.config.appurl, project))
        n = int(current[0])
        for i in range(2, 13):
            if i == n:
                sys.stdout.write('<option selected="selected">{}</option>\n'.format(i))
            else:
                sys.stdout.write('<option>{}</option>\n'.format(i))
        sys.stdout.write('''
        </select>
	<input type="submit" value="Change number">
	</form>
        <p>
        ''')

        if len(current) > 1:
            curclnum = int(current[1])
        else:
            curclnum = 0

        sys.stdout.write('''
        <h3 id="s2">Step 2: select cluster</h3>
	<form action="{}bin/cludetform" method="post" enctype="multipart/form-data">
	<input type="hidden" name="p" value="{}">
	<input type="hidden" name="action" value="cluster">
        '''.format(u.config.appurl, project))

        if accents:
            sys.stdout.write('''
            <div class="accents">
            These characters are ignored, unless checked:
            <div class="ipa2">
            ''')

            for i in sorted(accents):
                if i == 32:
                    s = 'SPACE'
                else:
                    s = '&nbsp;&#{};&nbsp;'.format(i)
                if accents[i]:
                    v = ' checked="checked"'
                else:
                    v = ''
                nm = unicodedata.name('{:c}'.format(i), '')
                if nm:
                    a1 = '<abbr title="{}">'.format(u.html.escape(nm))
                    a2 = '</abbr>'
                else:
                    a1 = a2 = ''
                sys.stdout.write('<span class="cdc">{}<input type="checkbox" name="chr{}"{}>&nbsp;{}{}</span>\n'.format(a1, i, v, s, a2))
            sys.stdout.write('''
            </div>
            </div>
            &nbsp;<br>
            ''')

        sys.stdout.write('''
	Clusters in plot:
        '''.format(u.config.appurl, project))

        for i in range(1, n + 1):
            if i == curclnum:
                c = ' checked="checked"'
            else:
                c = ''
            sys.stdout.write('<span class="s{0}"><input type="radio" name="c" value="{0}"{1}></span>\n'.format(i, c))
        sys.stdout.write('''
	<input type="submit" value="Select cluster">
	</form>
        <p>
        ''')

        if os.access('important.txt', os.F_OK):

            if len(current) > 2:
                curitem = current[2]
            else:
                curitem = ''

            sys.stdout.write('''
            <!-- <h3 id="s3">step 3: select important item</h3> -->
            <h3 id="s3">step 3: select relevant item</h3>
            <form action="{}bin/cludetform" method="post" enctype="multipart/form-data">
            <input type="hidden" name="p" value="{}">
            <input type="hidden" name="action" value="item">
            <!-- Items sorted by importance: -->
            Items sorted by relevance:
            <select name="item">
            '''.format(u.config.appurl, project))
            fp = open('important.txt', 'rt')
            for line in fp:
                a, b, c, d, e = line.split()
                if d == '0':
                    continue
                f = e[2:-5]
                if f == curitem:
                    sel = ' selected="selected"'
                else:
                    sel = ''
                sys.stdout.write('<option value="{}"{}>{:.2f} - {:.2f} - {:.2f} - {} ({})</option>\n'.format(
                    f, sel, float(a), float(b), float(c), _toStrHtml(f), d))
                #sys.stdout.write('<option value="{}"{}>{:.2f} - {} ({})</option>\n'.format(
                #    f, sel, float(a), _toStrHtml(f), d))
            sys.stdout.write('''
            </select>
            <input type="submit" value="Select item">
            <br>&rarr; <a href="cludetlist?p={}" target="_blank">download as list</a>
            <br>&rarr; <a href="help?s=cludetscores" target="_blank">about relevance (weighted importance)</a>
            </form>
            <p>
            '''.format(project))

            if curitem:
                if not os.access('currentlist.txt', os.F_OK):
                    variants = {}
                    fp = open('../data/_/' + curitem + '.data', 'rb')
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

            if curitem:
                if not os.access('currentselect.txt', os.F_OK):
                    fpin = open('_/' + curitem + '.utxt', 'rt')
                    fpout = open('currentselect.txt', 'wt')
                    fpout2 = open('currentreject.txt', 'wt')
                    for line in fpin:
                        line = line.strip()
                        if not line:
                            continue
                        elif line[0] == '[':
                            fpout2.write(line[1:-1] + '\n')
                            continue
                        elif line[-1] != ']':
                            continue
                        for a in line[:-2].split('[ ')[1].split(' | '):
                            fpout.write(a + '\n')
                    fpout2.close()
                    fpout.close()
                    fpin.close()

            if curitem:
                wrdcount = {}
                fp = open('currentlist.txt', 'rt', encoding='utf-8')
                for line in fp:
                    a, b = line.split(None, 1)
                    wrdcount[b.strip()] = a
                fp = open('_/' + curitem + '.utxt', 'rt')
                lines = fp.readlines()
                fp.close()
                sys.stdout.write('''
                <table style="margin:1em 0px;padding:0px;border:0px" cellpadding="0" cellspacing="0" border="0">
                <tr valign="top"><td style="padding-right:4em">
                Current item: {0}<br>
                <table cellspacing="0" celpadding="0" border="0">
                <tr><td>Importance (weighted):&nbsp;  <td>{1[0]:.2f}
                <tr><td>Distinctiveness (weighted):&nbsp; <td>{1[1]:.2f}
                <tr><td>Representativeness (weighted):&nbsp;    <td>{1[2]:.2f}
                </table>
                Patterns with forms:
                <ul>
                '''.format(_toStrHtml(curitem), [float(x) for x in lines[-1].split()]))
                for line in lines[:-1]:
                    if line[0] == '[':
                        continue
                    if line.strip():
                        a, b, c, d, e, f = line.split(None, 5)
                        sys.stdout.write('<li>{:.2f} - {:.2f} - {:.2f} - <span class="ipa2">{}</span> {}\n\n'.format(
                            float(a), float(b), float(c), _toStrHtml(d, True), e))
                        #sys.stdout.write('<li>{:.2f} - <span class="ipa2">{}</span> {}\n\n'.format(
                        #    float(a), _toStrHtml(d, True), e))
                        wrds = [re.sub('_([0-9]+)_', _num2chr, w) for w in f.split() if w != '[' and w != '|' and w != ']']
                        if len(wrds) > 1 or _toStrHtml(d) != u.html.escape(wrds[0]):
                            sys.stdout.write('<ul>\n')
                            for wrd in sorted(wrds):
                                sys.stdout.write('<li><span class="ipa2">{}</span> ({})\n'.format(
                                    u.html.escape(wrd), wrdcount[wrd]))
                            sys.stdout.write('</ul>\n')
                sys.stdout.write('''
                </ul>
                </td>
                ''')
                if os.access('currentreject.txt', os.F_OK):
                    sys.stdout.write('''
                    <td style="padding-left:2em;border-left:1px solid #808080">
                    Rejected patterns:<br>
                    &nbsp;<br>
                    ''')
                    fp = open('currentreject.txt', 'rt')
                    for line in fp:
                        sys.stdout.write('<span class="ipa2">' + _toStrHtml(line.strip(), True) + '</span><br>\n')
                    fp.close()
                    sys.stdout.write('</td>\n')
                sys.stdout.write('</tr>\n</table>\n')

            if curitem:
                if not os.access('distmap.ex', os.F_OK):
                    fpout = open('distmap.ex', 'wt', encoding='iso-8859-1')
                    fpin = open('clgroups.txt', 'rt', encoding='iso-8859-1')
                    for line in fpin:
                        a, b = line.split(None, 1)
                        if a == current[1]:
                            fpout.write('1 ' + b)
                    fpin.close()
                    if os.access('../map/map.ex', os.F_OK):
                        fpin = open('../map/map.ex', 'rt', encoding='iso-8859-1')
                        for line in fpin:
                            fpout.write(line)
                        fpin.close()
                    fpout.close()
                if not os.access('distmap.eps', os.F_OK):
                    variantset = set()
                    fp = open('currentselect.txt', 'rt')
                    for line in fp:
                        variantset.add(re.sub('_([0-9]+)_', _num2chr, line.strip()))
                    fp.close()
                    placen = {}
                    placeall = {}
                    fp = open('../data/_/{}.data'.format(curitem), 'rb')
                    for line in fp:
                        if line[:1] == b':':
                            place = line[1:].decode('iso-8859-1').strip()
                            if not place in placen:
                                placen[place] = 0
                                placeall[place] = 0
                        elif line[:1] == b'-':
                            if line[1:].strip().decode(encoding) in variantset:
                                placen[place] += 1
                            placeall[place] += 1
                    fp.close()
                    os.chdir('..')
                    u.distribute.distmap(placen, placeall, 'cludet/distmap', exfile='cludet/distmap.ex', normalise=False)
                    os.chdir('cludet')

            if curitem:
                sys.stdout.write(u.html.img('project_{}-cludet-distmap'.format(pnum), True, usemap="map1", idx=2))

                if os.access('currentregex.txt', os.F_OK):
                    fp = open('currentregex.txt', 'rt', encoding='utf-8')
                    regex = fp.read().strip()
                    fp.close()
                else:
                    regex = ''

                sys.stdout.write('''
                <h3 id="s4">Step 4: try for determinant feature</h3>
                <form action="{}bin/cludetform" method="post" enctype="multipart/form-data">
                <input type="hidden" name="hebci_auml"   value="&auml;">
                <input type="hidden" name="hebci_divide" value="&divide;">
                <input type="hidden" name="hebci_euro"   value="&euro;">
                <input type="hidden" name="hebci_middot" value="&middot;">
                <input type="hidden" name="hebci_oelig"  value="&oelig;">
                <input type="hidden" name="hebci_oslash" value="&oslash;">
                <input type="hidden" name="hebci_Scaron" value="&Scaron;">
                <input type="hidden" name="hebci_sect"   value="&sect;">
                <input type="hidden" name="hebci_thorn"  value="&thorn;">
                <input type="hidden" name="p" value="{}">
                <input type="hidden" name="action" value="regex">
                Regular expression:{}<br><input type="text" name="regex" size="60" value="{}" class="ipa2">
                <input type="submit" value="Try feature">
                </form>
                '''.format(u.config.appurl, project, u.html.help('regex'), regex))

                if regex:
                    fp = open('reresults.txt', 'rt')
                    results = fp.read().split()
                    fp.close()
                    sys.stdout.write('''
                    &nbsp;<br>
                    Current regular expression: <span class="ipa2">{0}</span>
                    <!--
                    Relevance: {1[0]:.2f}<br>
                    -->
                    <table cellspacing="0" celpadding="0" border="0">
                    <tr><td>Importance (weighted):&nbsp;  <td>{1[0]:.2f}
                    <tr><td>Distinctiveness (weighted):&nbsp; <td>{1[1]:.2f}
                    <tr><td>Representativeness (weighted):&nbsp;    <td>{1[2]:.2f}
                    </table>
                    Matching forms:
                    '''.format(regex, [float(x) for x in results]))
                    found = False
                    fp = open('rematches.txt', 'rt', encoding='utf-8')
                    for line in fp:
                        if not found:
                            sys.stdout.write('<ul>\n')
                            found = True
                        a, b = line.split(None, 1)
                        sys.stdout.write('<li><span class="ipa2">{}</span> ({})\n'.format(u.html.escape(b.strip()), a))
                    fp.close()
                    if found:
                        sys.stdout.write('</ul>\n')
                    else:
                        sys.stdout.write('none\n')

                if regex and not os.access('redistmap.eps', os.F_OK):
                    variantset = set()
                    fp = open('rematches.txt', 'rt', encoding='utf-8')
                    for line in fp:
                        variantset.add(line.split(None, 1)[1].strip())
                    fp.close()
                    placen = {}
                    placeall = {}
                    fp = open('../data/_/{}.data'.format(curitem), 'rb')
                    for line in fp:
                        if line[:1] == b':':
                            place = line[1:].decode('iso-8859-1').strip()
                            if not place in placen:
                                placen[place] = 0
                                placeall[place] = 0
                        elif line[:1] == b'-':
                            if line[1:].strip().decode(encoding) in variantset:
                                placen[place] += 1
                            placeall[place] += 1
                    fp.close()
                    os.chdir('..')
                    u.distribute.distmap(placen, placeall, 'cludet/redistmap', exfile='cludet/distmap.ex', normalise=False)
                    os.chdir('cludet')

                if regex:
                    sys.stdout.write(u.html.img('project_{}-cludet-redistmap'.format(pnum), True, usemap="map1", idx=3))



    elif os.access('QUEUED', os.F_OK):
        sys.stdout.write(u.html.busy())
    else:
        sys.stdout.write(u.html.makeError(path.split('-', 1)[1]))

    sys.stdout.write('\n</div>\n')
    sys.stdout.write(u.html.foot())


#| main