#!/usr/bin/env python

"""
--documentation--
"""

__author__ = "Peter Kleiweg"
__version__ = "0.1"
__date__ = "2010/01/29"

#| imports

import os, re, shutil, sys

import u.config, u.login, u.html, u.path

#| globals

#| functions

def _split(s):
    m = re.match(r'(.*?)([0-9]+)$', s)
    return (m.group(1), int(m.group(2)))

def cleanup():
    cwd = os.getcwd()
    u.path.chdir(u.login.username)

    for filename in os.listdir('.'):
        if not filename.startswith('project'):
            continue
        if os.access(filename + '/QUEUED', os.F_OK):
            continue
        if os.access(filename + '/OK', os.F_OK):
            continue

        shutil.rmtree(filename)

    os.chdir(cwd)

def makepage(path):

    u.path.chdir(path)

    title = path.split('-', 1)[1].replace('-', '/').replace('_', ' ')

    try:
        fp = open('description', 'rt', encoding='utf-8')
        description = fp.readline().strip()
        fp.close()
    except:
        description = ''

    fp = open('data/Method', 'rt')
    method = fp.read().strip()
    fp.close()

    header = '''<script type="text/javascript"><!--
    var visible = false;
    function EDIT () {{
      s = document.getElementById('edit').style;
      if (visible) {{
        s.visibility = 'hidden';
        s.display = 'none';
        visible = false;
      }} else {{
        s.visibility = 'visible';
        s.display = 'block';
        visible = true;
      }}
      s = document.getElementById('title').style;
      if (visible) {{
        s.visibility = 'hidden';
        s.display = 'none';
      }} else {{
        s.visibility = 'visible';
        s.display = 'block';
      }}
    }}
    function CANCEL () {{
        s = document.getElementById('edit').style;
        s.visibility = 'hidden';
        s.display = 'none';
        s = document.getElementById('title').style;
        s.visibility = 'visible';
        s.display = 'block';
        visible = false;
    }}
    function DEL() {{
        var answer = confirm("Remove project {0}?\\n\\nThis will destroy all data and results for this project");
        if (answer) {{
            window.location = "{1}projectremove?p={0}";
        }}
    }}
    //--></script>
    '''.format(path.split('_')[-1], u.config.binurl)
    sys.stdout.write(u.html.head(title, headers=header))

    sys.stdout.write('''
    <div class="pgproject">
    <h2>{0} <a href="javascript:DEL()" title="Remove">&nbsp;&times;&nbsp;<!--&#10007;--></a></h2>
    <div id="title">
    {1} <a href="javascript:EDIT()" title="Edit">&nbsp;&nbsp;&laquo;&nbsp;&nbsp;</a>
    </div>
    <div id="edit" style="visibility:hidden;display:none">
    <form action="{3}editproject" method="post" enctype="multipart/form-data" accept-charset="utf-8" name="editproject">
    <input type="hidden" name="hebci_auml"   value="&auml;">
    <input type="hidden" name="hebci_divide" value="&divide;">
    <input type="hidden" name="hebci_euro"   value="&euro;">
    <input type="hidden" name="hebci_middot" value="&middot;">
    <input type="hidden" name="hebci_oelig"  value="&oelig;">
    <input type="hidden" name="hebci_oslash" value="&oslash;">
    <input type="hidden" name="hebci_Scaron" value="&Scaron;">
    <input type="hidden" name="hebci_sect"   value="&sect;">
    <input type="hidden" name="hebci_thorn"  value="&thorn;">
    <input type="hidden" name="p" value="{2}">
    Description:<br>
    <input type="text" name="description" size="80" value="{1}"><br>
    <input type="submit" value="Save">
    <input onclick="CANCEL()" type="button" value="Cancel">
    </form>
    </div>

    '''.format(title, description, path.split('_')[-1], u.config.binurl))

    if method.startswith('num'):
        num = 'num'
    else:
        num = ''

    sys.stdout.write('''<p>
    <table class="project">
    <tr><td colspan="2"><hr>
    <tr valign="top">
    <td>Index
    <td><ul>
    <li><a href="{0}goto?p={1}-map">places</a>
    '''.format(u.config.binrel, path.split('-', 1)[1]))
    if not method.startswith('dif'):
        sys.stdout.write('''
        <li><a href="{0}goto?p={1}-{2}items">items</a>
        '''.format(u.config.binrel, path.split('-', 1)[1], num))
    sys.stdout.write('''
    </ul>
    <tr valign="top">
    <td>Data inspection
    <td><ul>
    ''')
    if method.startswith('num'):
        sys.stdout.write('''
        <li><a href="{0}goto?p={1}-numdata">data overview</a>
        <li><a href="{0}goto?p={1}-nummap">value maps</a>
        '''.format(u.config.binrel, path.split('-', 1)[1]))
    elif method.startswith('dif'):
        sys.stdout.write('''
        <li><a href="{0}goto?p={1}-difdata">data overview</a>
        '''.format(u.config.binrel, path.split('-', 1)[1]))
    else:
        sys.stdout.write('''
        <li><a href="{0}goto?p={1}-data">data overview</a>
        '''.format(u.config.binrel, path.split('-', 1)[1]))
        sys.stdout.write('<li><a href="{0}goto?p={1}-distmap">distribution maps</a>\n'.format(
            u.config.binrel, path.split('-', 1)[1]))
    sys.stdout.write('</ul>\n')

    if method.startswith('lev'):
        sys.stdout.write('''
        <tr valign="top">
        <td>Measuring technique
        <td><ul>
        <li><a href="{0}goto?p={1}-align">alignments</a>
        </ul>
        '''.format(u.config.binrel, path.split('-', 1)[1]))

    sys.stdout.write('''
    <tr valign="top">
    <td>Differences
    <td><ul>
    <li><a href="{0}goto?p={1}-diff">statistics and difference maps</a>
    '''.format(u.config.binrel, path.split('-', 1)[1]))
    if not os.access('map/PSEUDOMAP', os.F_OK):
        sys.stdout.write('''
        <li><a href="{0}goto?p={1}-plot">linguistic difference &#8596; geographic distance</a>
        '''.format(u.config.binrel, path.split('-', 1)[1]))
    sys.stdout.write('''
    <li><a href="{0}goto?p={1}-refmaps">reference point maps</a>
    </ul>
    <tr><td colspan="2"><hr>
    <tr valign="top">
    <td>Multidimensional Scaling
    <td><ul>
    <li><a href="{0}goto?p={1}-mdsplots">mds plots</a>
    <li><a href="{0}goto?p={1}-mdsmaps">mds maps</a>
    </ul>
    <tr valign="top">
    <td>Discrete clustering
    <td><ul>
    <li><a href="{0}goto?p={1}-clusters">cluster maps and dendrograms</a>
    <li><a href="{0}goto?p={1}-clumaps">cluster validation</a>
    </ul>
    <tr valign="top">
    <td>Fuzzy clustering
    <td><ul>
    <li><a href="{0}goto?p={1}-prob">probabilistic dendrogram</a>
    <li><a href="{0}goto?p={1}-cccmaps">fuzzy cluster maps</a>
    </ul>
    '''.format(u.config.binrel, path.split('-', 1)[1]))

    if not method.startswith('num') and not method.startswith('dif'):
        sys.stdout.write('''
        <tr><td colspan="2"><hr>
        <tr valign="top">
        <td>Data mining
        <td><ul>
        <li><a href="{0}goto?p={1}-cludet">cluster determinants</a>
        </ul>
        '''.format(u.config.binrel, path.split('-', 1)[1]))

    sys.stdout.write('<tr><td colspan="2"><hr>\n</table>\n')
    sys.stdout.write('</div>\n')
    sys.stdout.write(u.html.foot())


def getProjects(path = ''):

    cleanup()

    projects = ''
    filenames = [x for x in os.listdir('.') if x.startswith('project')]
    for i in range(len(filenames)):
        j = int(filenames[i].split('_')[1])
        filenames[i] = (j, filenames[i])
    for j, filename in sorted(filenames):
        try:
            fp = open(filename + '/description', 'rt', encoding='utf-8')
            d = fp.readline().strip()
            fp.close()
        except:
            d = ''
        if not d:
            d = '&nbsp;'
        projects += '<tr valign="top">'
        projects += '<td><a href="goto?p={}">{}</a> \n'.format(filename, filename.replace('_', '&nbsp;'))
        projects += '  <td>&mdash; {}\n'.format(d)

    if projects:
        return '<table class="projects">\n' + projects + '</table>\n', len(filenames)
    else:
        return 'You don\'t have any projects yet<p>Read about how to get started: <a href="{}doc/preparing/" target="_blank">Preparing dialect data for Gabmap</a>'.format(u.config.apprel), 0
