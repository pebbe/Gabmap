#!/usr/bin/env python3
"""
--documentation--
"""

__author__ = "Peter Kleiweg"
__version__ = "0.1"
__date__ = "2010/07/28"

#| imports

import cgitb; cgitb.enable(format="text")

import os, re, sys

#| globals

reHelp = re.compile(r'(help|more)\s*\(\s*[\'"]([-_+0-9a-zA-Z]+)')
reTodo = re.compile(r'\bto ?do\b', re.I)

#| functions


#| main

sys.stdout.write('Content-type: text/plain\n\n')

for root, dirs, files in os.walk('.'):
    for filename in sorted(files):
        if filename.endswith('.py'):
            fullname = root + '/' + filename
            fp = open(fullname, 'rt', encoding='utf-8')
            for line in fp:
                for m in reHelp.finditer(line):
                    h = m.group(1)
                    if not os.access('../help/{}.html'.format(h), os.F_OK):
                        sys.stdout.write('Missing help page for {}: {}\n'.format(fullname, h))

sys.stdout.write('\n')
os.chdir('../help')
for filename in sorted(os.listdir('.')):
    if not filename.endswith('.html'):
        continue
    todo = False
    fp = open(filename, 'rt', encoding='utf-8')
    for line in fp:
        if reTodo.search(line):
            todo = True
            break
    fp.close()
    if todo:
        sys.stdout.write('To do in help page: {}\n'.format(filename))
        
