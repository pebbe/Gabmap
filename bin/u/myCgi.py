#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""

cgi.FieldStorage() in Python 3.1 werkt niet voor multipart/form-data

Dit is een simpele vervanger


"""

__author__ = "Peter Kleiweg"
__version__ = "0.1"
__date__ = "2010/03/27"

#| imports

import re, sys

#| globals

data = {}

#| functions

def _init():
    global data

    fp = sys.stdin.detach()
    sep = fp.readline().rstrip()
    state = 0
    key = ''
    for line in fp:
        if state == 0:
            line = line.strip()
            if not line:
                state = 1
                dat = b''
            else:
                m = re.search(br'[ ;]name\s*=\s*"(.*?)"', line)
                if m:
                    key = m.group(1).decode('us-ascii')
        elif state == 1:
            if line.startswith(sep):            
                state = 0
                if dat[-2:] == b'\r\n' or dat[-2:] == b'\n\r':
                    dat = dat[:-2]
                elif dat[-1:] == b'\n' or dat[-1:] == b'\r':
                    dat = dat[:-1]
                if key in data:
                    data[key] += b'\n' + dat
                else:
                    data[key] = dat
                key = ''
            else:
                dat += line
                

    fp.close()

#| main

_init()
