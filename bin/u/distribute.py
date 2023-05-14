#!/usr/bin/env python3
"""
--documentation--
"""

__author__ = "Peter Kleiweg"
__version__ = "0.1"
__date__ = "2010/06/24"

#| imports

import os, stat, sys, time

import u.html

#| globals

colors = [x.replace(' ', '\n') for x in '''1 1 0.9979133
1 1 0.951178
1 1 0.904911
1 1 0.8595787
0.9936441 0.9975165 0.8157186
0.9766634 0.9908928 0.7751566
0.9537174 0.9819685 0.7408325
0.9261637 0.971293 0.7157217
0.8940859 0.9588669 0.7015761
0.853902 0.9431143 0.6966288
0.8013755 0.9221774 0.698484
0.7328502 0.8944876 0.7048092
0.6514241 0.8618412 0.7140098
0.5645519 0.8282048 0.7249673
0.4797463 0.797567 0.7365706
0.4021244 0.7716024 0.7476638
0.3317804 0.7471322 0.7569964
0.268176 0.7203667 0.7633064
0.2111159 0.6878304 0.76541
0.1631302 0.6485423 0.7627474
0.1280489 0.6027108 0.7550558
0.1096479 0.5505687 0.7420829
0.1079946 0.4933524 0.7240725
0.1174074 0.4338541 0.7020381
0.1317104 0.3750003 0.6770591
0.1449949 0.3195292 0.6498102
0.1528481 0.2691288 0.6187012
0.1513770 0.2251213 0.5813547
0.1368118 0.1887735 0.5354694
0.1090943 0.1596755 0.481082
0.07245721 0.1354784 0.4209323
0.03137255 0.1137255 0.3579104'''.split('\n')]

ncols = len(colors)

#| functions

def distmap(placen, placeall, outfile=None, normalise=True, normaliseBoth=False, red=False, imgpath=None, exfile=None):

    # current dir is user project dir

    fname = 'dist{}'.format(os.getpid())
    if not outfile:
        ofile = '../tmp/{0}'.format(fname)
    else:
        ofile = outfile

    if not os.path.isdir('../tmp'):
        os.mkdir('../tmp')

    # remove old files
    limit = time.time() - 10 * 60  # max: 10 minutes
    oldfiles = [x for x in os.listdir('../tmp') if x.startswith('dist')]
    for filename in oldfiles:
        try:
            f = '../tmp/' + filename
            if os.lstat(f)[stat.ST_MTIME] < limit:
                os.remove(f)
        except:
            pass
    
    placed = {}
    for i in placen:
        if placeall[i] > 0:
            placed[i] = placen[i] / placeall[i]
    if normalise:
        if normaliseBoth:
            fmin = min(placed.values())
        else:
            fmin = 0.0
        fmax = max(placed.values())
        if fmax == fmin:
            fmin = 0.0
            fmax = 1.0
    else:
        fmin = 0.0
        fmax = 1.0

    fp = open(ofile + '.rgb', 'wt', encoding='iso-8859-1')
    fp.write('3\n')
    if red:
        for place in placed:
            if placed[place]:
                fp.write('{}\n.9\n0\n0\n'.format(place))
            else:
                fp.write('{}\n1\n1\n1\n'.format(place))
    else:
        for place in placed:
            i = int((placed[place] - fmin) / (fmax - fmin) * ncols)
            if i == ncols:
                i = ncols - 1
            fp.write('{}\n{}\n'.format(place, colors[i]))
    fp.close()
    
    cfg = 'map/map.cfg'
    if exfile:
        cfg += '.tmp.{}'.format(os.getpid())
        fpout = open(cfg, 'wt')
        fpin = open('map/map.cfg', 'rt')
        for line in fpin:
            if not line.startswith('othermarkers:'):
                fpout.write(line)
        fpin.close()
        fpout.write('othermarkers: ' + exfile + '\n')
        fpout.close()
            

    os.system('maprgb -r -o {0}.eps {1} {0}.rgb 2> {0}.err'.format(ofile, cfg))
    if exfile:
        os.remove(cfg)
    os.system('smappost {0}.eps >> {0}.err 2>&1'.format(ofile))
    #os.system('( echo cd `dirname {0}.eps` ; cd `dirname {0}.eps` ; eps2png ) >> {0}.err 2>&1'.format(ofile))
    os.chdir('map')
    if not outfile:
        sys.stdout.write(u.html.img('tmp-{}'.format(fname), True, usemap="map1", imgpath=imgpath) + '\n<p>\n')
    os.chdir('..')
