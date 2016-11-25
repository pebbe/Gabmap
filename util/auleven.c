/*
 * File: auleven.c
 *
 * (c) Peter Kleiweg
 *     Wed Jun 15 20:07:42 2005
 *     2008
 *     2010
 *
 * This is free software; you can redistribute it and/or modify
 * it under the terms of the GNU General Public License as
 * published by the Free Software Foundation; either version 2,
 * or (at your option) any later version.
 *
 */

#define my_VERSION "0.08"

#if defined(LEVEN_REAL)
typedef float DIFFTYPE;
typedef double WEIGHTTYPE;
#elif defined(LEVEN_SMALL)
typedef unsigned char DIFFTYPE;
typedef unsigned long int WEIGHTTYPE;
#else
typedef unsigned short int DIFFTYPE;
typedef unsigned long int WEIGHTTYPE;
#endif

#ifndef LEVEN_REAL
#define DIFFMAX ((1 << (8 * sizeof (DIFFTYPE))) - 1)
#endif

#define __NO_MATH_INLINES

#ifdef __WIN32__
#  define my_PATH_SEP '\\'
#else
#  define my_PATH_SEP '/'
#endif

#ifdef __MSDOS__
#  ifndef __COMPACT__
#    error Memory model COMPACT required
#  endif  /* __COMPACT__  */
#  include <dir.h>
#endif  /* __MSDOS__  */
#include <ctype.h>
#include <errno.h>
#include <limits.h>
#include <stdarg.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <time.h>

#define BUFSIZE 4095

typedef enum { FALSE = 0, TRUE } BOOL_;

typedef struct {
    char
        *label;
    int
        *i,
	len,
	lineno;
} STRING_;

typedef struct {
    WEIGHTTYPE
        i;
    BOOL_
        al,
        ab,
	le;
    int
        n;
} TBL_;

typedef struct {
    int
        i,
	j;
    WEIGHTTYPE
        v;
} ACTION_;

STRING_
    *strings = NULL;

TBL_
    **tbl;

BOOL_
    indelsubstequal = FALSE,
    skipindelpairs = TRUE,
    linenums = FALSE,
    randomcol = FALSE,
    utf8,
    weight_is_plain;

ACTION_
    actions [2 * BUFSIZE + 2];

long
    lineno,
    maxtoken = 0;

int
    counter,
    maxalign = 10,
    *s1,
    *s2,
    ibuffer [BUFSIZE + 1],
    ilen,
    tsize,
    n_strings = 0,
    max_strings = 0,
    hicode = 0,
    arg_c,
    max_code = INT_MAX,
    column = 0,
    randomseed = 0;

DIFFTYPE
    *id,
    *zero,
    **w;

char
    *label = NULL,
    *label_file = NULL,
    **tokens,
    buffer [BUFSIZE + 1],
    buffer2 [BUFSIZE + 1],
    *current_loc,
    **arg_v,
    *programname,
    *subst_file = NULL,
    *zero_file = NULL,
    *indel_file = NULL,
    *token_file = NULL,
    *no_mem_buffer,
    out_of_memory [] = "Out of memory";

char const
    *filename;

FILE
    *fp_in;

void
    do_pair (int i, int j),
    traverse (int i, int j, int len),
    alignment (int len),
    levenshtein (int const *s1, int len1, int const *s2, int len2),
    putstring (int),
    putlist (void),
    storestring (void),
    open_read (char const *s),
    read_substfile (void),
    read_indelfile (void),
    read_tokenfile (void),
    get_programname (char const *argv0),
    process_args (void),
    errit (char const *format, ...),
    syntax (void),
    *s_malloc (size_t size),
    *s_realloc (void *block, size_t size);
char
    *GetLine (BOOL_ required),
    *get_arg (void),
    *s_strdup (char const *s);
WEIGHTTYPE
    (*weight)(int, int),
    weight_plain (int, int),
    weight_indel (int, int),
    weight_subst (int, int),
    min3 (WEIGHTTYPE i1, WEIGHTTYPE i2, WEIGHTTYPE i3);
double
    get_diff (int i, int j);

int main (int argc, char *argv [])
{
    int
	i,
	j,
	k,
	*indexes;

    no_mem_buffer = (char *) malloc (1024);

    get_programname (argv [0]);

    arg_c = argc;
    arg_v = argv;
    process_args ();

    if (arg_c != 2)
	syntax ();

    if (subst_file && indel_file)
        errit ("Use either substitution values or indel values, not both");

    weight_is_plain = FALSE;
    if (subst_file)
        read_substfile ();
    else if (indel_file)
        read_indelfile ();
    else {
        weight = weight_plain;
	weight_is_plain = TRUE;
    }

    if (token_file)
	read_tokenfile ();

    if (label_file) {
	open_read (label_file);
	GetLine (TRUE);
	label = s_strdup (buffer);
	fclose (fp_in);
    }

    utf8 = FALSE;
    current_loc = s_strdup ("");
    open_read (arg_v [1]);
    while (GetLine (FALSE)) {
        if (buffer [0] == '*') {
	    ;
	} else if (buffer [0] == '%') {
	    if (memcmp (buffer, "%utf8", 5) && memcmp (buffer, "%UTF8", 5))
		errit ("Syntax error, in file %s, line %li", filename, lineno);
	    utf8 = TRUE;
        } else if (buffer [0] == ':') {
	    i = 1;
	    while (buffer [i] && isspace ((unsigned char) buffer [i]))
		i++;
	    current_loc = s_strdup (buffer + i);
        } else if (isdigit ((unsigned char) buffer [0])) {
	    current_loc = s_strdup (buffer);
        } else if (buffer [0] == '-') {
            putstring (1);
	    storestring ();
        } else if (buffer [0] == '+') {
            putlist ();
	    storestring ();
        } else
            errit ("Syntax error, in file %s, line %li", filename, lineno);
    }
    fclose (fp_in);

    tsize = 16;
    tbl = (TBL_ **) s_malloc (tsize * sizeof (TBL_ *));
    for (i = 0; i < tsize; i++)
        tbl [i] = (TBL_ *) s_malloc (tsize * sizeof (TBL_));

    if (column && column > n_strings)
	errit ("There are only %i columns", n_strings);

    if (label) {
	for (i = 0; i < n_strings; i++)
	    if (strcmp (label, strings [i].label))
		for (j = 0; j < n_strings; j++)
		    if (! strcmp (label, strings [j].label))
			do_pair (j, i);	
    } else if (column) {
	for (i = 0; i < n_strings; i++)
	    if (i != column - 1)
		do_pair (column - 1, i);
    } else if (randomcol) {
	if (randomseed)
	    srand (randomseed);
	else
	    srand ((unsigned int) time (NULL));
	indexes = (int *) s_malloc (n_strings * sizeof (int));
	for (i = 0; i < n_strings; i++)
	    indexes [i] = i;
	for (i = n_strings - 1; i; i--) {
	    k = rand () % (i + 1);
	    j = indexes [i];
	    indexes [i] = indexes [k];
	    indexes [k] = j;
	}
	for (i = 0; i < n_strings; i++)
	    if (indexes [i] != i)
		do_pair (i, indexes [i]);
    } else {
	for (i = 0; i < n_strings; i++)
	    for (j = i + 1; j < n_strings; j++)
		do_pair (i, j);
    }

    return 0;
}

void bytescheck (unsigned char *s, int n)
{
    int
	i;
    for (i = 0; i < n; i++)
	if (! s [i])
	    errit ("Invalid utf-8 code in %s, line %li", filename, lineno);
}

void limitcheck (long unsigned c)
{
    if (c > (long unsigned) max_code)
	errit ("Code out of range in %s, line %li", filename, lineno);
    
}

int bytes2 (unsigned char *s)
{

    long unsigned
	c;

    bytescheck (s, 2);

    c =   ( s [1] & 0x3F)
        | ((s [0] & 0x1F) << 6);

    limitcheck (c);

    return (int) c;

}

int bytes3 (unsigned char *s)
{

    long unsigned
	c;

    bytescheck (s, 3);

    c =   ( s [2] & 0x3F)
        | ((s [1] & 0x3F) <<  6)
        | ((s [0] & 0x0F) << 12);

    limitcheck (c);

    return (int) c;

}

int bytes4 (unsigned char *s)
{

    long unsigned
	c;

    bytescheck (s, 4);

    c =   ( s [3] & 0x3F)
        | ((s [2] & 0x3F) <<  6)
        | ((s [1] & 0x3F) << 12)
        | ((s [0] & 0x07) << 18);

    limitcheck (c);

    return (int) c;

}

int bytes5 (unsigned char *s)
{

    long unsigned
	c;

    bytescheck (s, 5);

    c =   ( s [4] & 0x3F)
        | ((s [3] & 0x3F) <<  6)
        | ((s [2] & 0x3F) << 12)
        | ((s [1] & 0x3F) << 18)
        | ((s [0] & 0x03) << 24);

    limitcheck (c);

    return (int) c;

}

int bytes6 (unsigned char *s)
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

    limitcheck (c);

    return (int) c;

}



void do_pair (int i, int j)
{
    /*
    if (strings [i].len == strings [j].len && memcmp (strings [i].i, strings [j].i, strings [i].len * sizeof (int)) == 0)
	return;
    */
    if (linenums)
	printf ("[%3i] %s\n[%3i] %s\n", strings [i].lineno, strings [i].label, strings [j].lineno, strings [j].label);
    else
	printf ("[1] %s\n[2] %s\n", strings [i].label, strings [j].label);

    levenshtein (strings [i].i, strings [i].len, strings [j].i, strings [j].len);

    s1 = strings [i].i;
    s2 = strings [j].i;

    counter = 0;

    traverse (strings [i].len, strings [j].len, 0);
}

char *gettoken (int i)
{
    if (maxtoken) {
	if (i > maxtoken || tokens [i] == NULL)
	    errit ("Undefined token nr %i", i);
	sprintf (buffer, "\t%s", tokens [i]);
	return buffer;
    }

    if (i == 0)
	sprintf (buffer, "\t");
    else if ((i > 32 && i < 127) || (i > 160 && i < 256))
	sprintf (buffer, "\t%c", (unsigned char) i);
    else
	sprintf (buffer, "\t%i", i);

    return buffer;
}

void alignment (int len)
{
    int
	i;

    /*
    if (skipindelpairs) {
	for (i = 0; i < len - 1; i++)
	    if ((actions [i].i == 0 && actions [i + 1].j == 0) ||
	        (actions [i].j == 0 && actions [i + 1].i == 0)
	    )
		return;
    }
    */

    counter++;

    for (i = len - 1; i >= 0; i--)
	fputs (gettoken (actions [i].i), stdout);
    printf ("\n");

    for (i = len - 1; i >= 0; i--)
	fputs (gettoken (actions [i].j), stdout);
    printf ("\n");

    for (i = len - 1; i >= 0; i--)
#ifdef LEVEN_REAL
	printf ("\t%g", weight_is_plain ? (float)((int)actions [i].v) : actions [i].v);
#else
	printf ("\t%li", actions [i].v);
#endif
    printf ("\n\n");

}

void traverse (int l1, int l2, int len)
{
    if (counter == maxalign)
	return;

    if (l1 == 0 && l2 == 0) {
	alignment (len);
	return;
    }
    actions [len].v = tbl [l2][l1].i;
    if (tbl [l2][l1].al) {
	actions [len].i = s1 [l1 - 1];
	actions [len].j = s2 [l2 - 1];
	traverse (l1 - 1, l2 - 1, len + 1);
    }
    if (tbl [l2][l1].le) {
	actions [len].i = 0;
	actions [len].j = s2 [l2 - 1];
	traverse (l1, l2 - 1, len + 1);
    }
    if (tbl [l2][l1].ab) {
	actions [len].i = s1 [l1 - 1];
	actions [len].j = 0;
	traverse (l1 - 1, l2, len + 1);
    }
}

void putstring (int offset)
{
    int
	j;

    unsigned char
	*buf;


    while (buffer [offset] && isspace ((unsigned char) buffer [offset]))
	offset++;


    if (utf8) {

	ilen = 0;
	for (buf = (unsigned char *) (buffer + offset); buf [0]; buf++) {
	    if        ((int) (buf [0]) >= 0374U) {
		ibuffer [ilen] = bytes6 (buf);
		buf += 5;
	    } else if ((int) (buf [0]) >= 0370U) {
		ibuffer [ilen] = bytes5 (buf);
		buf += 4;
	    } else if ((int) (buf [0]) >= 0360U) {
		ibuffer [ilen] = bytes4 (buf);
		buf += 3;
	    } else if ((int) (buf [0]) >= 0340U) {
		ibuffer [ilen] = bytes3 (buf);
		buf += 2;
	    } else if ((int) (buf [0]) >= 0300U) {
		ibuffer [ilen] = bytes2 (buf);
		buf += 1;
	    } else if ((int) (buf [0]) >= 0200U) {
		errit ("Invalid utf-8 code in %s, line %li", filename, lineno);
	    } else {
		limitcheck (buf [0]);
		ibuffer [ilen] = buf [0];
	    }
	    ilen++;
	}
	if (ilen == 0)
	    errit ("Missing string in %s, line %lu", filename, lineno);

    } else {

	ilen = strlen (buffer + offset);
	if (ilen == 0)
	    errit ("Missing string in %s, line %lu", filename, lineno);

	for (j = offset; buffer [j]; j++)
	    if ((unsigned char) buffer [j] > max_code)
		errit ("Code out of range in %s, line %li", filename, lineno);

	for (j = 0; j < ilen; j++)
	    ibuffer [j] = (unsigned char) buffer [offset + j];

    }

}

void putlist ()
{
    int
        i,
        n,
        val;

    ilen = 0;
    i = 1;
    while (sscanf (buffer + i, "%i%n", &val, &n) >= 1) {
        i += n;
        ibuffer [ilen++] = val;
    }
    if (ilen == 0)
        errit ("Missing string in %s, line %lu", filename, lineno);
}

void storestring ()
{
    int
	i;

    for (i = 0; i < ilen; i++)
	if (ibuffer [i] > hicode)
	    hicode = ibuffer [i];

    if (n_strings == max_strings) {
	max_strings += 512;
	strings = (STRING_ *) s_realloc (strings, max_strings * sizeof (STRING_));
    }
    strings [n_strings].i = s_malloc (ilen * sizeof (int));
    memcpy (strings [n_strings].i, ibuffer, ilen * sizeof (int));
    strings [n_strings].len = ilen;
    strings [n_strings].label = current_loc;
    strings [n_strings++].lineno = lineno;
}

void levenshtein (int const *s1, int l1, int const *s2, int l2)
{
    int
        i,
        x,
        y,
	n,
        newsize;
    WEIGHTTYPE
        aboveleft,
        above,
        left;

    if (l1 >= tsize || l2 >= tsize) {
        newsize = tsize + 16;
        while (l1 >= newsize || l2 >= newsize)
            newsize += 16;
        for (i = 0; i < tsize; i++)
            tbl [i] = (TBL_ *) s_realloc (tbl [i], newsize * sizeof (TBL_));
        tbl = (TBL_ **) s_realloc (tbl, newsize * sizeof (TBL_ *));
        while (tsize < newsize)
            tbl [tsize++] = (TBL_ *) s_malloc (newsize * sizeof (TBL_));
    }
    tbl [0][0].i = 0;
    tbl [0][0].n = 0;
    for (x = 1; x <= l2; x++) {
        tbl [x][0].i = tbl [x - 1][0].i + weight (0, s2 [x - 1]);
	tbl [x][0].al = tbl [x][0].ab = FALSE;
	tbl [x][0].le = TRUE;
	tbl [x][0].n = x;
    }
    for (y = 1; y <= l1; y++) {
        tbl [0][y].i = tbl [0][y - 1].i + weight (s1 [y - 1], 0);
	tbl [0][y].al = tbl [0][y].le = FALSE;
	tbl [0][y].ab = TRUE;
	tbl [0][y].n = y;
    }
    for (x = 1; x <= l2; x++)
        for (y = 1; y <= l1; y++) {
            aboveleft = tbl [x - 1][y - 1].i + weight (s1 [y - 1], s2 [x - 1]);
            above     = tbl [x    ][y - 1].i + weight (s1 [y - 1], 0         );
            left      = tbl [x - 1][y    ].i + weight (0,          s2 [x - 1]);
            tbl [x][y].i = min3 (aboveleft, above, left);
	    n = INT_MAX;
	    /* als meerdere paden met zelfde afstand, dan alleen de kortste onthouden */
	    if (tbl [x][y].i == aboveleft && tbl [x - 1][y - 1].n < n) n = tbl [x - 1][y - 1].n;
	    if (tbl [x][y].i == left      && tbl [x - 1][y    ].n < n) n = tbl [x - 1][y    ].n;
	    if (tbl [x][y].i == above     && tbl [x    ][y - 1].n < n) n = tbl [x    ][y - 1].n;
	    tbl [x][y].n = n + 1;
	    tbl [x][y].al = (tbl [x][y].i == aboveleft && tbl [x - 1][y - 1].n == n) ? TRUE : FALSE;
	    tbl [x][y].le = (tbl [x][y].i == left      && tbl [x - 1][y    ].n == n) ? TRUE : FALSE;
	    tbl [x][y].ab = (tbl [x][y].i == above     && tbl [x    ][y - 1].n == n) ? TRUE : FALSE;
        }
}

WEIGHTTYPE weight_plain (int i, int j)
{
    if (i == j)
        return 0;
    if ((i && j) || indelsubstequal)
        return 2;
    return 1.001;
}

WEIGHTTYPE weight_indel (int i, int j)
{
    if (i == j)
	return 0;
    return id [i] + id [j];
}

WEIGHTTYPE weight_subst (int i, int j)
{
    if (i == j)
	return zero_file ? zero [i] : 0;
    if (i > j)
        return w [i][j];
    return w [j][i];
}

WEIGHTTYPE min3 (WEIGHTTYPE i1, WEIGHTTYPE i2, WEIGHTTYPE i3)
{
    if (i1 < i2) {
        if (i1 < i3)
            return i1;
        else
            return i3;
    } else {
        if (i2 < i3)
            return i2;
        else
            return i3;
    }
}

void open_read (char const *s)
{
    filename = s;
    lineno = 0;
    fp_in = fopen (s, "r");
    if (! fp_in)
        errit ("Opening file \"%s\": %s", s, strerror (errno));
}

char *GetLine (BOOL_ required)
{
    int
        i;

    for (;;) {
        lineno++;
        if (fgets (buffer, BUFSIZE, fp_in) == NULL) {
            if (required)
                errit ("Reading file \"%s\", line %li: %s",
                       filename, lineno, errno ? strerror (errno) : "End of file");
            else
                return NULL;
        }
        i = strlen (buffer);
        while (i > 0 && isspace ((unsigned char) buffer [i - 1]))
            buffer [--i] = '\0';
        i = 0;
        while (buffer [i] && isspace ((unsigned char) buffer [i]))
            i++;
        if (i)
            memmove (buffer, buffer + i, strlen (buffer + i) + 1);
        if (buffer [0] == '\0' || buffer [0] == '#')
            continue;
        return buffer;
    }
}

void read_substfile ()
{
#ifdef LEVEN_REAL
    float
	c;
#else
    long int
	c;
#endif
    int
        i,
        j;

    weight = weight_subst;

    open_read (subst_file);
    GetLine (TRUE);
#ifdef LEVEN_REAL
    if (buffer [0] != 'F' || buffer [1] != ':') {
	errit ("File \"%s\" is not a table with real values. You should use 'auleven' or 'auleven-s'", filename);
    }
    GetLine (TRUE);
#else
    if (buffer [0] == 'F' && buffer [1] == ':') {
	errit ("File \"%s\" is not a table with integer values. You should use 'auleven-r'", filename);
    }
#endif
    max_code = atoi (buffer);
    if (max_code < 1)
        errit ("Illegal table size in \"%s\", line %li: %i", filename, lineno, max_code);
    w = (DIFFTYPE **) s_malloc ((max_code + 1) * sizeof (DIFFTYPE *));
    for (i = 1; i <= max_code; i++) {
        w [i] = (DIFFTYPE *) s_malloc (i * sizeof (DIFFTYPE));
        for (j = 0; j < i; j++) {
            GetLine (TRUE);
#ifdef LEVEN_REAL
	    if (sscanf (buffer, "%f", &c) != 1)
#else
	    if (sscanf (buffer, "%li", &c) != 1)
#endif
		errit ("Reading value in \"%s\", line %li", filename, lineno);
#ifdef LEVEN_REAL
	    if (c < 0.0)
#else
	    if (c < 0 || c > DIFFMAX)
#endif
		errit ("Value out of range in \"%s\", line %li", filename, lineno);
            w [i][j] = (DIFFTYPE) c;
        }
    }
    fclose (fp_in);

    if (! zero_file)
	return;

    open_read (zero_file);
    GetLine (TRUE);
#ifdef LEVEN_REAL
    if (buffer [0] != 'F' || buffer [1] != ':') {
	errit ("File \"%s\" is not a table with real values. You should use 'auleven' or 'auleven-s'", filename);
    }
    GetLine (TRUE);
#else
    if (buffer [0] == 'F' && buffer [1] == ':') {
	errit ("File \"%s\" is not a table with integer values. You should use 'auleven-r'", filename);
    }
#endif
    i = atoi (buffer);
    if (i != max_code)
        errit ("Illegal table size in \"%s\", line %li: %i (should be %i)", filename, lineno, i, max_code);
    
    zero = (DIFFTYPE *) s_malloc ((max_code + 1) * sizeof (DIFFTYPE));
    zero [0] = 0;
    for (i = 1; i <= max_code; i++) {
        GetLine (TRUE);
#ifdef LEVEN_REAL
	if (sscanf (buffer, "%f", &c) != 1)
#else
	if (sscanf (buffer, "%li", &c) != 1)
#endif
	    errit ("Reading value in \"%s\", line %li", filename, lineno);
#ifdef LEVEN_REAL
	if (c < 0.0)
#else
	if (c < 0 || c > DIFFMAX)
#endif
            errit ("Value out of range in \"%s\", line %li", filename, lineno);
        zero [i] = c;
    }
    fclose (fp_in); 
   


}

void read_tokenfile ()
{
    long int
	l;
    open_read (token_file);
    while (GetLine (FALSE)) {
	l = atol (buffer);
	if (l < 1)
	    errit ("Illegal value in \"%s\", line %li", filename, lineno);
	if (l > maxtoken)
	    maxtoken = l;
    }
    fclose (fp_in);

    tokens = (char **) s_malloc ((maxtoken + 1) * sizeof (char *));
    tokens [0] = s_strdup ("");
    for (l = 1; l <= maxtoken; l++)
	tokens [l] = NULL;

    open_read (token_file);
    while (GetLine (FALSE)) {
	if (sscanf (buffer, "%li %s", &l, buffer2) == 2)
	    tokens [l] = s_strdup (buffer2);
    }
    fclose (fp_in);

}

void read_indelfile ()
{
#ifdef LEVEN_REAL
    float
	c;
#else
    long int
	c;
#endif
    int
        i;

    weight = weight_indel;

    open_read (indel_file);
    GetLine (TRUE);
#ifdef LEVEN_REAL
    if (buffer [0] != 'F' || buffer [1] != ':') {
	errit ("File \"%s\" is not a table with real values. You should use 'auleven' or 'auleven-s'", filename);
    }
    GetLine (TRUE);
#else
    if (buffer [0] == 'F' && buffer [1] == ':') {
	errit ("File \"%s\" is not a table with integer values. You should use 'auleven-r'", filename);
    }
#endif
    max_code = atoi (buffer);
    if (max_code < 1)
        errit ("Illegal table size in \"%s\", line %li: %i", filename, lineno, max_code);
    id = (DIFFTYPE *) s_malloc ((max_code + 1) * sizeof (DIFFTYPE));
    id [0] = 0;
    for (i = 1; i <= max_code; i++) {
        GetLine (TRUE);
#ifdef LEVEN_REAL
	if (sscanf (buffer, "%f", &c) != 1)
#else
	if (sscanf (buffer, "%li", &c) != 1)
#endif
	    errit ("Reading value in \"%s\", line %li", filename, lineno);
#ifdef LEVEN_REAL
	if (c < 0.0)
#else
	if (c < 0 || c > DIFFMAX)
#endif
            errit ("Value out of range in \"%s\", line %li", filename, lineno);
        id [i] = c;
    }
    fclose (fp_in);
}

void process_args ()
{
    while (arg_c > 1 && arg_v [1][0] == '-') {
        switch (arg_v [1][1]) {
            case 'c':
		column = atoi (get_arg ());
		if (column < 1)
		    errit ("Invalid value for option -c");
	        randomcol = FALSE;
		break;
            case 'e':
		indelsubstequal = TRUE;
		skipindelpairs = FALSE;
		break;
            case 'i':
                indel_file = get_arg ();
		skipindelpairs = FALSE;
                break;
	    case 'l':
		label = get_arg ();
		break;
	    case 'L':
		label_file = get_arg ();
		break;
	    case 'm':
		maxalign = atoi (get_arg ());
		break;
	    case 'n':
		linenums = TRUE;
		break;
	    case 'r':
		column = 0;
		randomcol = TRUE;
		break;
	    case 'S':
		randomseed = atoi (get_arg ());
		if (randomseed < 1)
		    errit ("Invalid value for option -S");
		break;
	    case 's':
                subst_file = get_arg ();
		skipindelpairs = FALSE;
                break;
            case 't':
                token_file = get_arg ();
                break;
	    case 'z':
                zero_file = get_arg ();
                break;
            default:
                errit ("Illegal option '%s'", arg_v [1]);
        }
	arg_c--;
	arg_v++;
    }
}

char *get_arg ()
{
    if (arg_v [1][2])
        return arg_v [1] + 2;

    if (arg_c == 2)
        errit ("Missing argument for '%s'", arg_v [1]);

    arg_v++;
    arg_c--;
    return arg_v [1];
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
    );
#ifdef LEVEN_REAL
    fprintf (
	stderr,
	"Compiled with option LEVEN_REAL\n"
	"\n"
    );
#endif
#ifdef LEVEN_SMALL
    fprintf (
	stderr,
	"Compiled with option LEVEN_SMALL\n"
	"\n"
    );
#endif
    fprintf (
	stderr,
	"Usage: %s  [-c int | -l string | -L filename | -r [-S int] ] [-m int] [-n]\n"
	"\t\t[-e | -i filename | -s filename [-z filename]] [-t filename] datafile\n"
	"\n"
	"\t-c : column number\n"
        "\t-e : equal weight for indel and subst\n"
        "\t-i : file with indel values\n"
	"\t-l : select by label\n"
	"\t-L : select by label from file\n"
	"\t-m : maximum number of aligments per word pair\n"
	"\t-n : print line numbers\n"
	"\t-r : random column\n"
	"\t-S : seed for random number generator, instead of time\n"
        "\t-s : file with substitution and indel values\n"
	"\t-t : file with token strings\n"
        "\t-z : file with substitution values for identical tokens\n"
	"\n",
	programname
    );
    exit (1);
}
