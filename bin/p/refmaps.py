#!/usr/bin/env python
"""
--documentation--
"""

__author__ = "Peter Kleiweg"
__version__ = "0.1"
__date__ = "2010/04/10"

#| imports

import os, re, sys

import u.path, u.html, u.config

#| globals

title = 'reference point maps'

_colors = [x.replace(' ', '\n') for x in '''0.03137255 0.1137255 0.3579104
0.07245721 0.1354784 0.4209323
0.1090943 0.1596755 0.481082
0.1368118 0.1887735 0.5354694
0.1513770 0.2251213 0.5813547
0.1528481 0.2691288 0.6187012
0.1449949 0.3195292 0.6498102
0.1317104 0.3750003 0.6770591
0.1174074 0.4338541 0.7020381
0.1079946 0.4933524 0.7240725
0.1096479 0.5505687 0.7420829
0.1280489 0.6027108 0.7550558
0.1631302 0.6485423 0.7627474
0.2111159 0.6878304 0.76541
0.268176 0.7203667 0.7633064
0.3317804 0.7471322 0.7569964
0.4021244 0.7716024 0.7476638
0.4797463 0.797567 0.7365706
0.5645519 0.8282048 0.7249673
0.6514241 0.8618412 0.7140098
0.7328502 0.8944876 0.7048092
0.8013755 0.9221774 0.698484
0.853902 0.9431143 0.6966288
0.8940859 0.9588669 0.7015761
0.9261637 0.971293 0.7157217
0.9537174 0.9819685 0.7408325
0.9766634 0.9908928 0.7751566
0.9936441 0.9975165 0.8157186
1 1 0.8595787
1 1 0.904911
1 1 0.951178
1 1 0.9979133'''.split('\n')]

_ncols = len(_colors)

#| functions

def _toChar(m):
    return '{:c}'.format(int(m.group(1)))

def _getline(fp, required = False):
    while True:
        line = fp.readline()
        if not line:
            assert not required
            return ''
        line = line.strip()
        if line and line[0] != '#':
            return line

def _nan2NA(s):
    if s.lower() == 'nan':
        return 'NA'
    return s

def _NA2nan(s):
    if s.upper() == 'NA':
        return 'nan'
    return s

def _quote(s):
    return '"' + re.sub(r'(\\|")', r'\\\1', s.strip()) + '"'

def _unquote(s):
    s = s.strip()
    if len(s) < 2:
        return s
    if s[0] != '"' or s[-1] != '"':
        return s
    return re.sub(r'\\(.)', r'\1', s[1:-1]).strip()

def _difread(filename):
    """
    Reads a difference file, such as created by 'leven' program and others.
    Returns: tablesize, labels, table
    - filename: string
    - tablesize: integer
    - labels: list of strings
    - table: list of lists of floats (symmetric difference table)
    """

    fp = open(filename, 'rt', encoding='iso-8859-1')

    n = int(_getline(fp, True))

    lbls = []
    for i in range(n):
        lbls.append(_getline(fp, True))

    dif = [[] for x in range(n)]
    for i in range(n):
        dif[i] = [0 for x in range(n)]
    for i in range(n):
        for j in range(i):
            dif[i][j] = dif[j][i] = float(_NA2nan(_getline(fp, True)))

    fp.close()

    return n, lbls, dif

def makepage(path):
    u.path.chdir(path[:-8])
    if not os.path.isdir('refmaps'):
        os.mkdir('refmaps')
    os.chdir('refmaps')

    crumbs = u.path.breadcrumbs(path)
    ltitle = path.split('-')[1].replace('_', ' ') + ' / ' + title

    pnum =  path.split('-')[-2].split('_')[-1]

    sys.stdout.write(u.html.head(ltitle, tip=True, maptip=True))
    sys.stdout.write('''
    {}
    <div class="pgrefmaps">
    <h2>reference point maps</h2>
    '''.format(crumbs))

    if os.access('../diff/OK', os.F_OK):

        pseudo = False
        if os.access('../map/PSEUDOMAP', os.F_OK):
            pseudo = True

        if os.access('current', os.F_OK):
            fp = open('current', 'rt')
            current = fp.read().split()
            curplace, curmethod = [int(x) for x in current[:2]]
            if len(current) > 2:
                currev = int(current[2])
            else:
                currev = 0
            fp.close()
        else:
            curplace = curmethod = currev = 0

        if currev:
            _colors.reverse()

        places = {}
        truelabels = {}
        truelbl = []
        fp = open('../data/labels.txt', 'rt', encoding='iso-8859-1')
        fp2 = open('../data/truelabels.txt', 'rt', encoding='utf-8')
        for line in fp:
            a, b = line.strip().split(None, 1)
            places[b] = int(a)
            l = fp2.readline().strip()
            truelabels[b] = l
            truelbl.append(l)
        fp2.close()
        fp.close()

        sys.stdout.write('''
        <form action="{}bin/refmapsform" method="post">
        <input type="hidden" name="p" value="project_{}">
        <fieldset>
        <legend></legend>
        Place: <select name="pl">
        <option value="0">--</option>
        '''.format(u.config.appurl, pnum))
        for place in sorted(places):
            if places[place] == curplace:
                sel = ' selected="selected"'
                placename = place
            else:
                sel = ''
            sys.stdout.write('<option value="{}"{}>{}</option>\n'.format(places[place],
                                                                         sel,
                                                                         u.html.escape(truelabels[place])))
        sel = [''] * 4
        sel[curmethod] = ' selected="selected"'
        if currev:
            checked = ' checked="checked"'
        else:
            checked = ''
        sys.stdout.write('''
        </select><br>
        &nbsp;<br>
        Method: <select name="m">
        <option value="0"{0[0]}>linear distances</option>
        <option value="1"{0[1]}>quadratic distances</option>
        <option value="2"{0[2]}>zero-based linear distances</option>
        <option value="3"{0[3]}>zero-based quadratic distances</option>
        </select><br>
        &nbsp;<br>
        <input type="checkbox" name="revcol"{1}> Reverse colours<br>
        &nbsp;<br>
        <input type="submit" value="Show map">
        </fieldset>
        </form>
        '''.format(sel, checked))

        if curplace:
            if not os.access('curmap.eps', os.F_OK):
                n, lbls, dif = _difread('../diff/diff.txt')
                idx = lbls.index(placename)
                diffs = [dif[idx][i] for i in range(n) if i != idx]
                fmin = min(diffs)
                fmax = max(diffs)
                if curmethod == 2 or curmethod == 3:
                    fmin = 0.0
                fp = open('current.rgb', 'wt', encoding='iso-8859-1')
                fp.write('3\n{}\n1\n0\n0\n'.format(placename))
                for i in range(n):
                    if i == idx:
                        continue
                    f = (dif[idx][i] - fmin) / (fmax - fmin)
                    if curmethod == 1 or curmethod == 3:
                        f = f * f
                    fi = int(f * _ncols)
                    if fi == _ncols:
                        fi = _ncols - 1
                    fp.write('{}\n{}\n'.format(lbls[i], _colors[fi]))
                fp.close()
                os.system('maprgb -r -o curmap.eps ../map/map.cfg current.rgb 2> /dev/null')
                os.system('$PYTHON3 $APPDIR/util/smappost curmap.eps')
                if currev:
                    os.system('ref2star -r curmap.eps')
                else:
                    os.system('ref2star curmap.eps')

                if not pseudo and not os.access('plot01.eps', os.F_OK):
                    if not os.access('geo.dst', os.F_OK):
                        os.system('difmodin ../data/labels.txt tmp.tbl')
                        os.system('difmod -o geo.dst ../map/map.geo tmp.tbl')
                        os.remove('tmp.tbl')
                    n2, lbls2, geo = _difread('geo.dst')
                    fp = open('curplot.data', 'wt')
                    assert n == n2
                    for i in range(n):
                        if i == idx:
                            continue
                        fp.write('{} {}\n'.format(geo[idx][i], dif[idx][i]))
                    fp.close()
                    fp = open('curplace.txt', 'wt', encoding='utf-8')
                    fp.write(truelabels[placename] + '\n')
                    fp.close()
                    os.system('R --no-save < {}util/refplot.R > plot.log 2>&1'.format(u.config.appdir))
                    state = 0
                    fpin = open('plot01.eps', 'rt', encoding='iso-8859-1')
                    fpout = open('plot01i.eps', 'wt', encoding='iso-8859-1')
                    for line in fpin:
                        if state == 0:
                            fpout.write(line)
                            if line.startswith('%%BeginProlog'):
                                fpout.write('''
                                /mys 10 string def
                                /myf (image.coo) (w) file def
                                /mylog {
                                    2 copy transform
                                    exch 2 {
                                        round cvi mys cvs myf exch writestring myf ( ) writestring
                                    } repeat
                                    myf (\\n) writestring
                                } bind def
                                ''')
                                state = 1
                        elif state == 1:
                            if line.strip().endswith(' c p1'):
                                a = line.split()
                                fpout.write('{0[0]} {0[1]} mylog {0[2]} c p1\n'.format(a))
                            elif line.startswith('%%EOF'):
                                fpout.write('myf closefile\n')
                                fpout.write(line)
                                state = 2
                            else:
                                fpout.write(line)
                        else:
                            fpout.write(line)
                    fpout.close()
                    fpin.close()
                    os.system('eps2png > eps2png.log 2>&1')
                    n = -1
                    fp = open('image.coo', 'rt')
                    lines = fp.readlines()
                    fp.close()
                    i = 0
                    fp = open('image.coo', 'wt', encoding='iso-8859-1')
                    for line in lines:
                        if i == idx:
                            i += 1
                        fp.write(line.strip() + ' ' + truelbl[i].encode('iso-8859-1', 'xmlcharrefreplace').decode('iso-8859-1') + '\n')
                        i += 1
                    fp.close()
                    os.system('mkmap map2')
                    

            sys.stdout.write(u.html.img('project_{}-refmaps-curmap'.format(pnum), True, usemap="map1", idx=1))
            if not pseudo:
                fp = open('image.html', 'rt', encoding='utf-8')
                sys.stdout.write(fp.read())
                fp.close()
                sys.stdout.write('<p>\n' + u.html.img('project_{}-refmaps-plot01'.format(pnum), usemap="map2", noover=True, idx=2))


    elif os.access('../diff/QUEUED', os.F_OK):
        os.chdir('../diff/')
        sys.stdout.write(u.html.busy())
    else:
        sys.stdout.write(u.html.makeError(path.split('-', 1)[1]).replace('refmaps', 'diff'))

    sys.stdout.write('\n</div>\n')
    sys.stdout.write(u.html.foot())


#| main
