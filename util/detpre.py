#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
    This is detpre.py
    Copyright (C) 2011 Peter Kleiweg

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <http://www.gnu.org/licenses/>.
"""

__author__ = "Peter Kleiweg"
__version__ = "0.1"
__date__ = "2011/06/20"


#| imports

import cgitb; cgitb.enable(format="text")

import os

import u.setChar

#| globals

#| functions

#| main

if os.access('../data/UTF', os.F_OK):

    charset = set()

    fp = open('accentscurrent.txt', 'rt')
    for line in fp:
        charset.add(int(line))
    fp.close()
    fp = open('../data/charcount.txt', 'rt')
    for line in fp:
        i = int(line.split()[0])
        k = u.setChar.ci(i)
        if k == 'V' or k == 'S' or k == 'C':
            charset.add(i)
    fp.close()

    fp = open('currentchars-u.txt', 'wt', encoding='utf-8')
    for i in sorted(charset):
        fp.write('{:c}\n'.format(i))
    fp.close()
    
else:

    fp = open('currentchars-1.txt', 'wt', encoding='iso-8859-1')
    for i in ' 0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz':
        fp.write(i + '\n')
    fp.close()

