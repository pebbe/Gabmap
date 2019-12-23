/*
 * File: determinants2.c
 *
 * (c) Peter Kleiweg
 *     Mon Jun 20 13:15:31 2011
 *
 * This program is free software: you can redistribute it and/or modify
 * it under the terms of the GNU General Public License as published by
 * the Free Software Foundation, either version 3 of the License, or
 * (at your option) any later version.
 *
 * This program is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 * GNU General Public License for more details.
 *
 * You should have received a copy of the GNU General Public License
 * along with this program.  If not, see <http://www.gnu.org/licenses/>.
 *
 */

#define my_VERSION "0.93"

#define __NO_MATH_INLINES

#ifdef __WIN32__
#  define my_PATH_SEP '\\'
#else
#  define my_PATH_SEP '/'
#endif

#include <ctype.h>
#include <errno.h>
#include <math.h>
#include <search.h>
#include <stdarg.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>

#define BUFSIZE 4095

typedef struct {
    char
        *s,         /*  pattern                                   */
        **forms;    /*  original forms                            */
    int
        n_forms,    /*  number of different forms                 */
	max_forms,  /*  space avaiable for forms                  */
	ii,         /*  response count inside                     */
	oo,         /*  response count outside                    */
	rejected,
	used;
    double
	*i,         /*  counts per place, possibly interpolated   */
        AF,         /*  Adjusted F score                          */
	AP,         /*  Adjusted precision                        */
	AR;         /*  Adjusted recall                           */
} PATTERN_;

typedef struct {
    char
        *s;    /*  label  */
    int
        i;     /*  index  */
} LBLI_;

typedef struct {
    char
        *s;       /*  label */
    int
        inside,   /*  is this location within the target area?  */
	n;        /*  total response count for this location */
    double
        ni;       /*  if n > 0 then n else interpolated */
} LBLS_;

PATTERN_
    *patterns = NULL;

LBLI_
    *lbli = NULL;

LBLS_
    *lbls = NULL;

double
    **dst,
    *ppp,
    Beta = 0,
    Limit = 0,
    Sep = 0;

int
    nPlaces,
    nPlacesIn = 0,
    minvar = 2,
    utf = 0,
    dump = 0,
    n_patterns = 0,
    max_patterns = 0,
    n_valchars = 0,
    max_valchars = 0;

long
    lineno;

char
    buffer [BUFSIZE + 1],
    buffer2 [BUFSIZE + 1],
    buffer6 [BUFSIZE * 6 + 1],
    **valchars = NULL,
    *filename,
    *programname,
    *no_mem_buffer,
    out_of_memory [] = "Out of memory";

FILE
    *fp,
    *fp1,
    *fp2;

void
    insert(int),
    str2pattern (void),
    unquote (void),
    openread (char const *),
    get_programname (char const *argv0),
    errit (char const *format, ...),
    syntax (void),
    *s_malloc (size_t size),
    *s_realloc (void *block, size_t size);
char
    *s_strdup (char const *s),
    *escape (unsigned char *s);
int
    cmpstr (const void *, const void *),
    cmppat (const void *, const void *),
    cmppatstr (const void *, const void *),
    cmplbli (const void *, const void *),
    lfindpat (const void *, const void *),
    lfindform (const void *, const void *),
    GetLine (void);

int main (int argc, char *argv [])
{
    char
	c;
    int
	i,
	j,
	k,
	n,
	target,
	old_i,
	old_o;
    double
	d,
	sum1,
	sum2,
	TP,
	FP,
	FN,
	TN,
	P,
	R,
	AF,
	AP,
	AR,
	BP,
	BR,
	oldAF,
	oldAP,
	oldAR;
    LBLI_
	*p;

    no_mem_buffer = (char *) malloc (1024);

    get_programname (argv [0]);


    /* process args */

    if (argc > 1) {
	if (! strcmp (argv [1], "-d")) {
	    dump = 1;
	    argc--;
	    argv++;
	}
    }

    if (argc != 5)
	syntax ();

    Beta = atof (argv [2]);
    Limit = atof (argv [3]);
    Sep = atof (argv [4]);


    /* read data */

    openread ("data-1.txt");
    GetLine ();
    nPlaces = atoi (buffer);
    lbli = (LBLI_ *) s_malloc (nPlaces * sizeof (LBLI_));
    lbls = (LBLS_ *) s_malloc (nPlaces * sizeof (LBLS_));
    for (i = 0; i < nPlaces; i++) {
	GetLine ();
	sscanf (buffer, "%i %n", &j, &n);
	lbli [i].i = j;
	lbls [j].s = lbli [i].s = s_strdup (buffer + n);
	lbls [j].inside = 0;
	lbls [j].n = 0;
    }
    dst = (double **) s_malloc (nPlaces * sizeof (double *));
    for (i = 0; i < nPlaces; i++)
	dst [i] = (double *) s_malloc (nPlaces * sizeof (double));
    for (i = 0; i < nPlaces; i++) {
	dst [i][i] = 0.0;
	for (j = 0; j < i; j++) {
	    GetLine ();
	    dst [i][j] = dst [j][i] = atof (buffer);
	}
    }
    fclose (fp);

    if (access ("../data/UTF", F_OK) == 0)
	utf = 1;

    openread ("current");
    GetLine ();
    sscanf (buffer, " %i %i", &i, &target);
    fclose (fp);
    nPlacesIn = 0;
    openread ("clgroups.txt");
    while (GetLine ()) {
	sscanf (buffer, " %i%n", &i, &n);
	if (i != target)
	    continue;
	while (buffer [n] && isspace ((unsigned char) buffer [n]))
	    n++;
	memmove (buffer, buffer + n, strlen (buffer + n) + 1);
	unquote ();
	p = bsearch (buffer, lbli, nPlaces, sizeof (LBLI_), cmplbli);
	lbls[p->i].inside = 1;
	nPlacesIn++;
    }
    fclose (fp);

    if (utf)
	openread ("currentchars-u.txt");
    else
	openread ("currentchars-1.txt");
    while (GetLine ()) {
	if (n_valchars == max_valchars) {
	    max_valchars += 64;
	    valchars = (char **) s_realloc (valchars, max_valchars * sizeof (char *));
	}
	valchars [n_valchars++] = s_strdup (buffer);
    }
    fclose (fp);
    qsort (valchars, n_valchars, sizeof (char **), cmpstr);

    openread (argv [1]);
    while (GetLine ()) {
	if (buffer [0] == ':') {
	    for (j = 1; buffer [j] && isspace ((unsigned char) buffer [j]); j++)
		;
	    p = bsearch (buffer + j, lbli, nPlaces, sizeof (LBLI_), cmplbli);
	    i = p->i;
	} else if (buffer [0] == '-') {
	    for (j = 1; buffer [j] && isspace ((unsigned char) buffer [j]); j++)
		;
	    memmove (buffer, buffer + j, strlen (buffer + j) + 1);
	    insert (i);
	}
    }
    fclose (fp);


    /* process data */

    fp = stdout;


    /* skip file with data in too few places in target area */

    n = 0;
    for (i = 0; i < nPlaces; i++)
	if (lbls [i].inside && lbls [i].n)
	    n++;
    if (n < 3) {
	fprintf (fp, "\n0.00 0.00 0.00 0:0\n");
	return 0;
    }


    /* interpolate the total counts */

    for (i = 0; i < nPlaces; i++) {
	if (lbls [i].n) {
	    lbls [i].ni = lbls [i].n;
	    continue;
	}
	sum2 = 0;
	for (j = 0; j < nPlaces; j++)
	    if (lbls [j].n)
		sum2 += ((double) lbls [j].n) / pow (dst [i][j], Sep);
	lbls [i].ni = sum2;
    }


    /* score all patterens */

    /* Baseline precision */
    BP = ((double) nPlacesIn) / (double) nPlaces;

    for (i = 0; i < n_patterns; i++) {

	/* skip it if pattern is too rare */

	n = 0;
	for (j = 0; j < nPlaces; j++)
	    n += patterns [i].i [j];
	if (n < minvar)
	    continue;

	patterns [i].used = 1;


	/* interpolate for this pattern */

	for (j = 0; j < nPlaces; j++) {
	    if (lbls [j].n)
		continue;
	    sum1 = 0;
	    for (k = 0; k < nPlaces; k++)
		if (lbls [k].n)
		    sum1 += patterns [i].i [k] / pow (dst [j][k], Sep);
	    patterns [i].i [j] = sum1;
	}


	/* calculate scores for this pattern */

	TP = FP = FN = TN = 0.0;
	for (j = 0; j < nPlaces; j++) {
	    d = patterns [i].i [j] / lbls [j].ni;
	    if (lbls [j].inside) {
		TP += d;
		FN += 1.0 - d;
	    } else {
		FP += d;
		TN += 1.0 - d;
	    }
	}
	if (! TP) {
	    patterns [i].rejected = 1;
	    continue;
	}

 	P = TP / (TP + FP);
	R = TP / (TP + FN);
	BR = ((double)(TP + FP)) / (double)(nPlaces);
	AP = (P - BP) / (1.0 - BP);
	AR = (R - BR) / (1.0 - BR);
	if (AP > 0 && AR > 0)
	    AF = (AP + Beta * AR) / (1.0 + Beta);
	else
	    AF = 0.0;
	patterns [i].AF = AF;
	patterns [i].AP = AP;
	patterns [i].AR = AR;

    }


    /* see what patterns will be used, print them, and sum up values for total score */

    qsort (patterns, n_patterns, sizeof (PATTERN_), cmppat);

    ppp = (double *) s_malloc (nPlaces * sizeof (double));
    for (i = 0; i < nPlaces; i++)
	ppp[i] = 0.0;

    oldAF = oldAP = oldAR = 0.0;
    old_i = old_o = 0;
    for (i = 0; i < n_patterns; i++) {
	if (! patterns [i].used)
	    continue;

	/* add the counts of the patterns that are already accepted to the new candidate */
	for (j = 0; j < nPlaces; j++)
	    patterns [i].i [j] += ppp [j];

	/* calculate what the score with the new candidate would be */
	TP = FP = FN = TN = 0.0;
	for (j = 0; j < nPlaces; j++) {
	    d = patterns [i].i [j] / lbls [j].ni;
	    if (lbls[j].inside) {
		TP += d;
		FN += 1 - d;
	    } else {
		FP += d;
		TN += 1 - d;
	    }
	}
 	P = TP / (TP + FP);
	R = TP / (TP + FN);
	BR = ((double)(TP + FP)) / (double)(nPlaces);
	AP = (P - BP) / (1.0 - BP);
	AR = (R - BR) / (1.0 - BR);
	if (AP > 0 && AR > 0)
	    AF = (AP + Beta * AR) / (1.0 + Beta);
	else
	    AF = 0.0;

	/* does this pattern increase the score enough? */
	if (AF < oldAF * Limit) {
	    patterns [i].rejected = 1;
	    continue;
	}

	/* use it, save the updated counts and the new score */
	oldAF = AF;
	oldAP = AP;
	oldAR = AR;
	old_i += patterns [i].ii;
	old_o += patterns [i].oo;
	for (j = 0; j < nPlaces; j++)
	    ppp [j] = patterns [i].i [j];
	fprintf (fp, "%.2f %.2f %.2f %s %i:%i",
		 patterns [i].AF,
		 patterns [i].AP,
		 patterns [i].AR,
		 escape ((unsigned char *) patterns [i].s),
		 patterns [i].ii,
		 patterns [i].ii + patterns [i].oo);
	c = '[';
	for (j = 0; j < patterns[i].n_forms; j++) {
	    fprintf (fp, " %c %s", c, escape((unsigned char *) patterns[i].forms[j]));
	    c = '|';
	}
	fprintf (fp, " ]\n");
    }

    /* print the rejected patterns */

    qsort (patterns, n_patterns, sizeof (PATTERN_), cmppatstr);

    for (i = 0; i < n_patterns; i++)
	if (patterns [i].rejected)
	    printf ("[%s %i:%i]\n",
		    escape((unsigned char *) patterns [i].s),
		    patterns [i].ii,
		    patterns [i].ii + patterns [i].oo);


    /* print the total score */

    fprintf (fp, "\n%.2f %.2f %.2f %i:%i\n", oldAF, oldAP, oldAR, old_i, old_i + old_o);


    
    /* write dump files for maprgb -r */

    if (! dump)
	return 0;

    fp1 = fopen ("dump1.rgb", "w");
    fp2 = fopen ("dump2.rgb", "w");
    fprintf (fp1, "3\n");
    fprintf (fp2, "3\n");
    for (i = 0; i < nPlaces; i++) {
        fprintf (fp1, "%s\n", lbls [i].s);
        fprintf (fp2, "%s\n", lbls [i].s);
        d = 1.0 - ppp[i] / lbls [i].ni;
        if (lbls [i].n > 0)
	    fprintf (fp1, "%f\n%f\n%f\n", d, d, d);
        else
            fprintf (fp1, "1\n.5\n.5\n");
        fprintf (fp2, "%f\n%f\n%f\n", d, d, d);
    }
    fclose (fp1);
    fclose (fp2);

    fprintf (stderr, "Wrote 'dump1.rgb' and 'dump2.rgb'\n");


    return 0;
}

void errit (char const *format, ...)
{
    va_list
	list;

    fprintf (stderr, "\nError %s: ", programname);

    va_start (list, format);
    vfprintf (stderr, format, list);

    fprintf (stderr, "\n\n");

    exit (1);
}

void get_programname (char const *argv0)
{
#ifdef __MSDOS__
    char
        name [MAXFILE];
    fnsplit (argv0, NULL, NULL, name, NULL);
    programname = strdup (name);
#else
    char
        *p;
    p = strrchr (argv0, my_PATH_SEP);
    if (p)
        programname = strdup (p + 1);
    else
        programname = strdup (argv0);
#endif
}

void *s_malloc (size_t size)
{
    void
	*p;

    p = malloc (size);
    if (! p) {
        free (no_mem_buffer);
	errit (out_of_memory);
    }
    return p;
}

void *s_realloc (void *block, size_t size)
{
    void
	*p;

    p = realloc (block, size);
    if (! p) {
        free (no_mem_buffer);
	errit (out_of_memory);
    }
    return p;
}

char *s_strdup (char const *s)
{
    char
	*s1;

    if (s) {
	s1 = (char *) s_malloc (strlen (s) + 1);
	strcpy (s1, s);
    } else {
	s1 = (char *) s_malloc (1);
	s1 [0] = '\0';
    }
    return s1;
}

void syntax ()
{
    fprintf (
	stderr,
	"\n"
	"Version " my_VERSION "\n"
	"\n"
	"Usage: %s datafile beta limit sepvalue\n"
	"\n"
	"Example: %s ../data/_/apple.data 1.05 1.02 3.0\n"
	"\n",
	programname,
	programname
    );
    exit (1);
}

void unquote()
{
    int
	i,
	j,
	n;

    n = strlen (buffer);
    if (n < 2)
	return;
    if (buffer [0] != '"' || buffer [n - 1] != '"')
	return;

    j = 0;
    for (i = 1; i < n - 1; i++) {
	if (buffer [i] == '\\')
	    i++;
	buffer [j++] = buffer [i];
    }
    buffer [j] = '\0';
}

void openread (char const *s)
{
    filename = s_strdup (s);
    lineno = 0;
    fp = fopen (filename, "r");
    if (! fp)
	errit ("Opening file \"%s\": %s", filename, strerror (errno));
}

int GetLine ()
{
    int
        i;

    /* there are no comment lines, and a line can have only a space, so just strip newline */
    for (;;) {
        lineno++;
        if (fgets (buffer, BUFSIZE, fp) == NULL)
	    return 0;

        i = strlen (buffer);
        while (i > 0 && (buffer [i - 1] == '\n' || buffer [i - 1] == '\r'))
            buffer [--i] = '\0';

        if (buffer [0] == '\0')
	    continue;

        return 1;
    }
}

int cmpstr (const void *p1, const void *p2)
{
    return strcmp (*((char **)p1), *((char **)p2));
}

int cmppat (void const *p1, void const *p2)
{
    double
	f1,
	f2;
    f1 = ((PATTERN_ *)p1)->AF;
    f2 = ((PATTERN_ *)p2)->AF;
    if (f1 > f2)
	return -1;
    if (f1 < f2)
	return 1;
    return 0;
}

int cmppatstr (void const *p1, void const *p2)
{
    return strcmp (((PATTERN_ *)p1)->s, ((PATTERN_ *)p2)->s);
}

int cmplbli (void const *key, void const *p)
{
    return strcmp ((char *) key, ((LBLI_ *)p)->s);
}

int cmpchr (void const *key, void const *p)
{
    return strcmp ((char *) key, *((char **)p));
}

int lfindpat (void const *key, void const *p)
{
    return strcmp ((char *) key, ((PATTERN_ *)p)->s);
}

int charlen (char c) {
    int
	i;

    if (! utf)
	return 1;

    i = (unsigned char) c;
    if (i <= 0x7F) return 1;
    if (i <= 0xDF) return 2;
    if (i <= 0xEF) return 3;
    if (i <= 0xF7) return 4;
    if (i <= 0xFB) return 5;
    if (i <= 0xFD) return 6;

    errit ("Invalid UFF-8 character");
    return 0;
}

void str2pattern ()
{
    char
	chr [10];
    int
	i,
	j,
	n;

    j = 0;
    for (i = 0; buffer [i]; i += n) {
	n = charlen (buffer [i]);
	memcpy (chr, buffer + i, n);
	chr [n] = '\0';
	if (bsearch (chr, valchars, n_valchars, sizeof (char *), cmpchr)) {
	    memcpy (buffer2 + j, buffer + i, n);
	    j += n;
	}
    }
    buffer2[ j] = '\0';
}

void insert(int idx)
{
    int
	i;
    size_t
	nmemb;
    PATTERN_
        *p;
    char
	**p2;

    str2pattern ();

    nmemb = n_patterns;
    p = lfind (buffer2, patterns, &nmemb, sizeof (PATTERN_), lfindpat);
    if (! p) {
	if (n_patterns == max_patterns) {
	    max_patterns += 32;
	    patterns = (PATTERN_ *) s_realloc (patterns, max_patterns * sizeof (PATTERN_));
	}
	patterns [n_patterns].forms = NULL;
	patterns [n_patterns].s = s_strdup (buffer2);
	patterns [n_patterns].n_forms = 0;
	patterns [n_patterns].max_forms = 0;
	patterns [n_patterns].rejected = 0;
	patterns [n_patterns].used = 0;
	patterns [n_patterns].ii = 0;
	patterns [n_patterns].oo = 0;
	patterns [n_patterns].i = (double *) s_malloc (nPlaces * sizeof (double));
	for (i = 0; i < nPlaces; i++)
	    patterns [n_patterns].i [i] = 0.0;
	p = &(patterns [n_patterns]);
	n_patterns++;
    }

    p->i[idx] += 1.0;
    lbls[idx].n++;
    if (lbls[idx].inside)
	p->ii++;
    else
	p->oo++;

    p2 = NULL;
    if (p->n_forms > 0) {
	nmemb = p->n_forms;
	p2 = lfind (buffer, p->forms, &nmemb, sizeof (char *), cmpchr);
    }
    if (! p2) {
	if (p->n_forms == p->max_forms) {
	    p->max_forms += 32;
	    p->forms = (char **) s_realloc (p->forms, p->max_forms * sizeof (char *));
	}
	p->forms[p->n_forms] = s_strdup (buffer);
	p->n_forms++;
    }

}

void bytescheck (unsigned char *s, int n)
{
    int
        i;
    for (i = 0; i < n; i++)
        if (! s [i])
            errit ("Invalid utf-8 code in %s, line %li", filename, lineno);
}

long unsigned bytes2 (unsigned char *s)
{

    long unsigned
        c;

    bytescheck (s, 2);

    c =   ( s [1] & 0x3F)
        | ((s [0] & 0x1F) << 6);

    return c;

}

long unsigned bytes3 (unsigned char *s)
{

    long unsigned
        c;

    bytescheck (s, 3);

    c =   ( s [2] & 0x3F)
        | ((s [1] & 0x3F) <<  6)
        | ((s [0] & 0x0F) << 12);

    return c;

}

long unsigned bytes4 (unsigned char *s)
{

    long unsigned
        c;

    bytescheck (s, 4);

    c =   ( s [3] & 0x3F)
        | ((s [2] & 0x3F) <<  6)
        | ((s [1] & 0x3F) << 12)
        | ((s [0] & 0x07) << 18);

    return c;

}

long unsigned bytes5 (unsigned char *s)
{

    long unsigned
        c;

    bytescheck (s, 5);

    c =   ( s [4] & 0x3F)
        | ((s [3] & 0x3F) <<  6)
        | ((s [2] & 0x3F) << 12)
        | ((s [1] & 0x3F) << 18)
        | ((s [0] & 0x03) << 24);

    return c;

}

long unsigned bytes6 (unsigned char *s)
{

    long unsigned
        c;

    bytescheck (s, 6);

    c =   ( s [5] & 0x3F)
        | ((s [4] & 0x3F) <<  6)
        | ((s [3] & 0x3F) << 12)
        | ((s [2] & 0x3F) << 18)
        | ((s [1] & 0x3F) << 24)
        | ((s [0] & 0x01) << 30);

    return c;

}

char *escape (unsigned char *s)
{
    int
	i,
	j,
	n;
    unsigned long
	c;

    j = 0;

    for (i = 0; s [i]; i += n) {
	n = charlen (s[i]);

	switch (n){
	    case 1: c = (unsigned char) s [i]; break;
  	    case 2: c = bytes2 (s + i); break;
  	    case 3: c = bytes3 (s + i); break;
  	    case 4: c = bytes4 (s + i); break;
  	    case 5: c = bytes5 (s + i); break;
  	    case 6: c = bytes6 (s + i); break;
	    default: c = 32;
	}

	if (c == 43 || c == 45 || (c >= 48 && c <= 57) || (c >= 65 && c <= 90) || (c >= 97 && c <= 122))
	    buffer6[j++] = (char) c;
	else {
	    sprintf (buffer6 + j, "_%lu_", c);
	    for ( ; buffer6 [j]; j++)
		;
	}
    }

    if (! j) {
	buffer6 [j++] = '_';
	buffer6 [j++] = '_';
    }

    buffer6 [j] = '\0';

    return buffer6;

}
