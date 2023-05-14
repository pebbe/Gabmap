#!/usr/bin/env python3
"""
--documentation--
"""

__author__ = "Peter Kleiweg"
__version__ = "0.1"
__date__ = "2010/06/10"

#| imports

from u.setChar import *

#| constants

_brackopen = {
    '{' : 16,
    '[' : 32,
    '(' : 64,
    '<' : 128   # not used
    }

_brackclose = {
    '}' : 16,
    ']' : 32,
    ')' : 64,
    '>' : 128   # not used
    }

#| functions

def makedef(chars, enc, tokenized):

    fp = open('charcat.txt', 'wt')
    for c in sorted(chars):
        fp.write('{}\t{}\n'.format(c, ci(c)))
    fp.close()

    vowels = []
    semivowels = []
    consonants = []
    stresses = []
    unknowns = []
    modifiers = []
    punctuations = []
    bracket1 = []
    bracket2 = []

    for c in sorted(chars):
        c = '{0:c}'.format(c)
        if not tokenized:
            unknowns.append(c)
        elif c in Vowel:
            vowels.append(c)
        elif c in Semivowel:
            semivowels.append(c)
        elif c in Consonant:
            consonants.append(c)
        elif c in Stress:
            stresses.append(c)
        elif c in Modifier:
            modifiers.append(c)
        elif c in Punctuation:
            punctuations.append(c)
        elif c in Bracket1:
            bracket1.append(c)
        elif c in Bracket2:
            bracket2.append(c)
        else:
            unknowns.append(c)

    fp = open('features.def', 'wt', encoding=enc)
    fp.write('# -*- coding: {} -*-\n'.format(enc))
    fp.write('''
##
## SUMMARY
##
## Indel (insertion or deletion) of stress symbol or punctuation: 0.5
## Other indel: 1.0
##
## Substitution of tokens with the same base symbol,
##    differing only in one or more diacritics: 0.5
## Substitution of vowel with consonant: 2.0
## Other substitution: 1.0
##

########
DEFINES
########

VERSION 2             # 0|1|2 (default: 0)

TOP 65535             # output maximum (default: 65535)

SUBSTMAX 2.1          # maximum for a substitution; larger values are cut off (default: 1)

INDEL 1.0             # indel, if not specified otherwise (default: .5 * SUBSTMAX)

METHOD SUM            # SUM|SQUARE|EUCLID|(MINKOWSKI value)  (default: SUM)

TOKENSTRING RAW       # RAW|ESC (default: RAW)

START 0               # STATE at start of string (default: 0)

RANGE 0.01 0.99 0.5   # everything in range 0.01:0.99 will be set to 0.5
RANGE 1 50 1          # everything in range 1:50 will be set to 1
RANGE 50 1000 2       # everything in range 50:1000 will be set to 2

########
FEATURES
########

# This file uses VERSION 2 (see DEFINES above)

# VERSION 0
# B|N|D label
# B|N|D weight label

# VERSION 1 and VERSION 2
# B|N|D default_diff label
# B|N|D default_diff weight label

# B : bitmap   (integer)
# N : numeric  (float)
# D : discrete (integer numbers)

B 1 100 type
D 1 1 id

''')


    fbrack = ''
    for i in sorted(bracket1):
        j = ord(i)
        fp.write('N 1 0.02 brack{0:04X}\n'.format(j))
        fbrack += '\nF brack{0:04X} = 0\n: {1} F brack{0:04X} = 1'.format(j, _brackopen[i])

    for i in sorted(modifiers):
        fp.write('N 1 0.02 mod{0:04X}\n'.format(ord(i)))


    fp.write('''
########
TEMPLATES
########

T vowel
F type = 1{0}
F STATE + 1

T consonant
F type = 2{0}
F STATE + 1

T semivowel
F type = 3{0}
F STATE + 1

T stress
F type = 255{0}
F INDEL = 0.5
F STATE - 1

T punctuation
F type = 255{0}
F INDEL = 0.5
F STATE - 1

T unknown
F type = 255{0}
F STATE + 1

T mods
'''.format(fbrack))

    for i in sorted(modifiers):
        fp.write('F mod{:04X} = 0\n'.format(ord(i)))

    fp.write('''
########
INDELS
########

# (nothing)

########
TOKENS
########

# vowels

''')

    for i in sorted(vowels):
        fp.write('H {}\nT vowel mods\nF id = {}\n\n'.format(i, ord(i)))

    fp.write('# consonants\n\n')
    for i in sorted(consonants):
        fp.write('H {}\nT consonant mods\nF id = {}\n\n'.format(i, ord(i)))

    fp.write('# semivowels\n\n')
    for i in sorted(semivowels):
        fp.write('H {}\nT semivowel mods\nF id = {}\n\n'.format(i, ord(i)))

    fp.write('# stress\n\n')
    for i in sorted(stresses):
        fp.write('H {}\nT stress mods\nF id = {}\n\n'.format(i, ord(i)))

    fp.write('# punctuation\n\n')
    for i in sorted(punctuations):
        fp.write('H {}\nT punctuation mods\nF id = {}\n\n'.format(i, ord(i)))

    fp.write('# unknown\n\n')
    for i in sorted(unknowns):
        if i == ' ':
            fp.write('H [[SP]]\nT unknown mods\nF id = 32\n\n')
        else:
            fp.write('H {}\nT unknown mods\nF id = {}\n\n'.format(i, ord(i)))

    fp.write('# modifiers\n\n')
    for i in sorted(modifiers):
        fp.write(': 1 M {}\nF mod{:04X} + 1\n\n'.format(i, ord(i)))

    if bracket1:
        fp.write('# opening brackets\n\n')
        for i in sorted(bracket1):
            fp.write('^: {1} P {0}\nF STATE - 1\nF STATE + {1}\n\n'.format(i, _brackopen[i]))

    if bracket2:
        fp.write('# closing brackets\n\n')
        for i in sorted(bracket2):
            fp.write(': {} M {}\nF STATE - {}\n\n'.format(_brackclose[i], i, (_brackclose[i] + 1)))

    if bracket1 or bracket2:
        fp.write('# END OF TEXT\n\n')
        fp.write('^: 240 EOT\n\n')

    fp.close()

