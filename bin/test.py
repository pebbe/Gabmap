#!/usr/bin/env python3
"""
--documentation--
"""

__author__ = "Peter Kleiweg"
__version__ = "0.1"
__date__ = "2010/04/24"

#| imports

import cgitb; cgitb.enable(format="text")

import os, sys

import u.config



sys.stdout.write('To do: check if mouse-over plot in "reference point maps" works with current version of R\n\n')

os.chdir(u.config.datadir)
for i in range(10):
    dirname = 'guest{}'.format(i)
    if not os.access(dirname, os.F_OK):
        os.mkdir(dirname)
        open(dirname + '/TIMESTAMP', 'wt').close()
        fp = open(dirname + '/passwd', 'wt')
        fp.write('guest\n')
        fp.close()

sys.stdout.write('ulimit -v : ')
sys.stdout.flush()
os.system('ulimit -v')
sys.stdout.write('\n')
sys.stdout.flush()
os.system('free -m')
sys.stdout.write('\n')

sys.stdout.write('stdout: {}  (should be UTF-8)\n\n'.format(sys.stdout.encoding))

sys.stdout.flush()
os.system('check3.py 2>&1')
sys.stdout.write('\n')

sys.stdout.flush()
os.system('id')
sys.stdout.write('\n')

sys.stdout.flush()
os.system('ls -Fla')
sys.stdout.write('\n')

for i, j in sorted(os.environ.items()):
    if i == 'SECRET' or i == 'SMTPPASS':
        j = '(value not shown)'
    sys.stdout.write('{}\n    {}\n'.format(i, j))

sys.stdout.write('\n\nenvironment through os.system:\n\n')
sys.stdout.flush()
os.system("set | perl -p -e 's/^(SECRET|SMTPPASS)=.*/$1=(value not shown)/;  s/=/\n    /'")

