#!/usr/bin/env python
"""
--documentation--
"""

__author__ = "Peter Kleiweg"
__version__ = "0.1"
__date__ = "2010/04/10"

#| imports

import os, sys

import u.path, u.html, u.config

#| globals

title = 'mds plots'

#| functions

def _number(s):
    try:
        f = '{:.2f}'.format(float(s))
    except:
        f = u.html.escape(s)
    return f

def makepage(path):
    u.path.chdir(path)
    crumbs = u.path.breadcrumbs(path)
    ltitle = path.split('-')[1].replace('_', ' ') + ' / ' + title

    p = path.split('-', 1)[1]
    project = path.split('-')[1]

    pnum =  path.split('-')[-2].split('_')[-1]

    sys.stdout.write(u.html.head(ltitle, tip=True))
    sys.stdout.write('''
    {}
    <div class="pgmdsplots">
    <h2>mds plots</h2>
    '''.format(crumbs))

    if os.access('OK', os.F_OK):

        fp = open('image.html', 'rt', encoding='utf-8')
        for line in fp:
            sys.stdout.write(line)
        fp.close()

        current = set()
        if os.access('current', os.F_OK):
            fp = open('current', 'rt', encoding='utf-8')
            for line in fp:
                current.add(line.strip())
            fp.close()

        places = []
        fp = open('../data/truelabels.txt', 'rt', encoding='utf-8')
        for line in fp:
            places.append(line.strip())
        fp.close()
        places.sort()

        corr = '<small><i>r</i> = {}</small>'.format(_number(open('mds.log', 'rt').read().split()[-1]))
        sys.stdout.write('''
        {}
        {}
        <script language="JavaScript"><!--
	  function clearAll(form) {{
	    o = form.s.options;
            for (var i = 0; i < o.length; i++) {{
	      o[i].selected = false;
            }}
          }}
	//--></script>
        <p>
        <form action="{}bin/mdsplotform" method="post" enctype="multipart/form-data">
        <fieldset><legend></legend>
        <input type="hidden" name="p" value="project_{}">
        Location(s):<br><select name="s" multiple="multiple" size="10">

        '''.format(u.html.img(p + '-plot2d', usemap="map1", noover=True), corr, u.config.appurl, pnum))

        for i in range(len(places)):
            if places[i] in current:
                s = ' selected="selected"'
            else:
                s = ''
            sys.stdout.write('<option value="{}"{}>{}</option>\n'.format(i, s, u.html.escape(places[i])))

        sys.stdout.write('''
        </select>
        <input onclick="clearAll(this.form)" type="button" value="Clear all"><br>
        &nbsp;<br>
        <input type="submit" value="Show labels">
        </fieldset>
        </form>
        ''')

    elif os.access('QUEUED', os.F_OK):
        sys.stdout.write(u.html.busy())
    else:
        sys.stdout.write(u.html.makeError(path.split('-', 1)[1]))

    sys.stdout.write('\n</div>\n')
    sys.stdout.write(u.html.foot())


#| main
