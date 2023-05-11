#!/usr/bin/env python
"""
--documentation--
"""

__author__ = "Peter Kleiweg"
__version__ = "0.1"
__date__ = "2010/04/10"

#| imports

import os, re, sys, unicodedata

import u.path, u.html, u.config

#| globals

title = 'data overview'

#| functions

def _num2chr(m):
    return '{:c}'.format(int(m.group(1)))

def makepage(path):
    u.path.chdir(path)
    crumbs = u.path.breadcrumbs(path)
    ltitle = path.split('-')[1].replace('_', ' ') + ' / ' + title

    pnum =  path.split('-')[-2].split('_')[-1]

    fp = open('Method', 'rt')
    method = fp.read().strip()
    fp.close()

    sys.stdout.write(u.html.head(ltitle))
    sys.stdout.write('''
    {}
    <div class="pgdata">
    <h2>{}</h2>
    '''.format(crumbs, title))

    if os.access('OK', os.F_OK):

        if method.startswith('lev'):
            sys.stdout.write('''
            Contents:
            <ul>
            <li><a href="#overview">Overview</a>
            <li><a href="#charlist">Character list</a>
            <li><a href="#search">Sample search</a>
            ''')

            if method.startswith('levfeat'):
                sys.stdout.write('''
                <li><a href="#errors">Errors</a>
                <li><a href="#tokens">Token list</a>
                ''')

            sys.stdout.write('</ul>\n')


        sys.stdout.write('<h3 id="overview">Overview{}</h3>\n'.format(u.html.help('dataoverview')))

        if os.access('comments.txt', os.F_OK):
            sys.stdout.write('<pre class="log">\n')
            fp = open('comments.txt', 'rt', encoding='utf-8')
            for line in fp:
                sys.stdout.write(u.html.escape(line))
            fp.close()
            sys.stdout.write('</pre>\n')

        if method.startswith('levfeat'):
            if not os.access('tokenstats.txt', os.F_OK):
                sumtokens = 0
                uniqtokens = 0
                fp = open('tokens-int.txt', 'rt')
                for line in fp:
                    if line.startswith('TOKEN'):
                        uniqtokens += 1
                        sumtokens += int(line.split()[-1])
                fp.close()
                fp = open('tokenstats.txt', 'wt')
                fp.write('{} {}\n'.format(sumtokens, uniqtokens))
                fp.close()
            fp = open('tokenstats.txt', 'rt')
            sumtokens, uniqtokens = fp.readline().split()
            fp.close()
            tokens = '\n<tr><td>Tokens:<td align="right">{}<tr><td>\nUnique tokens:<td align="right">{}\n'.format(sumtokens, uniqtokens)
        else:
            tokens = ''

        fp = open('stats.txt', 'rt')
        f = fp.readline().split()
        fp.close()
        if method.startswith('lev'):
            charcount = []
            charsum = 0
            fp = open('charcount.txt', 'rt')
            for line in fp:
                c, n = [int(x) for x in line.split()]
                charsum += 1
                charcount.append((c, n))
            fp.close()
            characters = '\n<tr><td>Characters:<td align="right">{}\n<tr><td>Unique characters:<td align="right">{}'.format(f[3], charsum)
        else:
            characters = ''

        sys.stdout.write('''
        <table class="stats" border="0" cellspacing="0" cellpadding="0">
        <tr><td>Places:<td align="right">{0[0]}
        <tr><td>Items:<td align="right">{0[1]}
        <tr><td>Instances:<td align="right">{0[2]}{1}{2}
        </table>
        '''.format(f, characters, tokens))

        if method.startswith('lev'):

            sys.stdout.write('<h3 id="charlist">Character list{}</h3>\n'.format(u.html.help('datacharlist')))


            sys.stdout.write('<p>\nClick on number in third column for a distribution map and a list of samples<p>\n')

            sys.stdout.write('<table class="charcount" border="1" cellspacing="0" cellpadding="4">\n')
            for c, n in charcount:
                if c > 255:
                    f1 = '''
                    <form method="post" action="https://www.unicode.org/cgi-bin/Code2Chart"
                          enctype="application/x-www-form-urlencoded" target="_blank">
                    <input type="hidden" name="HexCode" value="{:04X}">
                    <input value="?" type="submit">
                    '''.format(c)
                    f2 = '</form>'
                else:
                    f1 = f2 = ''

                sys.stdout.write('''
                <tr><!-- <td align="right"><tt>{0}</tt></td> -->
                    <td><tt>{0:04X}</tt></td>
                    <td align="center" class="ipa2">&nbsp;&#{0};&nbsp;</td>
                    <td align="right"><a href="{3}sample?{4}-{0}" target="_blank">{1}</a></td>
                    <td>{5}<small>{2}</small>{6}</td>
                </tr>
                '''.format(c, n, unicodedata.name('%c' % c, ''), u.config.binurls, pnum, f1, f2))
            sys.stdout.write('</table>\n')

            sys.stdout.write('''
            <h3 id="search">Sample search{}</h3>
            <form action="{}samplerx" method="post" enctype="multipart/form-data" accept-charset="utf-8" target="_blank">
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
            Regular expression:{}<br>
            <input type="text" name="regex" size="40">
            <input type="submit" value="Get samples">
            '''.format(u.html.help('datasearch'), u.config.binrel, pnum, u.html.help('regex')))

        if method.startswith('levfeat'):

            sys.stdout.write('<h3 id="errors">Errors{}</h3>\n'.format(u.html.help('dataerrors')))

            if os.access('UTF', os.F_OK):
                encoding = 'utf-8'
            else:
                encoding = 'iso-8859-1'

            lines = []
            fp = open('errors-float.txt', 'rb')
            for line in fp:
                if not line.startswith(b'No mapping from real'):
                    lines.append(line)
            fp.close()
            if not lines:
                sys.stdout.write('No errors\n')
            else:
                items = []
                footer = []
                sys.stdout.write('<p>\n<div class="log">\n')
                for line in lines:
                    if line[:2] == b'_/':
                        a, b, c, line = line.split(b':', 3)
                        item = re.sub('_([0-9]+)_', _num2chr, a.decode('us-ascii')[2:].replace('.sp', '').replace('.data', ''))
                        msg = c.decode('us-ascii')
                        parts = line.split('\u001B'.encode('iso-8859-1'))
                        p1 = parts[0].decode(encoding).strip()
                        p2 = parts[1].decode(encoding)[6:].strip()
                        p3 = parts[2].decode('iso-8859-1')[3:].strip()
                        if p3[:1] == ':':
                            p3 = p3[1:].strip()
                        items.append((p3, item, p1, p2, msg))
                    else:
                        footer.append(line.decode('us-ascii'))
                for place, item, p1, p2, msg in sorted(items):
                    if p2:
                        sys.stdout.write('''
                        <span class="ipa2">{}<span class="featerr">{}</span></span><br>
                        <span class="ghide"><span class="black">{} &mdash; {}</span> &mdash; {}: {:04X} &mdash; {}</span><br>
                        &nbsp;<br>
                        '''.format(u.html.escape(p1),
                                   u.html.escape(p2),
                                   u.html.escape(place),
                                   u.html.escape(item),
                                   u.html.escape(msg),
                                   ord(p2[0]),
                                   unicodedata.name(p2[0], '')))
                    else:
                        sys.stdout.write('''
                        <span class="ipa2">{}</span><br>
                        <span class="ghide"><span class="black">{} &mdash; {}</span> &mdash; {}</span><br>
                        &nbsp;<br>
                        '''.format(u.html.escape(p1),
                                   u.html.escape(place),
                                   u.html.escape(item),
                                   u.html.escape(msg)))
                for f in footer:
                    sys.stdout.write(f + '<br>\n')

                sys.stdout.write('</div>\n')

            if not method.endswith('user'):
                charcats = {}
                fp = open('charcat.txt', 'rt')
                for line in fp:
                    a, b = line.split()
                    charcats['{:c}'.format(int(a))] = b
                fp.close()

            fp = open('tokens-int.txt', 'rt', encoding=encoding)

            items = {}
            for line in fp:
                line = line.strip()
                if not line:
                    continue
                if line.startswith('TOKEN'):
                    continue
                i, c = line.split()
                c = c.replace('[[SP]]', ' ')
                if not c in items:
                    items[c] = 0
                items[c] += int(i)
            fp.close()

            sys.stdout.write('<h3 id="tokens">Token list{}</h3>\n'.format(u.html.help('datatokens')))
            
            if not method.endswith('user'):
                sys.stdout.write('<p><small>V = vowel, C = consonant, S = semivowel, U = unknown, X = stress, P = punctuation, M = modifier</small>\n')
                sys.stdout.write('<br><small>1 = opening bracket, 2 = closing bracket</small>\n')
            sys.stdout.write('<table class="charcount" border="1" cellspacing="0" cellpadding="4">\n')
            for c in sorted(items):
                xx = '&nbsp;'.join(['{:04X}'.format(ord(x)) for x in c])
                cc = '-'.join([str(ord(x)) for x in c])
                if method.endswith('user'):
                    cats = ''
                else:
                    cats = '<td><small>' + ' '.join([charcats[x] for x in c]) + '</small></td>'
                sys.stdout.write('''<tr>
                  <td><tt>{5}</tt></td>
                  <td align="center" class="ipa2">&nbsp;{0}&nbsp;</td>
                  <td align="right"><a href="{2}sample2?{3}-{4}" target="_blank">{1}</a></td>
                  {6}
                '''.format(u.html.escape(c), items[c], u.config.binurls, pnum, cc, xx, cats))
            sys.stdout.write('</table>\n')

    elif os.access('QUEUED', os.F_OK):
        sys.stdout.write(u.html.busy())
    else:
        sys.stdout.write(u.html.makeError(path.split('-', 1)[1]))

    sys.stdout.write('\n</div>\n')
    sys.stdout.write(u.html.foot())


#| main
