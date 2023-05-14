#!/usr/bin/env python3
"""

TO DO:

- alle taken die door 1 proces (=PID) in de queue worden gezet worden bij elkaar gezet in 1 subdir

- die subdir sluit aan achter de rij met de al bestaande subdirs

- taak uitvoeren: eerste taak in eerste subdir, daarna:
      als subdir leeg, dan verwijderen
      als niet leeg, dan verplaatsen naar einde van de rij

Waarom?

Als meerdere (twee) mensen data vrijwel gelijk puloaden, dan hoeft nummer 2 niet te wachten
tot alle taken van nummer 1 klaar zijn, maar worden taken om beurten uitgevoerd.


"""

__author__ = "Peter Kleiweg"
__version__ = "0.1"
__date__ = "2010/05/16"

#| imports

import os, random, re, sys

import u.config as _c
import u.login as _l

#| globals

_lockfile = _c.datadir + '.queue.lock'

#| check

# is 'ps' working as expected?
_fp = os.popen('ps h -p {} -o s'.format(os.getpid()), 'r')
_s = _fp.read().strip()
_fp.close()
assert len(_s) == 1 and 'DRS'.find(_s) > -1

#| functions

def _running(pid):
    try:
        pid = int(pid)
    except:
        return False
    fp = os.popen('ps h -p {} -o s'.format(pid), 'r')
    s = fp.read().strip()
    fp.close()
    return len(s) == 1 and 'DRS'.find(s) > -1

def getlock():
    dest = '{}'.format(os.getpid())
    while True:
        try:
            os.symlink(dest, _lockfile)
            s = os.readlink(_lockfile)
            assert s == dest
        except:
            pass
        else:
            return

        try:
            s = os.readlink(_lockfile)
            assert not _running(s)
            os.remove(_lockfile)
        except:
            pass
        else:
            continue

        time.sleep(1 + random.random())

def unlock():
    os.remove(_lockfile)

def enqueue(directory, make):

    getlock()

    filenames = [int(x) for x in os.listdir(_c.datadir + '.queue') if re.match('[0-9]+$', x)]
    if filenames:
        i = sorted(filenames)[-1] + 1
    else:
        i = 1
    fp = open(_c.datadir + '.queue/{}'.format(i), 'wt')
    fp.write('{}/{}\n'.format(_l.username, directory))
    fp.close()

    dirname = _c.datadir + _l.username + '/' + directory + '/'
    fp = open(dirname + 'Makefile', 'wt')
    fp.write('.SUFFIXES:\n\n')
    fp.write(make)
    fp.close()
    fp = open(dirname + 'QUEUED', 'wt')
    fp.write('{}\n'.format(i))
    fp.close()
    try:
        os.remove(dirname + 'OK')
    except:
        pass

    unlock()

def run():
    os.system('doqueue > /dev/null 2>&1 &')
