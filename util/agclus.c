/*
 * File: agclus.c
 *
 * (c) Peter Kleiweg
 *     Tue Jan 16 13:43:56 2007
 *
 * This is free software; you can redistribute it and/or modify
 * it under the terms of the GNU General Public License as
 * published by the Free Software Foundation; either version 2,
 * or (at your option) any later version.
 *
 */

#define my_VERSION "0.02"

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

#define BUFSIZE 4095

typedef enum { FALSE = 0, TRUE = 1} BOOL_;
typedef enum { CLS, LBL } NODETYPE_;

typedef struct _cluster {
    int
        index;
    float
        value;
    NODETYPE_
        node [2];
    union {
        int
            cluster;
        int
            label;
    } n [2];
} CLUSTER_;

typedef struct _group {
    char
        *members;
    int
        n;
    double
        value;
    struct _group
        *left,
	*right;
} GROUP_;

CLUSTER_
    *cl = NULL;

GROUP_
    *root = NULL;

char
    **lbls = NULL,
    buffer [BUFSIZE + 1],
    *outfile = NULL,
    *listfile = NULL,
    *members,
    *programname,
    *no_mem_buffer,
    out_of_memory [] = "Out of memory";

char const
    *filename;

int
    n_lbls = 0,
    max_lbls = 0,
    inputline;

FILE
    *fp,
    *fpl,
    *fpout;

void
    walk (int i),
    walkgroups (GROUP_ *gr),
    fileopen (char const *s),
    get_programname (char const *argv0),
    errit (char const *format, ...),
    syntax (void),
    *s_malloc (size_t size),
    *s_realloc (void *block, size_t size);
char
    *s_strdup (char const *s);
int
    scmp (void const *p1, void const *p2),
    lscmp (void const *key, void const *p);
BOOL_
    GetLine (BOOL_ required);
GROUP_
    *newgroup (void),
    *findgroup (void);

int main (int argc, char *argv [])
{
    int
	argn,
	argmax,
	max,
	used,
	i,
	j,
	k,
	n;
    char
	*p;
    GROUP_
	*gr;

    no_mem_buffer = (char *) malloc (1024);

    get_programname (argv [0]);

    while (argc > 1 && argv [1][0] == '-') {
	if (! strcmp (argv [1], "-o")) {
	    argc--;
	    argv++;
	    outfile = argv [1];
	} else if (! strcmp (argv [1], "-l")) {
	    argc--;
	    argv++;
	    listfile = argv [1];
	}
	argc--;
	argv++;
    }

    if (argc < 2 && ! listfile)
	syntax ();

    if (listfile) {
	argc = 1;
	argmax = 256;
	p = argv [0];
	argv = (char **) s_malloc (argmax * sizeof (char *));
	argv [0] = p;
	fileopen (listfile);
	while (GetLine (FALSE)) {
	    if (argc == argmax) {
		argmax += 256;
		argv = (char **) s_realloc (argv, argmax * sizeof (char *));
	    }
	    argv [argc++] = s_strdup (buffer);
	}
    }
    
    fileopen (argv [1]);
    while (GetLine (FALSE)) {
	if (buffer [0] == 'l' || buffer [0] == 'L') {
	    if (n_lbls == max_lbls) {
		max_lbls += 256;
		lbls = (char **) s_realloc (lbls, max_lbls * sizeof (char *));
	    }
	    i = 1;
	    while (buffer [i] && isspace ((unsigned char) buffer [i]))
		i++;
	    lbls [n_lbls++] = s_strdup (buffer + i);
	}
    }
    fclose (fp);

    qsort (lbls, n_lbls, sizeof (char *), scmp);

    if (outfile) {
	fpout = fopen (outfile, "w");
	if (! fpout)
	    errit ("Creating file \"%s\": %s", outfile, strerror (errno));
    } else
	fpout = stdout;

    fprintf (fpout, "# Number of cluster files:\n%i\n# Number of labels:\n%i\n# Labels:\n", argc - 1, n_lbls);
    for (i = 0; i < n_lbls; i++)
	fprintf (fpout, "%s\n", lbls [i]);
    fprintf (fpout, "# Cluster count, cluster members, average cophenetic distance:\n");

    max = n_lbls - 1;
    cl = (CLUSTER_ *) s_malloc (max * sizeof (CLUSTER_));

    members = (char *) s_malloc ((n_lbls + 1) * sizeof (char));
    members [n_lbls] = '\0';

    for (argn = 1; argn < argc; argn++) {
	fileopen (argv [argn]);
	for (used = 0; used < max; used++) {
	    GetLine (TRUE);
	    if (sscanf (buffer, "%i %f%n", &(cl [used].index), &(cl [used].value), &i) < 2)
		errit ("Syntax error in \"%s\", line %i: \"%s\"", filename, inputline, buffer);
	    for (n = 0; n < 2; n++) {
		GetLine (TRUE);
		switch (buffer [0]) {
                    case 'l':
                    case 'L':
			cl [used].node [n] = LBL;
			i = 1;
			while (buffer [i] && isspace ((unsigned char) buffer [i]))
			    i++;
			p = bsearch (buffer + i, lbls, n_lbls, sizeof (char *), lscmp);
			if (! p)
			    errit ("Unknown label in \"%s\", line %i: \"%s\"", filename, inputline, buffer + i);
			cl [used].n [n].label = ((char **)p) - lbls;
			break;
                    case 'c':
                    case 'C':
			cl [used].node [n] = CLS;
			if (sscanf (buffer + 1, "%i", &(cl [used].n [n].cluster)) != 1)
			    errit ("Missing cluster number at line %i", inputline);
			break;
                    default:
			errit ("Syntax error at line %i: \"%s\"", inputline, buffer);
		}
	    }
	}

	/* replace indexes */
	for (i = 0; i < max; i++)
	    for (j = 0; j < 2; j++)
		if (cl [i].node [j] == CLS)
		    for (k = 0; k < max; k++)
			if (cl [i].n [j].cluster == cl [k].index) {
			    cl [i].n [j].cluster = k;
			    break;
			}

	for (i = 0; i < max; i++) {
	    for (j = 0; j < n_lbls; j++)
		members [j] = '-';
	    walk (i);

	    gr = findgroup ();
	    gr->n++;
	    gr->value += cl [i].value;

	}
	fclose (fp);
    }

    walkgroups (root);

    if (outfile)
	fclose (fpout);

    return 0;
}

void walkgroups (GROUP_ *gr)
{
    if (! gr)
	return;

    walkgroups (gr->left);
    fprintf (fpout, "%i\t%s\t%g\n", gr->n, gr->members, gr->value / gr->n);
    walkgroups (gr->right);
}

GROUP_ *newgroup ()
{
    GROUP_
	*tmp;

    tmp = (GROUP_ *) s_malloc (sizeof (GROUP_));
    tmp->members = s_strdup (members);
    tmp->n = 0;
    tmp->value = 0.0;
    tmp->left = tmp->right = NULL;
    return tmp;
}

GROUP_ *findgroup ()
{
    int
	i;
    GROUP_
	*tmp;

    if (! root) {
	root = newgroup ();
	return root;
    }

    tmp = root;
    for (;;) {
	i = strcmp (tmp->members, members);
	if (i == 0)
	    return tmp;
	else if (i < 0) {
	    if (tmp->left)
		tmp = tmp->left;
	    else {
		tmp = tmp->left = newgroup ();
		return tmp;
	    }
	} else {
	    if (tmp->right)
		tmp = tmp->right;
	    else {
		tmp = tmp->right = newgroup ();
		return tmp;
	    }
	}
    }
}

void walk (int i)
{
    int
	j;

    for (j = 0; j < 2; j++)
	if (cl [i].node [j] == CLS)
	    walk (cl [i].n [j].cluster);
	else
	    members [cl [i].n [j].label] = '*';
}

void fileopen (char const *s)
{
    filename = s;
    inputline = 0;
    fp = fopen (s, "r");
    if (! fp)
	errit ("Opening file \"%s\": %s", s, strerror (errno));
}

BOOL_ GetLine (BOOL_ required)
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

int scmp (void const *p1, void const *p2)
{
    return strcmp (*((char **) p1), *((char **) p2));
}

int lscmp (void const *key, void const *p)
{
    return strcmp ((char *) key, *((char **) p));
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
	"Usage: %s [-l filelist] [-o output file] [cluster file...]\n"
	"\n",
	programname
    );
    exit (1);
}
