#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
--documentation--
"""

__author__ = "Peter Kleiweg"
__version__ = "0.1"
__date__ = "2010/06/09"

#| imports

import os, sys

#| globals

#| functions

#| main

Vowel = set('A E I O U Y a e i o u y'.split())
Consonant = set('B C D F G H J K L M N P Q R S T V W X Z b c d f g h k l m n p q r s t v x z'.split())
Semivowel = set('w ɥ ʋ ɹ ɻ j ɰ ɚ ɝ'.split())
Stress = set('ˌ ˈ'.split())
Modifier = set()
Punctuation = set(['{:c}'.format(i) for i in [0x002D, 0x002E, 0x007C, 0x00AD, 0x035C, 0x0361, 0x2016]])
Bracket1 = set('{ [ ('.split())
Bracket2 = set('} ] )'.split())

# 00C0 - 00FF
Vowel.update(set(
    'À Á Â Ã Ä Å Æ È É Ê Ë Ì Í Î Ï Ò Ó Ô Õ Ö Ø Ù Ú Û Ü Ý à á â ã ä å æ è é ê ë ì í î ï ò ó ô õ ö ø ù ú û ü ý ÿ'.split()))
Consonant.update(set(
    'Ç Ð Ñ Þ ß ç ð ñ þ'.split()))

# 0100 - 017F
Vowel.update(set(
    'Ā ā Ă ă Ą ą Ē ē Ĕ ĕ Ė ė Ę ę Ě ě Ĩ ĩ Ī ī Ĭ ĭ Į į İ ı Ĳ ĳ Ō ō Ŏ ŏ Ő ő Œ œ Ũ ũ Ū ū Ŭ ŭ Ů ů Ű ű Ų ų Ŷ ŷ'.split()))
Consonant.update(set(
    'Ć ć Ĉ ĉ Ċ ċ Č č Ď ď Đ đ Ĝ ĝ Ğ ğ Ġ ġ Ģ ģ Ĥ ĥ Ħ ħ Ĵ ĵ Ķ ķ ĸ Ĺ ĺ Ļ ļ Ľ ľ Ŀ ŀ Ł ł Ń ń Ņ ņ Ň ň ŉ Ŋ ŋ Ŕ ŕ Ŗ ŗ Ř ř Ś ś Ŝ ŝ Ş ş Š š Ţ ţ Ť ť Ŧ ŧ Ŵ ŵ Ź ź Ż ż Ž ž ſ'.split()))

Consonant.update(set(['{0:c}'.format(0x2C71)]))


# 0180 - 01FF
Consonant.update(set(['{0:c}'.format(i) for i in range(0x01C0, 0x01C4)]))

# 0025 - 02AF  IPA Extensions

Vowel.update(set(
    'ɐ ɑ ɒ ɔ ɘ ə ɛ ɜ ɞ ɤ ɨ ɩ ɪ ɯ ɵ ɶ ɷ ʉ ʊ ʌ ʏ ʚ '.split()))
Consonant.update(set(
    'ɓ ɕ ɖ ɗ ɟ ɠ ɡ ɢ ɣ ɦ ɧ ɫ ɬ ɭ ɮ ɱ ɲ ɳ ɴ ɸ ɺ ɼ ɽ ɾ ɿ ʀ ʁ ʂ ʃ ʄ ʅ ʆ ʇ ʈ ʍ ʎ ʐ ʑ ʒ ʓ ʔ ʕ ʖ ʗ ʘ ʙ ʛ ʜ ʝ ʞ ʟ ʠ ʡ ʢ ʣ ʤ ʥ ʦ ʧ ʨ ʩ ʪ ʫ ʬ ʭ ʮ ʯ'.split()))

# 0370 - 0377   Greek and Coptic
Consonant.update(set(['{0:c}'.format(i) for i in (0x03B2, 0x03B8, 0x03C7)]))

# 1D00 - 1D7F   Phonetic Extensions

Vowel.update(set(['{0:c}'.format(i) for i in (0x1D7B, 0x1D7F)]))
Consonant.update(set(['{0:c}'.format(i) for i in (0x1D6C, 0x1D6D, 0x1D6E, 0x1D6F, 0x1D70, 0x1D71, 0x1D72, 0x1D73, 0x1D74, 0x1D75, 0x1D76)]))

# 2000 - 206F   General Punctuation
Punctuation.update(set('{0:c}'.format(0x2060)))

# 2070 - 209F   Superscripts and Subscripts
Modifier.update(set('{0:c}'.format(0x207F)))

# 2190 - 21FF   Arrows
Modifier.update(set(['{0:c}'.format(i) for i in (0x2191, 0x2193, 0x2197, 0x2198)]))


# Modifier Tone Letters
Modifier.update(set(['{0:c}'.format(i) for i in range(0xA700, 0xA720)]))

# Spacing Modifier Letters
Modifier.update(set(['{0:c}'.format(i) for i in range(0x02B0, 0x0300)]))

# Combining Diacritical Marks
Modifier.update(set(['{0:c}'.format(i) for i in range(0x0300, 0x0370)]))

# Combining Diacritical Marks Supplement
Modifier.update(set(['{0:c}'.format(i) for i in range(0x1DC0, 0x1E00)]))

# Combining Half Marks
Modifier.update(set(['{0:c}'.format(i) for i in range(0xFE20, 0xFE27)]))


Modifier.difference_update(Stress)
Modifier.difference_update(Punctuation)


def cc(c):

    if c in Vowel:
        return 'V'
    if c in Semivowel:
        return 'S'
    if c in Consonant:
        return 'C'
    if c in Modifier:
        return 'M'
    if c in Stress:
        return 'X'
    if c in Punctuation:
        return 'P'
    if c in Bracket1:
        return '1'
    if c in Bracket2:
        return '2'
    return 'U'

def ci(i):
    return cc('{:c}'.format(i))

#| if main

if __name__ == "__main__":

    import unicodedata

    fp = sys.stdout.detach()
    def write(s):
        fp.write(s.encode('utf-8'))

    write('\nhttp://www.unicode.org/charts/\n\n')

    write('See further below for list ordered by character code\n\n')

    write('=' *  64 + '\n\n')

    setts = [('Vowels', Vowel),
             ('Consonants', Consonant),
             ('Semivowels', Semivowel),
             ('Stress', Stress),
             ('Punctuation', Punctuation),
             ('Modifiers', Modifier),
             ('Bracket Open', Bracket1),
             ('Bracket Close', Bracket2)]

    for i in range(len(setts)):
        write(setts[i][0] + ' :\n\n')
        for c in sorted(setts[i][1]):
            write('{0:04X}  {0:c}  {1}\n'.format(ord(c), unicodedata.name(c, '')))
        write('\n')

    write('=' *  64 + '\n\n')

    write('V = vowel, C = consonant, S = semivowel, X = stress, P = punctuation\n')
    write('M = modifier, 1 = Bracket Open, 2 = Bracket Close\n\n')

    a = set()
    for i, j in setts:
        a.update(j)
    for c in sorted(a):
        write('{2}  {0:04X}  {0:c}  {1}\n'.format(ord(c), unicodedata.name(c, ''), cc(c)))
    write('\n')

    for i in range(len(setts)):
        for j in range(i):
            x = setts[i][1].intersection(setts[j][1])
            if x:
                write("Error: intersection not empty: {} - {}\n\n".format(setts[j][0], setts[i][0]))
