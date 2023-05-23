
'''
Configuration variables
'''


import os

usermode = os.environ.get("USERMODE", "multi")

maxprojects = int(os.environ['MAXPROJECTS'])

secret = os.environ['SECRET']

datadir   = os.environ['DATADIR']
appdir    = os.environ['APPDIR']
appurl    = os.environ['APPURL']
appurls   = os.environ['APPURLS']
apprel    = os.environ['APPREL']
bindir    = os.environ['BINDIR']
binurl    = os.environ['BINURL']
binurls   = os.environ['BINURLS']
binrel    = os.environ['BINREL']

assert datadir[-1] == '/'
assert appdir[-1] == '/'
assert appurl[-1] == '/'
assert appurls[-1] == '/'
assert apprel[-1] == '/'
assert bindir[-1] == '/'
assert binurl[-1] == '/'
assert binurls[-1] == '/'
assert binrel[-1] == '/'

if usermode != 'single':
    mailfrom = os.environ['MAILFROM']
    smtpserv = os.environ['SMTPSERV']
else:
    mailfrom = os.environ.get('MAILFROM', '')
    smtpserv = os.environ.get('SMTPSERV', '')

smtpuser = os.environ.get('SMTPUSER', '')
smtppass = os.environ.get('SMTPPASS', '')

contact     = os.environ.get('CONTACT',     '')
contactname = os.environ.get('CONTACTNAME', '')
contactline = os.environ.get('CONTACTLINE', '')

if contact == '':
    contact = 'mailto:' + mailfrom
if contactname == '':
    contactname = mailfrom

salt = os.environ.get('SALT', '')

