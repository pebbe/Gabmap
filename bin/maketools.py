#!/usr/bin/env python3

import os

from u.config import appdir, binurls

targets = ('tools/ll2kml.html', 'tools/xs2utf.html')

for target in targets:
    outfile = appdir + target
    infile = outfile + '.IN'
    try:
        outst = os.stat(outfile)
    except:
        pass
    else:
        inst = os.stat(infile)
        if inst.st_mtime < outst.st_mtime:
            continue
    fp = open(infile, 'rt', encoding='utf-8')
    text = fp.read()
    fp.close()
    fp = open(outfile, 'wt', encoding='utf-8')
    fp.write(text.format(vars()))
    fp.close()

