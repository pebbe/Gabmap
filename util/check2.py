#!/usr/bin/env python2
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

def colormath():
    """
    >>> from colormath.color_objects import RGBColor, HSVColor
    >>> hsv = RGBColor(64, 128, 196).convert_to('hsv')
    >>> rgb = HSVColor(hsv.hsv_h, hsv.hsv_s, hsv.hsv_v).convert_to('rgb')
    >>> rgb.rgb_r, rgb.rgb_g, rgb.rgb_b        
    (64, 128, 196)
    """
    pass

def numpy():
    """
    >>> import numpy as np

    >>> x = np.arange(4).reshape((2,2))
    >>> x
    array([[0, 1],
           [2, 3]])
    
    >>> np.transpose(x)
    array([[0, 2],
           [1, 3]])
    
    >>> x = np.ones((1, 2, 3))
    >>> np.transpose(x, (1, 0, 2)).shape
    (2, 1, 3)
    
    >>> a = np.random.randn(9, 6) + 1j*np.random.randn(9, 6)
    >>> U, s, Vh = np.linalg.svd(a)
    >>> U.shape, Vh.shape, s.shape
    ((9, 9), (6, 6), (6,))
    
    >>> U, s, Vh = np.linalg.svd(a, full_matrices=False)
    >>> U.shape, Vh.shape, s.shape
    ((9, 6), (6, 6), (6,))
    >>> S = np.diag(s)
    >>> np.allclose(a, np.dot(U, np.dot(S, Vh)))
    True
    
    >>> s2 = np.linalg.svd(a, compute_uv=False)
    >>> np.allclose(s, s2)
    True
    """
    pass


def test():
    """run the examples in the docstrings using the doctest module"""
    import doctest

    #print 'Testing colormath ...'
    #doctest.run_docstring_examples(colormath, None, name='colormath', verbose=False)
    #print 'Testing colormath ... done'

    print 'Testing numpy ...'
    doctest.run_docstring_examples(numpy, None, name='numpy', verbose=False)
    print 'Testing numpy ... done'

#| main


#| if main

if __name__ == "__main__":
    test()

