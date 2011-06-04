#!/usr/bin/env python
"""
--documentation--
"""

__author__ = "Peter Kleiweg"
__version__ = "0.1"
__date__ = "2010/02/05"

#| imports

import cgitb; cgitb.enable(format="html")

import cgi, os, re, socket, stat, sys, time
from http import cookies

import u.html, u.login, u.mail
from u.config import *

#| globals

if contact[:4] == 'http':
    _t = ' target="_blank"'
else:
    _t = ''
if contactname:
    contacthtml = '<a href="{}"{}>{}</a>'.format(contact, _t, contactname)
else:
    contacthtml = '<a href="{}"{}>contact</a>'.format(contact, _)


#| functions

def userbymail(email):
    for fname in os.listdir('.'):
        if fname[0] == '.':
            continue
        if fname.startswith('guest') or fname.startswith('demo'):
            continue
        fp = open(fname + '/email', 'rt', encoding='utf-8')
        em = fp.readline().strip()
        fp.close()
        if email == em:
            fp = open(fname + '/passwd', 'rt', encoding='utf-8')
            pw = fp.readline().strip()
            fp.close()
            return email, fname, pw
    return '', '', ''

def userbyuser(user):
    try:
        if user.startswith('guest') or user.startswith('demo'):
            em = ''
        else:
            fp = open(user + '/email', 'rt', encoding='utf-8')
            em = fp.readline().strip()
            fp.close()
        fp = open(user + '/passwd', 'rt', encoding='utf-8')
        pw = fp.readline().strip()
        fp.close()
        return em, user, pw
    except:
        return '', '', ''

def escape(s):
    return s.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;').replace('"', '&quot;')

def getval(field):
    return re.sub(r'\s+', ' ', form.getvalue(field, '')).strip()

def errorExitCreate(errors):
    err = ''
    for e in errors:
        err += '<div class="error">\nError: ' + e + '\n</div>\n'
    sys.stdout.write(u.html.head('error'))
    sys.stdout.write(u.html.getBody('accountCreate.html').format({'appurl':appurl,
                                                                  'appurls':appurls,
                                                                  'errors':err,
                                                                  'email':email,
                                                                  'username':username}))
    sys.stdout.write(u.html.foot())
    sys.exit()

def actionLogin():

    username = getval('username')
    passwd = getval('password')
    if username.startswith('guest'):
        passwd = 'guest'
    if username.startswith('demo'):
        passwd = 'demo'
        fp = open(appdir + 'demo-log.txt', 'at', encoding='utf-8')
        ra = os.environ.get('REMOTE_ADDR', '')
        rh = '???'
        if ra:
            try:
                rh = socket.gethostbyaddr(ra)[0]
            except:
                pass
        else:
            ra = '[unknown]'
        fp.write('{} -- {} -- {} -- {} -- {}\n'.format(
            username,
            time.strftime('%d/%b/%Y-%H:%M', time.localtime()),
            ra,
            rh,
            os.environ.get('HTTP_USER_AGENT', '[unknown]')))
        fp.close()
    remember = getval('remember')
    if not username:
        u.html.exitMessage('Error', 'Missing value for username')
    if not passwd:
        u.html.exitMessage('Error', 'Missing password')
    if not re.match(r'[a-z][a-z0-9_]*$', username):
        u.html.exitMessage('Error', 'Invalid characters in username')

    try:
        em, us, pw = userbyuser(username)
        assert pw == passwd
    except:
        u.html.exitMessage('Error', 'Invalid username / password')

    c = cookies.SimpleCookie()
    c['L04u'] = u.login.mkString(username, passwd)
    c['L04u']['path'] = apprel

    if remember:
        days = 'Mon Tue Wed Thu Fri Sat Sun'.split()
        months = 'x Jan Feb Mar Apr May Jun Jul Aug Sep Oct Nov Dec'.split()
        tm_year, tm_mon, tm_day, tm_hour, tm_min, tm_sec, tm_wday, tm_yday, tm_isdst = time.gmtime(time.time() + 60 * 60 * 24 * 30)
        c['L04u']['expires'] = '{}, {:02d}-{}-{} {}:{:02d}:{:02d} GMT'.format(days[tm_wday], tm_day, months[tm_mon], tm_year, tm_hour, tm_min, tm_sec)

    sys.stdout.write('Location: {}bin/home\n{}\n\n'.format(appurl, c.output()))

def actionLogout():
    c = cookies.SimpleCookie()
    c['L04u'] = ''
    c['L04u']['path'] = apprel
    sys.stdout.write('Location: {}bin/home\n{}\n\n'.format(appurl, c.output()))

def actionRecover():
    username = getval('username')

    if not username:
        u.html.exitMessage('Error', 'Missing username/e-mail')

    if username.startswith('guest') or username.startswith('demo'):
        u.html.exitMessage('Error', 'No password for this user')

    if username.find('@') > -1:
        mail, user, password = userbymail(username)
    else:
        mail, user, password = userbyuser(re.sub('[^a-z0-9_]+', '', username))

    if not mail:
        u.html.exitMessage('Error', 'Unknown username/e-mail')

    u.mail.sendmail(mail, 'Your Gabmap account', '''
Here is your account info

Username: {}
Password: {}

{}

'''.format(user, password, appurl))
    u.html.exitMessage('Recover account',
                       '''Your account info was sent to {}
                       <p>
                       If you don\'t receive an e-mail, please contact {}
                       '''.format(escape(mail), contacthtml))


def actionCreate():
    global email, username
    email    = getval('email').lower()
    username = getval('username')
    password = getval('password')
    passwrd2 = getval('password2')

    errors = []

    if not email:
        errors.append('Missing value for e-mail address')
    if not username:
        errors.append('Missing value for username')
    if not (password and passwrd2):
        errors.append('Missing password')
    if password and password != passwrd2:
        errors.append('Passwords do not match')

    if email:
        valid = True
        if not re.match('[-.a-z0-9!#$%&\'*+/=?^_`{|}~]+@[-.a-z0-9]+$', email):
            valid = False
        elif email[0] == '.' or email[-1] == '.' or email.find('..') > -1 or email.find('.@') > -1 or email.find('@.') > -1:
            valid = False
        if not valid:
            errors.append('Malformed e-mail address')
            email = ''
        elif userbymail(email)[0]:
            errors.append('E-mail address already used')
            email = ''

    if username:
        if userbyuser(username)[0]:
            errors.append('Username already used')
            username = ''
        elif not re.match(r'[a-z][a-z0-9_]*$', username):
            errors.append('Invalid characters in username')
            username = ''
        elif username.startswith('guest') or username.startswith('demo'):
            errors.append('Reserved username')
            username = ''

    if errors:
        errorExitCreate(errors)

    pending = '.pending{}{}'.format(os.getpid(), username)
    url = '{}bin/account?action=confirm&id={}{}'.format(appurl, os.getpid(), username)

    fp = open(pending, 'wt', encoding='utf-8')
    fp.write('{}\t{}\t{}\n'.format(username, email, password))
    fp.close()
    os.chmod(pending, 0o600)

    u.mail.sendmail(email, 'Confirm your account', '\nVisit the url below to confirm your account\n\n' + url)
    u.html.exitMessage(
        'Create account',
        '''A message was sent to {}
        <p>
        Visit the link in that message to confirm your account
        <p>
        If you don\'t receive an e-mail, please contact {}
        '''.format(escape(email), contacthtml))


def actionConfirm():
    filename = '.pending' + re.sub('[^a-z0-9_]+', '', getval('id'))

    if not os.access(filename, os.F_OK):
        u.html.exitMessage('Error', 'The url you try is not valid, or it has expired, or your account has already been confirmed')

    fp = open(filename, 'rt', encoding='utf-8')
    username, email, password = fp.readline().strip('\r\n').split('\t')
    fp.close()
    os.remove(filename)
    os.mkdir(username)
    os.chdir(username)
    fp = open('passwd', 'wt', encoding='utf-8')
    fp.write(password + '\n')
    fp.close()
    os.chmod('passwd', 0o600)
    fp = open('email', 'wt', encoding='utf-8')
    fp.write(email + '\n')
    fp.close()
    open('TIMESTAMP', 'w').close()

    u.html.exitMessage('Confirmed', 'Your account has been confirmed\n<p>\nYou can now log in at the <a href="../">home page</a>')

#| main

os.chdir(datadir)

## remove .pending files that are too old
now = time.time()
for fname in os.listdir('.'):
    if not fname.startswith('.pending'):
        continue
    if now - os.stat(fname)[stat.ST_MTIME] > 3600:
        os.remove(fname)

form = cgi.FieldStorage()

action = getval('action')

if action == 'login':
    actionLogin()
elif action == 'logout':
    actionLogout()
elif action == 'recover':
    actionRecover()
elif action == 'create':
    actionCreate()
elif action == 'confirm':
    actionConfirm()
elif action == 'edit':
    actionEdit()
elif action == 'remove':
    actionRemove()
else:
    u.html.exitMessage('Error', 'Invalid action')



#| if main
if __name__ == "__main__":
    pass


