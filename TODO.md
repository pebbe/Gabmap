**Methods:**

<table border="1" cellpadding="4">
<tr><td> lev          <td>   String Edit Distance — Plain
<tr><td> levfeat-tok  <td>   String Edit Distance — Tokenized
<tr><td> levfeat-user <td>   String Edit Distance — User defined
<tr><td> bin          <td>   Binary comparison
<tr><td> giw          <td>   Gewichteter Identitätswert
<tr><td> num          <td>   Numeric distance — not normalised
<tr><td> numnorm      <td>   Numeric distance — normalised by column
<tr><td> dif          <td>   User supplied differences — Method unknown
</table>

Let op: Na belangrijke veranderingen testen met PA-euro om te zien of er
geen issues met tekensets zijn.

Algemeen

 * menu: edit account
 * kleine kans op conflict in plaatslabels, bijv. tussen &#8364; en euro
 * bij onderdelen, waar van toepassing, uitleg over hoe R in dat
   onderdeel is gebruikt, zodat gebruikers dit zelf ook kunnen doen

Inlogpagina

 * klaar?

Lijst met projecten + aanmaak nieuw project

 * help: Upload kml or kmz file
 * help: Pseudo maps
 * help: Disperse places that are too close to each other
 * help: Upload data file, onderaan: or unspecified 8-bit?
 * help: Type of data: meer uitleg?
 * help: Type of processing: String data
 * help: User Defined String edit distance
 * help: Type of processing: Numeric
 * help: Type of processing: Categorical
 * advanced optie wel of geen Cronbach’s alpha ook van toepassing bij
   numerieke data
 * advanced optie: andere projecties dan UTM
 * help als max projecten: verwijderen van een project
 * table of character classes is still incomplete
 * compare results of projects with identical places
 * bij dif data: NA’s bijwerken

Projectpagina

 * modify and add parts voor very small data sets

Index: places

 * blok: samenvattende koptekst
 * Download map files in L04 format
 * Let user select labels to add to map for printing.

Index: items (`lev*`, `bin`, `giw`)

 * meer uitleg voor kaart?

Index: items (`num*`)

 * meer uitleg voor kaart?

Data inspection: data overview (`lev*`, `bin`, `giw`)

 * blok: samenvattende koptekst
 * help: Overview
 * download data in L04 format : _/*.data labels.txt features.def
 * help: Character list
 * help: Data sample search
 * help: Errors
 * help: Token list

Data inspection: data overview (`num*`)

 * blok: samenvattende koptekst
 * help: Overview
 * help: Box plots

Data inspection: data overview (`dif`)

 * moet helemaal nog
 * blok: samenvattende koptekst

Data inspection: distribution maps (`lev*`, `bin`, `giw`)

 * blok: samenvattende koptekst

Data inspection: value maps (`num*`)

 * blok: samenvattende koptekst

Measuring technique: alignments (`lev*`)

 * blok: samenvattende koptekst

Differences: statistics and difference maps

 * blok: samenvattende koptekst
 * error: Error in plot.window(xlim, ylim, "") : need finite `ylim' values
 * other data overview and analyses
 * help: uitleg bij grafieken

Differences: linguistic difference <-> geographic distance (niet: pseudomap)

 * blok: samenvattende koptekst
 * help: uitleg bij falen van plot met asymptoot
 * help: uitleg bij grafieken
 * use circles instead of dots for very small data sets
 * meer uitleg over R: ook hoe de modellen te gebruiken

Differences: reference point maps

 * blok: samenvattende koptekst
 * methodes: meer? minder?
 * scaling of colors uniform for all places, instead of maximized for a single place?
 * uitleg bij plot: muis over cirkels voor label

Multidimensional Scaling: mds plots

 * blok: samenvattende koptekst (ook: muis over cirkels voor labels)
 * uitleg bij plot: betekenis van blauwe pijlen (procrustes?)
 * uitleg bij plot: correlatie
 * MDS with Kruskal’s method?

Multidimensional Scaling: mds maps

 * blok: samenvattende koptekst
 * uitleg over correlatie en stress
 * error: Error in nls(dif ~ a + b * geo/(c + geo), start = list(a = a,
   b = b, c = c), : step factor 0.000488281 reduced below ‘minFactor’ of
   0.000976562

Discrete clustering: cluster maps and dendrograms

 * blok: uitgebreidere samenvattende koptekst
 * help bij opties
 * error: Error clgroup: Too many groups
 * statistical evaluation of clusters
 * let users define a legend

Discrete clustering: cluster validation

 * help: uitleg over correlatie
 * help: iets over procrustes?
 * MDS with Kruskal’s method?
 * a method to mark places in the map by selecting them from the plot
 * make the use of options more intuitive (now: multiple forms, each for
   a single option)
 * option, black/white: small symbols / large symbols
 * statistical evaluation of clusters

Fuzzy clustering: probabilistic dendrogram

 * blok: samenvattende koptekst
 * help: uitleg over de methode + literatuurverwijzing
 * help: uitleg bij opties
 * To do’s in bin/p/prob.py

Fuzzy clustering: fuzzy cluster maps

 * blok: samenvattende koptekst
 * help: uitleg over de methode

Data mining: cluster determinants (`lev*`, `bin`, `giw`)

 * maak van beta een optie
 * help: adjusted Fbeta score i.p.v. F1 score
 * [optie: minimum occurence of pattern, 1 to 4 (now fixed at 2)]
 * [optie: Normalise values in distribution maps? Currently: no]
 * [optie: meerdere clusters tegelijk selecteren]
 * help: uitleg over score
 * help: intro over raw data en localised data
 * help: uitleg over het algoritme voor het vinden van de optimale set
   van varianten. zie: http://www.gabmap.nl/~app/bin/help?s=cludetselect
 * error: Error clgroup: Too many groups
 * bijwerken: doc/ClusterDeterminants/
 * automatische extractie van kenmerken? (doorsnedes en disjuncties van
   reguliere expressie, of een leermethode met positieve/negatieve
   patronen als trainingsdata)

Data mining: cluster determinants (`num*`)

 * waardebereiken als patronen?

Tools

 * [Something to fix non-Latin1 characters in figures]
 * [Download kml-file of a single country, extracted from
   http://www.gabmap.nl/~app/examples/world-countries.kmz]

Implementatie

 * Alle tekstbestanden hernoemen: *-a.txt voor us-ascii, *-1.txt voor
   iso-8858-1, *-u.txt voor utf-8

Overigen

 * Handleiding schrijven voor downloaden en installeren van de software
   vanaf github
 * Admin guide
   + crontab

- - -

**Old to do list**

to do: see what is still useful, delete the rest

 * Other stuff, plans/suggestions:
  + factor analysis (examples)
  + correlation with known factors, normalisation for known factors
  + normalisation for major clusters, read more
  + semi-local difference map (mexican hat) (examples)
  + vector map (example) and contrast map (read more)
  + cophenetic correlation coefficient (?)
  + other cluster validation methods
  + svd? lsa? (examples)
  + more...

 * handleiding op gabmap.nl: gebruiker moet juiste fonts hebben in de browser

 * wat te doen als mensen data uploaden met maar een paar plaatsen?

 * http://www.let.rug.nl/p04/ off-line halen?

 * te veel gebruikers tegelijk, dan ‘make’-processen niet tegelijk
   draaien, maar na elkaar. Is dit nodig? Ja, dat is nodig.
  + Taakvolgorde, als meerdere gebruikers tegelijk actief zijn, moet anders.
  + Nu is volgorde: user 1 taak 1, user 1 taak 2, user 1 taak 3…. user 2 taak 1, user 2 taak 2…
  + Volgorde moet worden: user 1 taak 1, user 2 taak 1, user 3 taak 1… user 1 taak 2, user 2 taak 2…

 * als een project verwijderd wordt moet eerst de queue voor dat project worden
   verwijderd

 * bij guest-accounts: waarschuwing dat data na twee dagen verwijderd wordt

 * [done] pyproj installeren onder Python 3.1
  + diffs in temp/pyproj.patch toepassen
  + compileren met:
    <pre>
        cython _geod.pyx
        cython _proj.pyx
        python3 setup.py install
    </pre>
  + testen met: `python3 __init.py__`

 * volledig overschakelen op Python3 als alle library’s beschikbaar zijn

 * invoer van data als xml, naast comma-separated values
  + ervan uitgaande dat er een xml-standaard komt voor het opslaan van dialectdata
  + zie Dialectdata in XML http://www.let.rug.nl/alfa/adept/?p=166

 * kml2l04 (drie versies: web, stand-alone, onderdeel van webapp)
  + poolprojecties? lijkt me niet echt nodig
  + kaarten zonder polygonen
  + [done] hulpmiddel om lijst met coördinaten + plaatsnamen om te zetten in kml
  + moeten we eigenlijk wel alleen op kml vertrouwen? blijven tools om
    makkelijk kml te maken vrij beschikbaar? is kml stabiel?

 * [done] gebruiker (en alle data) verwijderen als gebruiker 60 dagen niet is ingelogd.
  + zet dit in crontab (path naar INIT.sh aanpassen):
    <pre>
        0 3 * * * ( source $HOME/public_html/L04/webapp/bin/INIT.sh ; rmoldusers )
    </pre>

 * wat te doen bij beperkte schijfruimte?
  + .eps → .eps.gz

 * gebruik: ulimit -v
  + grotendeels gedaan, maar moet nog verder getest worden
  + als ‘leven’ met cronbach alpha faalt (out of memory), dan opnieuw
    zonder cronbach alpha. Zal zelden voorkomen, omdat ‘leven’ zelf al
    probeert door te gaan zonder cronbach alpha, als het in
    geheugenproblemen komt.
  + idem voor ‘giw’ (nog niet gedaan)

 * bij nieuw project: automatische detectie van tekenset van datatabel
  + <s>default: iso-8859-1 (aanname voor elke 8-bits tekenset)</s>
  + <s>us-ascii</s>
  + <s>utf-8 met/zonder BOM</s>
  + <s>utf-16 met BOM</s>
  + utf-16 zonder BOM ???
  + wel of niet: x-sampa ???

 * gebruikershandleiding
  + schema van de webapplicatie: projectpagina als basis
  + tutorial met screencasts
  + weergave kleurkubus voor tutorial
  + cursusmateriaal
  + terms of use
  + gebruik van excel. waarschuwing: max 256 kolommen
  + ...

 * installatiehandleiding
  + systeemeisen
  + benodigde software

 * documentatie van de implementatie
  + voor een volgende beheerder

 * voor MDS-kaarten (en CCC-kaarten?): beter kleurgebruik. CIE?

 * een testprogramma dat kijkt of alles goed geïnstalleerd is, alle
   binary’s en library’s aanwezig zijn, de directory’s de juiste rechten
   hebben, of sys.stdout utf-8 is, etc.

 * een programma dat in de gaten houdt of alles goed blijft gaan met diskruimte
   en zo, draaien vanuit crontab

