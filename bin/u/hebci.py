#!/usr/bin/env python3
"""
--documentation--
"""

__author__ = "Peter Kleiweg"
__version__ = "0.1"
__date__ = "2010/05/02"

#| imports

#| globals

#| functions

def hebci(e):

    # ORDER IS IMPORTANT

    # utf
    if e['euro'] == b'\xe2\x82\xac': return 'utf_8'

    # antiek: cp437 en dergelijke
    if e['auml'] == b'\x84':
        if e['thorn' ] == b'\xe7': return 'cp850'
        if e['thorn' ] == b'\x95': return 'cp861'
        if e['Scaron'] == b'\xe6': return 'cp852'
        if e['Scaron'] == b'\xbe': return 'cp775'
        if e['sect'  ] == b'\xf5': return 'cp857'
        if e['oslash'] == b'\x9b': return 'cp865'
        return 'cp437'

    # windows
    if e['euro'] == b'\x88':  return 'cp1251'
    if e['euro'] == b'\x80':
        if e['thorn'] == b'\xfe':    return 'cp1252'
        if e['Scaron'] == b'\xd0':   return 'cp1257'
        if e['divide'] == b'\xba':   return 'cp1255'
        if e['Scaron'] == b'\x8a':
            if e['oelig'] == b'\x9c': return 'cp1254'
            return 'cp1250'
        if e['auml'] == b'\xe4':    return 'cp1258'
        if e['divide'] == b'\xf7':   return 'cp1256'
        return 'cp1253'

    # mac
    if e['divide'] == b'\xd6':
        if e['euro'] == b'\x9c':   return 'mac_greek'
        if e['euro'] == b'\xdb':
            if e['thorn'] == b'\xdf': return 'mac_iceland'
            return 'mac_roman'
        if e['euro'] == b'\xff':   return 'mac_cyrillic'
        if e['Scaron'] == b'\xe1': return 'mac_latin2'
        return 'mac_turkish'

    # koi8
    if e['divide'] == b'\x9f':
        # assume koi8_u, but could also be koi8_r
        return 'koi8_u'

    # iso-8859
    if e['euro'] == b'\xa4':
        if e['divide'] == b'\xf7': return 'iso8859_15'
        return 'iso8859_7'
    if e['divide'] == b'\xba': return 'iso8859_8'
    if e['Scaron'] == b'\xaa': return 'iso8859_10'
    if e['Scaron'] == b'\xd0': return 'iso8859_13'
    if e['sect'] == b'\xfd': return 'iso8859_5'
    if e['middot'] == b'\xb7':
        if e['thorn'] == b'\xfe': return 'latin_1'
        if e['oslash'] == b'\xf8': return 'iso8859_9'
        return 'iso8859_3'
    if e['oslash'] == b'\xf8':
        if e['Scaron'] == b'\xa9': return 'iso8859_4'
        return 'iso8859_14'
    if e['Scaron'] == b'\xa9': return 'iso8859_2'
    return 'iso8859_6'

def cp(data):
    e = {}
    for i in 'auml divide euro middot oelig oslash Scaron sect thorn'.split():
        e[i] = data.get('hebci_' + i, '')
    return hebci(e)

def _test():
    import html.entities
    cps = '''
    cp437 cp775 cp850 cp852 cp857 cp861 cp865
    cp1250 cp1251 cp1252 cp1253 cp1254 cp1255 cp1256 cp1257 cp1258
    latin_1 iso8859_2 iso8859_3 iso8859_4 iso8859_5 iso8859_6 iso8859_7
    iso8859_8 iso8859_9 iso8859_10 iso8859_13 iso8859_14 iso8859_15
    koi8_u
    mac_cyrillic mac_greek mac_iceland mac_latin2 mac_roman mac_turkish
    utf_8
    '''.split()

    ent = 'auml divide euro middot oelig oslash Scaron sect thorn'.split()
    chrs = []
    for e in ent:
        c = html.entities.entitydefs[e]
        chrs.append((e, c))
    for cp in cps:
        e = {}
        for en, ch in chrs:
            e[en] = ch.encode(cp, 'ignore')
        print(cp, '  \t', hebci(e))



#| if main

if __name__ == "__main__":
    _test()
