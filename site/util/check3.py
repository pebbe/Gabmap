#!/usr/bin/env python3
"""

"""

__author__ = "Peter Kleiweg"
__version__ = "0.1"
__date__ = "2010/07/08"

#| imports

import cgitb; cgitb.enable(format="text")

import os, sys

#| globals

#| functions

def pyproj():
    """
    >>> from pyproj import Proj
    >>> p = Proj(proj='utm',zone=10,ellps='WGS84') # use kwargs
    >>> x,y = p(-120.108, 34.36116666)
    >>> print('x=%9.3f y=%11.3f' % (x,y))
    x=765975.641 y=3805993.134
    >>> print('lon=%8.3f lat=%5.3f' % p(x,y,inverse=True))
    lon=-120.108 lat=34.361
    >>> # do 3 cities at a time in a tuple (Fresno, LA, SF)
    >>> lons = (-119.72,-118.40,-122.38)
    >>> lats = (36.77, 33.93, 37.62 )
    >>> x,y = p(lons, lats)
    >>> print('x: %9.3f %9.3f %9.3f' % x)
    x: 792763.863 925321.537 554714.301
    >>> print('y: %9.3f %9.3f %9.3f' % y)
    y: 4074377.617 3763936.941 4163835.303
    >>> lons, lats = p(x, y, inverse=True) # inverse transform
    >>> print('lons: %8.3f %8.3f %8.3f' % lons)
    lons: -119.720 -118.400 -122.380
    >>> print('lats: %8.3f %8.3f %8.3f' % lats)
    lats:   36.770   33.930   37.620
    >>> p2 = Proj('+proj=utm +zone=10 +ellps=WGS84') # use proj4 string
    >>> x,y = p2(-120.108, 34.36116666)
    >>> print('x=%9.3f y=%11.3f' % (x,y))
    x=765975.641 y=3805993.134

    """
    pass


def test():
    """run the examples in the docstrings using the doctest module"""
    import doctest

    print('Testing pyproj.Proj ...')
    doctest.run_docstring_examples(pyproj, None, name='pyproj.Proj', verbose=False)
    print('Testing pyproj.Proj ... done')

#| main


#| if main

if __name__ == "__main__":
    test()

