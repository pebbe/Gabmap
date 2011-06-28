#!/usr/bin/env python3
"""
--documentation--
"""

__author__ = "Peter Kleiweg"
__version__ = "0.1"
__date__ = "2010/04/24"

#| imports

import cgitb; cgitb.enable(format="text")

import os, re, stat, sys, time

import u.config


#| globals

#| functions



#| main

sys.stdout.write('Content-type: text/plain\n\n')

users = []

os.chdir(u.config.datadir)

dus = {}
fp = os.popen('du -h --max-depth=1', 'r')
for line in fp:
    a, b = line.split()
    b = b[2:]
    dus[b] = a
fp.close()

for dirname in os.listdir('.'):
    if dirname[0] == '.':
        continue
    if os.access(dirname + '/TIMESTAMP', os.F_OK):
        t = os.stat(dirname + '/TIMESTAMP')[stat.ST_MTIME]
        t2 = os.stat(dirname + '/passwd')[stat.ST_MTIME]
        if dirname.startswith('guest') or dirname.startswith('demo'):
            email = dirname
        else:
            fp = open(dirname + '/email', 'rt')
            email = fp.read().strip()
            fp.close()
        email = re.sub('@.*', '@...', email)
        projects = len([f for f in os.listdir(dirname) if f.startswith('project')])
        if projects:
            projects = '{:2d}'.format(projects)
        else:
            projects = '  '
        du = dus.get(dirname, '')
        users.append((t, t2, email, projects, du))

sys.stdout.write('''number of users: {}

total disk use: {}

last activity  -  account since - number of projects  -  disk use  -  e-mail

'''.format(len(users), dus.get('', '')))

for t, t2, email, projects, du in sorted(users, reverse=True):
    sys.stdout.write(time.strftime(' %d %b %Y, %H:%M', time.localtime(t)).replace(' 0', '  ')[1:])
    sys.stdout.write('  -  ')
    sys.stdout.write(time.strftime(' %d %b %Y, %H:%M', time.localtime(t2)).replace(' 0', '  ')[1:])
    sys.stdout.write('  - {}  - {:>5}  -  {}\n'.format(projects, du, email))

sys.stdout.write('\n\n')
sys.stdout.flush()

lines = []
if os.access(u.config.appdir + 'demo-log.txt.1.gz', os.F_OK):
    fp = os.popen('gunzip -c {}demo-log.txt.1.gz'.format(u.config.appdir), 'r')
    lines = fp.readlines()
    fp.close()
if os.access(u.config.appdir + 'demo-log.txt', os.F_OK):
    fp = open(u.config.appdir + 'demo-log.txt', 'rt', encoding='utf-8')
    lines.extend(fp.readlines())
    fp.close()
if lines:
    lines.reverse()
    for line in lines[:100]:
        sys.stdout.write(line)
    fp.close()
    sys.stdout.write('\n\n')
    sys.stdout.flush()

os.system('date 2>&1')
