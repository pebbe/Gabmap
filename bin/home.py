#!/usr/bin/env python
"""
--documentation--
"""

__author__ = "Peter Kleiweg"
__version__ = "0.1"
__date__ = "2010/02/18"

#| imports

import cgitb; cgitb.enable(format="html")

import sys

from u.config import appurls
from u.html import head, foot, getBody
from u.login import username
import p.user

#| main

if username:
    p.user.makepage(username)
else:
    body = getBody('login.html').format(vars())
    sys.stdout.write(head())
    sys.stdout.write(body)
    sys.stdout.write(foot())
