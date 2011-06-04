#!/usr/bin/env python3
"""
--documentation--
"""

__author__ = "Peter Kleiweg"
__version__ = "0.1"
__date__ = "2010/03/07"

#| imports

import smtplib, sys
from email.mime.text import MIMEText
import u.html as _h
import u.config as _c

#| functions

def sendmail(address, subject, text):
    try:
        text.encode('us-ascii')
    except:
        try:
            text.encode('iso-8859-1')
        except:
            msg = MIMEText(text.encode('utf-8'), _charset='utf-8')
        else:
            msg = MIMEText(text, _charset='iso-8859-1')
    else:
        msg = MIMEText(text)

    msg['From'] = 'Gabmap <{}>'.format(_c.mailfrom)
    msg['To'] = address
    msg['Subject'] = subject

    try:
        server = smtplib.SMTP(_c.smtpserv)
        if _c.smtpuser and _c.smtppass:
            server.login(_c.smtpuser, _c.smtppass)
        server.sendmail(_c.mailfrom, address, msg.as_string())
        server.quit()
    except:
        i = [_h.escape(str(x)) for x in sys.exc_info()]
        _h.exitMessage('Error', 'Sending e-mail to {0}:<p>\n{1[0]} - {1[1]}\n'.format(_h.escape(address), i))
