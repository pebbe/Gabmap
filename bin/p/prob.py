#!/usr/bin/env python
"""
--documentation--
"""

__author__ = "Peter Kleiweg"
__version__ = "0.1"
__date__ = "2010/04/10"

#| imports

import os, re, sys

import u.config, u.path, u.html

#| globals

title = 'probabilistic dendrogram'

#| functions

def makepage(path):
    u.path.chdir(path)
    crumbs = u.path.breadcrumbs(path)
    ltitle = path.split('-')[1].replace('_', ' ') + ' / ' + title

    p = path.split('-', 1)[1]
    pp = p.rsplit('-', 1)[0]
    pnum =  path.split('-')[-2].split('_')[-1]

    sys.stdout.write(u.html.head(ltitle, tip=True, maptip=True))
    sys.stdout.write('''
    {}
    <div class="pgprob">
    <h2>{}</h2>
    '''.format(crumbs, title))

    if os.access('OK', os.F_OK):

        fp = open('../data/Method', 'rt')
        method = fp.read().strip()
        fp.close()

        fp = open('current.txt', 'rt')
        noise, limit, exponent, color, mthd = fp.read().split()
        fp.close()

        if color == 'col':
            col = ''
        else:
            col = 'bw'
            if not os.access('probbw.eps', os.F_OK):
                fpin = open('prob.eps', 'rt', encoding='iso-8859-1')
                fpout = open('probbw.eps', 'wt', encoding='iso-8859-1')
                for line in fpin:
                    if not re.match('\\s*\\S+\\s+\\S+\\s+\\S+\\s+cl\\s*$', line):
                        fpout.write(line)
                fpout.close()
                fpin.close()        
        sys.stdout.write('''
        {}
        <p>
        Above: Clustering with noise. The graph shows the relative certainty of certain clusters.
        '''.format(u.html.img(p + '-prob' + col)))

        # TODO: deze waardes inlezen vanuit bestand 'reset'
        # TODO: fix voor IE
        if method == 'giw':
            eV = '6'
        else:
            eV = '1.5'
        sys.stdout.write('''
	<script language="JavaScript"><!--
        function defaults(form) {{
        form.noise.value = "0.2";
        form.limit.value = "60";
        form.exp.value = "{}";
        form.col.value = "col";
        form.mthd.value = "gawa";
        }}
	//--></script>
        <form action="{}probform" method="post">
        <fieldset><legend></legend>
        <input type="hidden" name="p" value="project_{}">
        noise:&nbsp;<select name="noise">
        '''.format(eV, u.config.binurls, pnum))
        for i in '0.001 0.005 0.01 0.05 0.1 0.2 0.3 0.4 0.5 0.8 1 1.5 2 3 4'.split():
            if i == noise:
                sel = ' selected="selected"'
            else:
                sel = ''
            sys.stdout.write('<option{}>{}</option>\n'.format(sel, i))
        sys.stdout.write('''
        </select>
        limit:&nbsp;<select name="limit">
        ''')
        for i in '51 60 70 80'.split():
            if i == limit:
                sel = ' selected="selected"'
            else:
                sel = ''
            sys.stdout.write('<option value="{1}"{0}>{1}%</option>\n'.format(sel, i))
        sys.stdout.write('''
        </select>
        exponent:&nbsp;<select name="exp">
        ''')

        for i in '0.25 0.5 1 1.5 2 4 6'.split():
            if i == exponent:
                sel = ' selected="selected"'
            else:
                sel = ''
            sys.stdout.write('<option{0}>{1}</option>\n'.format(sel, i))

        sys.stdout.write('''
        </select>
        color:&nbsp;<select name="col">
        ''')

        for i, j in [('col', 'yes'), ('bw', 'no')]:
            if i == col:
                sel = ' selected="selected"'
            else:
                sel = ''
            sys.stdout.write('<option value="{}"{}>{}</option>\n'.format(i, sel, j))


        sys.stdout.write('''
        </select><br>
        &nbsp;<br>
        method:&nbsp;<select name="mthd">
        ''')
        for i, j in [('ga', 'group average'), ('wa', 'weighted average'), ('gawa',  'group average + weighted average')]:
            if i == mthd:
                sel = ' selected="selected"'
            else:
                sel = ''
            sys.stdout.write('<option value="{}"{}>{}</option>\n'.format(i, sel, j))
        sys.stdout.write('''
        </select>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;
        <input type="button" value="Restore defaults" onclick="defaults(this.form)">
        &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;
        <input type="submit" value="Update settings">
        </fieldset>
        </form>
        ''')

        if color == 'col':
            sys.stdout.write('''
            <p>
            For reference: Colors in the graph above correspond to colors in the map below.
            <p>
            {}
            '''.format(u.html.img(pp + '-cccmaps-ccc', usemap="map1")))

    elif os.access('QUEUED', os.F_OK):
        sys.stdout.write(u.html.busy())
    else:
         sys.stdout.write(u.html.makeError(path.split('-', 1)[1]))
         if os.access('reset', os.F_OK):
             sys.stdout.write('<p>\n<a href="{}probform?p=project_{}">Continue...</a>\n'.format(u.config.binurls, pnum))

    sys.stdout.write('\n</div>\n')
    sys.stdout.write(u.html.foot())


#| main
