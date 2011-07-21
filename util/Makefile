
.SUFFIXES:

all: agclus agden auleven auleven-r auleven-s determinants1 determinants1af determinants2 determinants2af smap

agclus: agclus.c
	gcc -s -Wall -o agclus agclus.c

agden: agden.c
	gcc -s -Wall -o agden agden.c

auleven: auleven.c
	gcc -s -Wall -o auleven auleven.c -lm

auleven-r: auleven.c
	gcc -DLEVEN_REAL -s -Wall -o auleven-r auleven.c -lm

auleven-s: auleven.c
	gcc -DLEVEN_SMALL -s -Wall -o auleven-s auleven.c -lm

determinants1: determinants1.c
	gcc -s -Wall -O2 -o determinants1 determinants1.c

determinants1af: determinants1af.c
	gcc -s -Wall -O2 -o determinants1af determinants1af.c

determinants2: determinants2.c
	gcc -s -Wall -O2 -o determinants2 determinants2.c -lm

determinants2af: determinants2af.c
	gcc -s -Wall -O2 -o determinants2af determinants2af.c -lm

smap: smap.c
	gcc -s -Wall -o smap smap.c -lm
