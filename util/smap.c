/*
 * File: smap.c
 *
 * (c) Peter Kleiweg
 *     Thu Sep 30 13:05:48 2010
 *
 * This is free software; you can redistribute it and/or modify
 * it under the terms of the GNU General Public License as
 * published by the Free Software Foundation; either version 2,
 * or (at your option) any later version.
 *
 */

#define my_VERSION "0.01"

#define __NO_MATH_INLINES

#ifdef __WIN32__
#  define my_PATH_SEP '\\'
#else
#  define my_PATH_SEP '/'
#endif

#include <ctype.h>
#include <errno.h>
#include <math.h>
#include <stdarg.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#define BUFSIZE 4095

typedef struct {
    double
        x,
        y;
    char
        *s;
} POINT_;

int
    npoints = 0,
    maxpoints = 0,
    lineno;

char
    buffer [BUFSIZE + 1],
    *programname,
    *no_mem_buffer,
    out_of_memory [] = "Out of memory";

FILE
    *fp;

POINT_
    *points = NULL,
    *points1 = NULL;

void
    get_programname (char const *argv0),
    errit (char const *format, ...),
    *s_malloc (size_t size),
    *s_realloc (void *block, size_t size);
char
    *GetLine (void),
    *s_strdup (char const *s);

int main (int argc, char *argv [])
{
    int
	found,
	i,
	j,
	n;
    double
	alpha,
	limit,
	x,
	dx,
	y,
	dy,
	d,
	dmax,
	dlim,
	minimal;


    no_mem_buffer = (char *) malloc (1024);

    get_programname (argv [0]);

    fp = fopen (argv [1], "r");
    if (! fp)
	errit ("Opening file \"%s\": %s", argv [0], strerror (errno));
    lineno = 0;

    while (GetLine ()) {
	if (npoints == maxpoints) {
	    maxpoints += 256;
	    points = (POINT_ *) s_realloc (points, maxpoints * sizeof (POINT_));
	}
	if (sscanf (buffer, " %lg %lg %n", &x, &y, &n) < 2)
	    errit ("Reading file \"%s\", line %i", argv [0], lineno);
	points [npoints].x = x;
	points [npoints].y = y;
	points [npoints++].s = s_strdup (buffer + n);
    }
    fclose (fp);

    dmax = 0.0;
    for (i = 0; i < npoints; i++)
	for (j = 0; j < i; j++) {
	    dx = points [i].x - points [j].x;
	    dy = points [i].y - points [j].y;
	    d = sqrt (dx * dx + dy * dy);
	    if (d > dmax)
		dmax = d;
	}
	
    dlim = dmax * 0.02;
    minimal = dlim * .0001;

    points1 = (POINT_ *) s_malloc (npoints * sizeof (POINT_));

    alpha = 0.0;
    limit = 2.0;

    found = 1;
    while (found) {
	found = 0;
	if (alpha < 1.0) {
	    alpha += .01;
	    found = 1;
	}
	if (limit > 1.0) {
	    limit -= .02;
	    found = 1;
	}
	for (i = 0; i < npoints; i++)
	    points1 [i] = points [i];
	for (i = 0; i < npoints; i++) {
	    n = 0;
	    x = y = 0.0;	
	    for (j = 0; j < npoints; j++) {
		if (i == j)
		    continue;
		dx = points1 [j].x - points1 [i].x;
		dy = points1 [j].y - points1 [i].y;
		d = sqrt (dx * dx + dy * dy);
		if (d < dlim * limit) {
		    found = 1;
		    n += 1;
		    x += dx;
		    y += dy;
		}
	    }
	    if (n) {	      
		if (fabs (x) < minimal && fabs (y) < minimal) {
		    x = (((float) random ()) / (float) RAND_MAX) * minimal * 20.0 - minimal * 10.0;
		    y = (((float) random ()) / (float) RAND_MAX) * minimal * 20.0 - minimal * 10.0;
		}
		points [i].x -= x * alpha * .51;
		points [i].y -= y * alpha * .51;
	    }
	}
	
    }
    
    for (i = 0; i < npoints; i++)
	printf ("%g %g\t%s\n", points [i].x, points [i].y, points [i].s);

    return 0;
}

/*
 * get line from `fp' into `buffer'
 * remove leading and trailing white space
 * skip empty lines and lines starting with #
 */
char *GetLine ()
{
    int
        i;

    for (;;) {
        lineno++;
        if (fgets (buffer, BUFSIZE, fp) == NULL) {
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
