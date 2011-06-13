
import os

maxprojects = int(os.environ['MAXPROJECTS'])
maxdays = int(os.environ['MAXDAYS'])

python = os.environ['PYTHON']
python2 = os.environ['PYTHON2']
python3 = os.environ['PYTHON3']
python2path = os.environ.get('PYTHON2PATH', '')
python3path = os.environ.get('PYTHON3PATH', '')

secret = os.environ['SECRET']
tryxforwardedfor = os.environ.get('TRY_X_FORWARDED_FOR', '')

datadir   = os.environ['DATADIR']
appdir    = os.environ['APPDIR']
appurl    = os.environ['APPURL']
appurls   = os.environ['APPURLS']
apprel    = os.environ['APPREL']
abouturl  = os.environ['ABOUTURL']
helpurl   = os.environ['HELPURL']

assert datadir[-1] == '/'
assert appdir[-1] == '/'
assert appurl[-1] == '/'
assert appurls[-1] == '/'
assert apprel[-1] == '/'

mailfrom = os.environ['MAILFROM']

smtpserv = os.environ['SMTPSERV']
smtpuser = os.environ.get('SMTPUSER', '')
smtppass = os.environ.get('SMTPPASS', '')

contact     = os.environ.get('CONTACT',     '')
contactname = os.environ.get('CONTACTNAME', '')
contactline = os.environ.get('CONTACTLINE', '')
