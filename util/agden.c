/*
 * File: agden.c
 *
 * (c) Peter Kleiweg
 *     Tue Jan 16 16:04:56 2007
 *
 * This is free software; you can redistribute it and/or modify
 * it under the terms of the GNU General Public License as
 * published by the Free Software Foundation; either version 2,
 * or (at your option) any later version.
 *
 */

#define my_VERSION "0.03"

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
#include <stdarg.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#define BUFSIZE 10240

typedef enum { FALSE = 0, TRUE = 1} BOOL_;

typedef struct {
    char
        *members;
    double
        value;
    int
        n;
    BOOL_
        *parent,
	*child;
} CLUSTER_;

CLUSTER_
    *clust = NULL;

int
    n_clust = 0,
    max_clust = 0,
    nfiles,
    nlbls,
    inputline,
    arg_c;

float
    percentage = 50.001;

char
    buffer [BUFSIZE + 1],
    *outfile = NULL,
    *members,
    **lbls,
    **arg_v,
    *programname,
    *no_mem_buffer,
    out_of_memory [] = "Out of memory";

char const
    *filename;


FILE
    *fp;

BOOL_
    *useit;

void
    traverse (int i),
    fileopen (char const *s),
    get_programname (char const *argv0),
    errit (char const *format, ...),
    syntax (void),
    *s_malloc (size_t size),
    *s_realloc (void *block, size_t size);
char
    *s_strdup (char const *s);
char const
    *psstring (unsigned char const *s);
BOOL_
    getline (BOOL_ required),
    is_parent (int i, int j);

int main (int argc, char *argv [])
{
    int
	i,
	j,
	k,
	top;
    double
	limit,
	f;

    no_mem_buffer = (char *) malloc (1024);

    get_programname (argv [0]);

    while (argc > 1 && argv [1][0] == '-') {
	if (! strcmp (argv [1], "-o")) {
	    argc--;
	    argv++;
	    outfile = argv [1];
	} else if (! strcmp (argv [1], "-p")) {
	    argc--;
	    argv++;
	    percentage = atof (argv [1]);
	    if (percentage <= 50.0 || percentage > 100.0)
		errit ("Percentage must be more than 50 and equal to or less than 100 ");
	}
	argc--;
	argv++;
    }

    if (argc != 2)
	syntax ();

    fileopen (argv [1]);
    getline (TRUE);
    nfiles = atoi (buffer);
    getline (TRUE);
    nlbls = atoi (buffer);
    lbls = (char **) s_malloc (nlbls * sizeof (char *));
    for (i = 0; i < nlbls; i++) {
	getline (TRUE);
	lbls [i] = (char *) s_strdup (buffer);
    }
    members = (char *) s_malloc ((nlbls + 1) * sizeof (char));
    limit = percentage / 100.0 * nfiles;
    while (getline (FALSE)) {
	sscanf (buffer, "%i %s %lf", &i, members, &f);
	if (i < limit)
	    continue;
	if (n_clust == max_clust) {
	    max_clust += 256;
	    clust = (CLUSTER_ *) s_realloc (clust, max_clust * sizeof (CLUSTER_));
	}
	clust [n_clust].members = s_strdup (members);
	clust [n_clust].value = f;
	clust [n_clust].n = i;
	n_clust++;
    }
    fclose (fp);

    for (i = 0; i < n_clust; i++) {
	clust [i].parent = (BOOL_ *) s_malloc (n_clust * sizeof (BOOL_));
	clust [i].child  = (BOOL_ *) s_malloc (n_clust * sizeof (BOOL_));
    }

    for (i = 0; i < n_clust; i++)
	for (j = 0; j < n_clust; j++)
	    clust [j].parent [i] = clust [i].child [j] = is_parent (i, j);


    for (i = 0; i < n_clust; i++)
	for (j = 0; j < n_clust; j++)
	    for (k = 0; k < n_clust; k++)
		if (clust [k].parent [j] && clust [j].parent [i])
		    clust [i].child [k] = FALSE;

    for (i = 0; i < n_clust; i++)
	for (j = 0; j < n_clust; j++)
	    if (! clust [i].child [j])
		clust [j].parent [i] = FALSE;


    /* find top node */
    top = -1;
    for (i = 0; i < n_clust; i++) {
	for (j = 0; j < n_clust; j++)
	    if (clust [i].parent [j])
		break;
	if (j == n_clust) {
	    top = i;
	    break;
	}
    }


    if (outfile) {
	fp = fopen (outfile, "w");
	if (! fp)
	    errit ("Creating file \"%s\": %s", outfile, strerror (errno));
    } else
	fp = stdout;

    useit = (BOOL_ *) s_malloc (nlbls * sizeof (BOOL_));
    for (i = 0; i < nlbls; i++)
	useit [i] = TRUE;
    traverse (top);

    if (outfile)
	fclose (fp);

    return 0;
}

void traverse (int i)
{
    int
	j;

    fprintf (fp, "nstart\n");
    for (j = n_clust - 1; j >= 0; j--)
	if (clust [i].child [j])
	    traverse (j);
    for (j = 0; j < nlbls; j++)
	if (clust [i].members [j] == '*' && useit [j]) {
	    fprintf (fp, "(%s) lbl\n", psstring ((unsigned char const *) (lbls [j])));
	    useit [j] = FALSE;
	}
    fprintf (fp, "%.0f %g nend\n", ((float) clust [i].n) / ((float) nfiles) * 100.0, clust [i].value);

}

/*
 * i is parent of j
 */
BOOL_ is_parent (int i, int j)
{
    int
	ii;

    if (i == j)
	return FALSE;

    for (ii = 0; ii < nlbls; ii++)
	if (clust [j].members [ii] == '*' && clust [i].members [ii] != '*')
	    return FALSE;

    return TRUE;
}


BOOL_ getline (BOOL_ required)
/* Lees een regel in
 * Plaats in buffer
 * Negeer lege regels en regels die beginnen met #
 */
{
    int
        i;

    for (;;) {
        if (fgets (buffer, BUFSIZE, fp) == NULL) {
            if (required)
                errit ("Unexpected end of file");
            else
                return FALSE;
        }
        inputline++;
        i = strlen (buffer);
        while (i && isspace ((unsigned char) buffer [i - 1]))
            buffer [--i] = '\0';
        i = 0;
        while (buffer [i] && isspace ((unsigned char) buffer [i]))
            i++;
        if (buffer [i] == '#')
            continue;
        if (buffer [i]) {
            memmove (buffer, buffer + i, strlen (buffer) + 1);
            return TRUE;
        }
    }
}

char const *psstring (unsigned char const *s)
{
    int
        i,
        j;

    j = 0;
    for (i = 0; s [i]; i++) {
        if (j + 4 > BUFSIZE)
            errit ("String too long: \"%s\"", s);
        if (s [i] == '(' ||
            s [i] == ')' ||
            s [i] == '\\'
        ) {
            buffer [j++] = '\\';
            buffer [j++] = s [i];
        } else if (s [i] < 32 || s [i] > 126) {
            buffer [j++] = '\\';
            sprintf (buffer + j, "%3o", (unsigned) s [i]);
            j += 3;
        } else
            buffer [j++] = s [i];
    }
    buffer [j] = '\0';
    return buffer;
}

void fileopen (char const *s)
{
    filename = s;
    inputline = 0;
    fp = fopen (s, "r");
    if (! fp)
        errit ("Opening file \"%s\": %s", s, strerror (errno));
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
	"Usage: %s [-o outfile] [-p percentage] agclusterfile\n"
	"\n",
	programname
    );
    exit (1);
}
