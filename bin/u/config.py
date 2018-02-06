
'''
Configuration variables
'''


import os

def _istrue(s):
    try:
        i = int(s)
        return i != 0
    except:
        pass
    return s.lower() in ['y', 'yes', 't', 'true']

usermode = os.environ.get("USERMODE", "multi")

maxprojects = int(os.environ['MAXPROJECTS'])
maxdays = int(os.environ['MAXDAYS'])

python = os.environ['PYTHON']
python2 = os.environ['PYTHON2']
python3 = os.environ['PYTHON3']
python2path = os.environ.get('PYTHON2PATH', '')
python3path = os.environ.get('PYTHON3PATH', '')

secret = os.environ['SECRET']
tryxforwardedfor = _istrue(os.environ.get('TRY_X_FORWARDED_FOR', ''))

datadir   = os.environ['DATADIR']
appdir    = os.environ['APPDIR']
appurl    = os.environ['APPURL']
appurls   = os.environ['APPURLS']
apprel    = os.environ['APPREL']

assert datadir[-1] == '/'
assert appdir[-1] == '/'
assert appurl[-1] == '/'
assert appurls[-1] == '/'
assert apprel[-1] == '/'

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
