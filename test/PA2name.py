#!/usr/bin/env python3

import sys

PA = b'''
PA1
PA2
PA3
PA4
PA5
PA6
PA7
PA8
PA9
PA10
PA11
PA12
PA13
PA14
PA15
PA16
PA17
PA18
PA19
PA20
PA21
PA22
PA23
PA24
PA25
PA26
PA27
PA28
PA29
PA30
PA31
PA32
PA33
PA34
PA35
PA36
PA37
PA38
PA39
PA40
PA41
PA42
PA43
PA44
PA45
PA46
PA47
PA48
PA49
PA50
PA51
PA52
PA53
PA54
PA55
PA56
PA57
PA58
PA59
PA60
PA61
PA62
PA63
PA64
PA65
PA66
PA67
'''.split()

names = b'''
Philadelphia
Bucks
Montgomery
Delaware
Chester
Berks
Lancaster
York
Dauphin
Lebanon
Northumberland
Montour
Columbia
Schuylkill
Luzerne
Carbon
Lehigh
Northampton
Monroe
Pike
Wayne
Lackawanna
Susquehanna
Wyoming
Sullivan
Bradford
Tioga
Lycoming
Clinton
Potter
Cameron
Centre
Blair
Huntingdon
Mifflin
Union
Snyder
Juniata
Perry
Cumberland
Adams
Franklin
Fulton
Bedford
Somerset
Fayette
Greene
Washington
Westmoreland
Allegheny
Pittsburgh
Beaver
Lawrence
Butler
Mercer
Venango
Clarion
Armstrong
Jefferson
Indiana
Cambria
Clearfield
Elk
McKean
Warren
Crawford
Erie
'''.split()

tr = {}
for i in range(len(PA)):
    tr[PA[i]] = names[i]

for line in sys.stdin.buffer.readlines():
    if line.startswith(b'PA'):
        a = line.split(b'\t', 1)
        line = tr[a[0]] + b'\t' + a[1]
    sys.stdout.buffer.write(line)
