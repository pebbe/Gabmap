#!/usr/bin/env python3

from hashlib import pbkdf2_hmac

def hash(txt, salt):
    our_app_iters = 500_000
    dk = pbkdf2_hmac('sha256', txt.encode('utf-8', errors='ignore'), salt.encode('utf-8', errors='ignore'), our_app_iters)
    return dk.hex()
