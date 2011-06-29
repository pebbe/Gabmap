/*
 * File: determinants1.c
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

#define my_VERSION "0.91"

#define __NO_MATH_INLINES

#ifdef __WIN32__
#  define my_PATH_SEP '\\'
#else
#  define my_PATH_SEP '/'
#endif

#include <ctype.h>
#include <errno.h>
#include <search.h>
#include <stdarg.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>

#define BUFSIZE 4095

typedef struct pattern_struct {
    char
        *s,         /*  pattern                    */
        **forms;    /*  original forms             */
    int
	n_forms,    /*  number of different forms  */
	max_forms,  /*  space avaiable for forms   */
	i,          /*  response count inside      */
	o,          /*  response count outside     */
	used,
	rejected;
    double
        I,          /*  Importance                 */
	R,          /*  Representativeness         */
	D;          /*  Distinctiveness            */
} PATTERN_;

PATTERN_
    *patterns = NULL;

double
    Limit;

int
    minvar = 2,
    utf = 0,
    n_patterns = 0,
    max_patterns = 0,
    n_targets = 0,
    max_targets = 0,
    n_valchars = 0,
    max_valchars = 0;

long
    lineno;

char
    buffer [BUFSIZE + 1],
    buffer2 [BUFSIZE + 1],
    buffer6 [BUFSIZE * 6 + 1],
    **targets = NULL,
    **valchars = NULL,
    *filename,
    *programname,
    *no_mem_buffer,
    out_of_memory [] = "Out of memory";

FILE
    *fp;

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
    searchcmp (const void *, const void *),
    lfindpat (const void *, const void *),
    lfindform (const void *, const void *),
    GetLine (void);

int main (int argc, char *argv [])
{
    char
	c;
    int
	allinn,
	allout,
	bias,
	i,
	j,
	n,
	o,
	old_i,
	old_o,
	intarget,
	target;
    double
	I,
	R,
	D,
	RO,
	RS,
	oldI,
	oldR,
	oldD;

    no_mem_buffer = (char *) malloc (1024);

    get_programname (argv [0]);


    /* process args */

    if (argc != 3)
	syntax ();

    Limit = atof (argv [2]);


    /* read data */

    if (access ("../data/UTF", F_OK) == 0)
	utf = 1;

    openread ("current");
    GetLine ();
    sscanf (buffer, " %i %i", &i, &target);
    fclose (fp);
    openread ("clgroups.txt");
    while (GetLine ()) {
	sscanf (buffer, " %i%n", &i, &n);
	if (i != target)
	    continue;
	while (buffer [n] && isspace ((unsigned char) buffer [n]))
	    n++;
	memmove (buffer, buffer + n, strlen (buffer + n) + 1);
	unquote ();
	if (n_targets == max_targets) {
	    max_targets += 64;
	    targets = (char **) s_realloc (targets, max_targets * sizeof (char *));
	}
	targets [n_targets++] = s_strdup (buffer);
    }
    fclose (fp);
    qsort (targets, n_targets, sizeof (char **), cmpstr);

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

    intarget = 0;
    openread (argv [1]);
    while (GetLine ()) {
	if (buffer [0] == ':') {
	    for (j = 1; buffer [j] && isspace ((unsigned char) buffer [j]); j++)
		;
	    if (bsearch (buffer + j, targets, n_targets, sizeof (char **), searchcmp))
		intarget = 1;
	    else
		intarget = 0;
	} else if (buffer [0] == '-') {
	    for (j = 1; buffer [j] && isspace ((unsigned char) buffer [j]); j++)
		;
	    memmove (buffer, buffer + j, strlen (buffer + j) + 1);
	    insert (intarget);
	}
    }
    fclose (fp);


    /* process data */

    fp = stdout;


    /* total response count inside and outside */

    allinn = 0;
    allout = 0;
    for (i = 0; i < n_patterns; i++) {
	allinn += patterns [i].i;
	allout += patterns [i].o;
    }

    /* bias: 0 or 1 */

    bias = 1;

    /* Relative Size */

    RS = (allinn + 2 * bias) / (allinn + allout + 4 * bias);

    /* score all patterens */

    for (j = 0; j < n_patterns; j++) {
	if (! patterns [j].used) {
	    patterns [j].I = -1;
	    continue;
	}
	i = patterns [j].i;
	o = patterns [j].o;
	R = ((double)(i + bias)) / (double)(allinn + 2 * bias);
	RO = ((double)(i + bias)) / (double)(i + o + 2 * bias);
	D = (RO - RS) / (1 - RS);
	if (D > 0)
	    I = (R + D) / 2.0;
	else
	    I = 0.0;
	patterns [j].I = I;
	patterns [j].R = R;
	patterns [j].D = D;

    }


    /* see what patterns will be used, print them, and sum up values for total score */

    qsort (patterns, n_patterns, sizeof (PATTERN_), cmppat); /* sort by score, descending */

    oldI = oldR = oldD = 0.0;
    old_i = old_o = 0;
    for (j = 0; j < n_patterns; j++) {
	if (! patterns[j].used)
	    continue;
	i = old_i + patterns[j].i;
	o = old_o + patterns[j].o;
	R = ((double)(i + bias)) / (double)(allinn + 2 * bias);
	RO = ((double)(i + bias)) / (double)(i + o + 2 * bias);
	D = (RO - RS) / (1 - RS);
	if (D > 0)
	    I = (R + D) / 2.0;
	else
	    I = 0.0;
	if (patterns[j].i == 0 || I < oldI * Limit)
	    patterns[j].rejected = 1;
	else {
	    oldI = I;
	    oldR = R;
	    oldD = D;
	    old_i = i;
	    old_o = o;
	    c = '[';
	    fprintf (fp, "%.2f %.2f %.2f %s %i:%i",
		     patterns[j].I, patterns[j].R, patterns[j].D,
		     escape((unsigned char *) patterns[j].s),
		     patterns[j].i, patterns[j].i + patterns[j].o);
	    qsort (patterns[j].forms, patterns[j].n_forms, sizeof (char **), cmpstr);
	    for (n = 0; n < patterns[j].n_forms; n++) {
		fprintf (fp, " %c %s", c, escape((unsigned char *) patterns[j].forms[n]));
		c = '|';
	    }
	    fprintf (fp, " ]\n");
	}

    }


    /* print the rejected patterns */

    qsort (patterns, n_patterns, sizeof (PATTERN_), cmppatstr); /* sort by pattern */

    for (i = 0; i < n_patterns; i++)
	if (patterns[i].rejected)
	    fprintf (fp, "[%s %i:%i]\n", escape((unsigned char *) patterns[i].s), patterns[i].i, patterns[i].i + patterns[i].o);


    /* print the total score */

    fprintf (fp, "\n%.2f %.2f %.2f %i:%i\n", oldI, oldR, oldD, old_i, old_i + old_o);


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
	"Usage: %s datafile limit\n"
	"\n"
	"Example: %s ../data/_/apple.data 1.02\n"
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
    f1 = ((PATTERN_ *)p1)->I;
    f2 = ((PATTERN_ *)p2)->I;
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

int searchcmp (void const *key, void const *p)
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
	if (bsearch (chr, valchars, n_valchars, sizeof (char *), searchcmp)) {
	    memcpy (buffer2 + j, buffer + i, n);
	    j += n;
	}
    }
    buffer2[ j] = '\0';
}

void insert(int intarget)
{
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
	patterns [n_patterns].s = s_strdup (buffer2);
	patterns [n_patterns].n_forms = 0;
	patterns [n_patterns].max_forms = 0;
	patterns [n_patterns].i = 0;
	patterns [n_patterns].o = 0;
	patterns [n_patterns].used = 0;
	patterns [n_patterns].rejected = 0;
	patterns [n_patterns].forms = NULL;
	p = &(patterns [n_patterns]);
	n_patterns++;
    }

    if (intarget)
	p->i++;
    else
	p->o++;

    if (p->i + p->o >= minvar)
	p->used = 1;

    p2 = NULL;
    if (p->n_forms > 0) {
	nmemb = p->n_forms;
	p2 = lfind (buffer, p->forms, &nmemb, sizeof (char *), searchcmp);
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
