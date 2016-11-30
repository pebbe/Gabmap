#!/usr/bin/env python
"""
--documentation--
"""

__author__ = "Peter Kleiweg"
__version__ = "0.1"
__date__ = "2010/04/10"

#| imports

import os, sys

import u.path, u.html

#| globals

title = 'linguistic difference vs geographic distance'

#| functions

def makepage(path):
    u.path.chdir(path)
    crumbs = u.path.breadcrumbs(path)
    ltitle = path.split('-')[1].replace('_', ' ') + ' / ' + title

    p = path.split('-', 1)[1]
    pnum = int(path.split('-')[1].split('_')[-1])

    sys.stdout.write(u.html.head(ltitle))
    sys.stdout.write('''
    {}
    <div class="pgprob">
    <h2>linguistic difference &#8596; geographic distance</h2>
    '''.format(crumbs))

    if os.access('OK', os.F_OK):

        sys.stdout.write('''
        &rarr; <a href="getplotdata?{}">download R data</a>{}
        <p>
        '''.format(pnum, u.html.help("plotr")))

        
        try:
            fp = open('plot01.log', 'rt', encoding='utf-8')
            txt = fp.read()
            fp.close()
        except:
            txt = ''
        else:
            txt = '<pre class="log">\n' + u.html.escape(txt) + '</pre>\n'

        # try:
        #     fp = open('plot02.log', 'rt', encoding='utf-8')
        #     txt2 = fp.read()
        #     fp.close()
        # except:
        #     txt2 = ''
        # else:
        #     txt2 = '<pre class="log">\n' + u.html.escape(txt2) + '</pre>\n'
        #
        # sys.stdout.write('''
        # {}
        # <p>
        # {}
        #
        # <p>
        # <hr>
        # '''.format(u.html.img(p + '-plot02'), txt2))

        if (os.access('plot01.eps', os.F_OK)):
            sys.stdout.write('''
            <p>
            {}
            <p>
            A plot with local regression (red) and asymptotic regression (blue).<br>
            A large b/a ratio indicates a large signal/noise ratio in the data.<br>
            A small value for c indicates that linguistic variation is measurable over a short geographic distance.
            <p>
            {}

            <p>
            <hr>
            '''.format(u.html.img(p + '-plot01'), txt))
        else:
            # TO DO: link to help page on reason for failure
            sys.stdout.write('''
            <p>
            {}
            <p>
            Asymptotic regression failed.
            <p>
            {}

            <p>
            <hr>
            '''.format(u.html.img(p + '-plot02'), txt))

        sys.stdout.write('''
        <p>
        
        {}        

        '''.format(u.html.img(p + '-plot03')))
    elif os.access('QUEUED', os.F_OK):
        sys.stdout.write(u.html.busy())
    else:
        sys.stdout.write(u.html.makeError(path.split('-', 1)[1]))

    sys.stdout.write('\n</div>\n')
    sys.stdout.write(u.html.foot())


#| main
