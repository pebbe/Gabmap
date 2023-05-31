#!/usr/bin/env python3
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
from u.crypt import hash

#| globals

if contact[:4] == 'http':
    _t = ' target="_blank"'
else:
    _t = ''
contacthtml = '<a href="{}"{}>{}</a>'.format(contact, _t, contactname)

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
            fp = open(fname + '/passwdh', 'rt', encoding='utf-8')
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
        fp = open(user + '/passwdh', 'rt', encoding='utf-8')
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
    sys.stdout.write(u.html.getBody('accountCreate.html').format({'binurls':binurls,
                                                                  'errors':err,
                                                                  'email':email,
                                                                  'username':username}))
    sys.stdout.write(u.html.foot())
    sys.exit()

def errorExitUpdateUserPass(errors):
    err = ''
    for e in errors:
        err += '<div class="error">\nError: ' + e + '\n</div>\n'
    sys.stdout.write(u.html.head('error'))
    sys.stdout.write(u.html.getBody('accountUpdateUserPass.html').format({'binurls':binurls,
                                                                  'errors':err,
                                                                  'email':email}))
    sys.stdout.write(u.html.foot())
    sys.exit()

def errorExitUpdateMail(errors):
    err = ''
    for e in errors:
        err += '<div class="error">\nError: ' + e + '\n</div>\n'
    sys.stdout.write(u.html.head('error'))
    sys.stdout.write(u.html.getBody('accountUpdateMail.html').format({'binurls':binurls,
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
    if not username:
        u.html.exitMessage('Error', 'Missing value for username')
    if not passwd:
        u.html.exitMessage('Error', 'Missing password')
    if not re.match(r'[a-z][a-z0-9_]*$', username):
        u.html.exitMessage('Error', 'Invalid characters in username')

    try:
        _, _, pw = userbyuser(username)
        assert pw == hash(passwd, salt)
    except:
        u.html.exitMessage('Error', 'Invalid username / password')

    c = cookies.SimpleCookie()
    c['L04u'] = u.login.mkString(username, pw)
    c['L04u']['path'] = binrel

    days = 'Mon Tue Wed Thu Fri Sat Sun'.split()
    months = 'x Jan Feb Mar Apr May Jun Jul Aug Sep Oct Nov Dec'.split()
    tm_year, tm_mon, tm_day, tm_hour, tm_min, tm_sec, tm_wday, tm_yday, tm_isdst = time.gmtime(time.time() + 60 * 60 * 24)
    c['L04u']['expires'] = '{}, {:02d}-{}-{} {}:{:02d}:{:02d} GMT'.format(days[tm_wday], tm_day, months[tm_mon], tm_year, tm_hour, tm_min, tm_sec)

    sys.stdout.write('Location: {}home\n{}\n\n'.format(binurl, c.output()))

def actionLogout():
    c = cookies.SimpleCookie()
    c['L04u'] = ''
    c['L04u']['path'] = binrel
    sys.stdout.write('Location: {}home\n{}\n\n'.format(binurl, c.output()))

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

    password = hash(password, salt)

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
    url = '{}account?action=confirm&id={}{}'.format(binurl, os.getpid(), username)

    fp = open(pending, 'wt', encoding='utf-8')
    fp.write('{}\t{}\t{}\tcreate\n'.format(username, email, password))
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


def actionUpdateUserPass():
    global email, username
    email    = getval('email').lower()
    username = getval('username')
    password = getval('password')
    passwrd2 = getval('password2')

    errors = []

    if not email:
        errors.append('Missing value for e-mail address')
    if not (username or password):
        errors.append('Missing value for username and password, at least one should be provided')
    if password and password != passwrd2:
        errors.append('Passwords do not match')

    valid = False
    if email:
        valid = True
        if not re.match('[-.a-z0-9!#$%&\'*+/=?^_`{|}~]+@[-.a-z0-9]+$', email):
            valid = False
        elif email[0] == '.' or email[-1] == '.' or email.find('..') > -1 or email.find('.@') > -1 or email.find('@.') > -1:
            valid = False
        if not valid:
            errors.append('Malformed e-mail address')
            email = ''
    if not valid:
        errorExitUpdateUserPass(errors)


    mail_by_mail, name_by_mail, pw_by_mail = userbymail(email)
    if not mail_by_mail:
        errors.append('No user for this e-mail found')
        errorExitUpdateUserPass(errors)

    if not username:
        username = name_by_mail
    if password:
        password = hash(password, salt)
    else:
        password = pw_by_mail

    mail_by_user, name_by_user, pw_by_user = userbyuser(username)
    if mail_by_user:
        if mail_by_user != email:
            errors.append('Username already used')
            username = ''

    if not re.match(r'[a-z][a-z0-9_]*$', username):
        errors.append('Invalid characters in username')
        username = ''
    elif username.startswith('guest') or username.startswith('demo'):
        errors.append('Reserved username')
        username = ''

    if errors:
        errorExitUpdateUserPass(errors)

    pending = '.pending{}{}'.format(os.getpid(), username)
    url = '{}account?action=confirm&id={}{}'.format(binurl, os.getpid(), username)

    fp = open(pending, 'wt', encoding='utf-8')
    fp.write('{}\t{}\t{}\tuserpass\n'.format(username, email, password))
    fp.close()
    os.chmod(pending, 0o600)

    u.mail.sendmail(email, 'Confirm your account update', '\nVisit the url below to confirm your account update\n\n' + url)
    u.html.exitMessage(
        'Account update',
        '''A message was sent to {}
        <p>
        Visit the link in that message to confirm your account update
        <p>
        If you don\'t receive an e-mail, please contact {}
        '''.format(escape(email), contacthtml))


def actionUpdateMail():
    global email, username
    email    = getval('email').lower()
    username = getval('username')
    password = getval('password')

    errors = []

    if not email:
        errors.append('Missing value for e-mail address')
    if not username:
        errors.append('Missing value for username')
    if not password:
        errors.append('Missing password')
    if errors:
        errorExitUpdateMail(errors)

    password = hash(password, salt)

    valid = True
    if not re.match('[-.a-z0-9!#$%&\'*+/=?^_`{|}~]+@[-.a-z0-9]+$', email):
        valid = False
    elif email[0] == '.' or email[-1] == '.' or email.find('..') > -1 or email.find('.@') > -1 or email.find('@.') > -1:
        valid = False
    if not valid:
        errors.append('Malformed e-mail address')
        email = ''
    if not valid:
        errorExitUpdateMail(errors)

    _, _, pw = userbyuser(username)
    if pw != password:
        errors.append("Invalid username / password")
        errorExitUpdateMail(errors)

    ma, _, _ = userbymail(email)
    if ma:
        errors.append("E-mail address already in use")
        errorExitUpdateMail(errors)

    pending = '.pending{}{}'.format(os.getpid(), username)
    url = '{}account?action=confirm&id={}{}'.format(binurl, os.getpid(), username)

    fp = open(pending, 'wt', encoding='utf-8')
    fp.write('{}\t{}\t{}\tmail\n'.format(username, email, password))
    fp.close()
    os.chmod(pending, 0o600)

    u.mail.sendmail(email, 'Confirm your account update', '\nVisit the url below to confirm your account update\n\n' + url)
    u.html.exitMessage(
        'Account update',
        '''A message was sent to {}
        <p>
        Visit the link in that message to confirm your account update
        <p>
        If you don\'t receive an e-mail, please contact {}
        '''.format(escape(email), contacthtml))


def actionConfirm():
    filename = '.pending' + re.sub('[^a-z0-9_]+', '', getval('id'))

    if not os.access(filename, os.F_OK):
        u.html.exitMessage('Error', 'The url you try is not valid, or it has expired, or your account has already been confirmed')

    fp = open(filename, 'rt', encoding='utf-8')
    username, email, password, action = fp.readline().strip('\r\n').split('\t')
    fp.close()
    os.remove(filename)

    if action == 'create':

        os.mkdir(username)
        os.chdir(username)
        fp = open('passwdh', 'wt', encoding='utf-8')
        fp.write(password + '\n')
        fp.close()
        os.chmod('passwdh', 0o600)
        fp = open('email', 'wt', encoding='utf-8')
        fp.write(email + '\n')
        fp.close()
        open('TIMESTAMP', 'w').close()

        u.html.exitMessage('Confirmed', 'Your account has been confirmed\n<p>\nYou can now log in at the <a href="home">home page</a>')

    elif action == 'userpass':

        _, un, _ = userbymail(email)
        if un != username:
            os.rename(un, username)
        os.chdir(username)
        fp = open('passwdh', 'wt', encoding='utf-8')
        fp.write(password + '\n')
        fp.close()
        open('TIMESTAMP', 'w').close()

        u.html.exitMessage('Confirmed', 'Your account update has been confirmed\n<p>\nYou can now log in at the <a href="home">home page</a>')

    elif action == 'mail':
        os.chdir(username)
        fp = open('email', 'wt', encoding='utf-8')
        fp.write(email + '\n')
        fp.close()
        open('TIMESTAMP', 'w').close()

        u.html.exitMessage('Confirmed', 'Your account update has been confirmed\n<p>\nYou can now log in at the <a href="home">home page</a>')



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
elif action == 'create':
    actionCreate()
elif action == 'confirm':
    actionConfirm()
elif action == 'updateuserpass':
    actionUpdateUserPass()
elif action == 'updatemail':
    actionUpdateMail()
else:
    u.html.exitMessage('Error', 'Invalid action')



#| if main
if __name__ == "__main__":
    pass


