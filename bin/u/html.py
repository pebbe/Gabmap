#!/usr/bin/env python
"""
--documentation--
"""

__author__ = "Peter Kleiweg"
__version__ = "0.1"
__date__ = "2010/02/18"

#| imports

import os, re, sys

assert sys.stdout.encoding.lower() == 'utf-8'

import u.config as _c
import u.login as _l

#| globals

if _l.username:
    _logout = '<a href="{}bin/account?action=logout">log out</a>'.format(_c.appurl)
    # _logout += ' <a href="{}bin/account?action=edit">edit account</a>'.format(_c.appurl)
else:
    _logout = ''

_head = '''Content-type: text/html; charset=utf-8
Cache-Control: no-cache
Pragma: no-cache

<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.01 Transitional//EN" "http://www.w3.org/TR/html4/loose.dtd">
<html>
  <head>
    <title>Gabmap{{}}</title>
    <META NAME="ROBOTS" CONTENT="NOINDEX, NOFOLLOW">
    <link rel="stylesheet" type="text/css" href="{0}styles.css">
    <link rel="icon" href="{0}L04.ico" type="image/ico">
    {{}}
  </head>
  <body>
<!--
<center style="background-color:#800000;color:#ffffff;padding:.2em 0px">under development | grey means: not yet implemented</center>
-->
    <div id="header">
      <a href="{0}bin/home">home</a>
      <a href="{0}examples/" target="_blank">examples</a>
      <a href="{0}tools/">tools</a>
      {1}
      <a href="{2}" target="_blank">help</a>
      <a href="{3}" target="_blank">about</a>
      <a href="http://www.gabmap.nl" target="_blank">Gabmap</a>
    </div>
    {{}}
    <!-- START CONTENT -->


'''.format(_c.appurl, _logout,  _c.helpurl, _c.abouturl)

if _c.contactline:
    _a = _c.contactline
else:
    if _c.contact[:4] == 'http':
        _target = ' target="_blank"'
    else:
        _target = ''
    if not _c.contact:
        _a = '&nbsp;'
    elif _c.contactname:
        _a = 'contact: <a href="{}"{}>{}</a>'.format(_c.contact, _target, _c.contactname)
    else:
        _a = '<a href="{}"{}>contact</a>'.format(_c.contact, _target)
_foot = '''

    <!-- END CONTENT -->

    <div id="footer">
      {}
    </div>
  </body>
</html>
'''.format(_a) + '''<!-- Keep this comment at the end of the file
Local variables:
mode:''' + '''sgml
coding:utf-8
sgml-declaration:"HTML4.01/HTML4.decl"
sgml-omittag:t
sgml-shorttag:nil
End:
-->
'''

#| functions

def _iso2utf(m):
    return '{:c}'.format(int(m.group(1)))

def iso2utf(s):
    return re.sub('&#([0-9]+);', _iso2utf, s)


def escape(s):
    return s.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;').replace('"', '&quot;')

def head(title='', headers='', tip=False, maptip=False):
    ''' return start of html file, including http headers '''
    if title:
        title = ' - ' + title
    if tip:
        headers += '\n    <script type="text/javascript" src="../tip.js"></script>'
    if maptip:
        try:
            fp = open('../map/image.html', 'rt', encoding='utf-8')
            body = fp.read()
            fp.close()
        except:
            body = ''
    else:
        body = ''
    return _head.format(title, headers, body)

def foot():
    ''' return end of html file '''
    return _foot

def getBody(filename, dirname='templates/', getTitle=False):
    ''' return the body of html file, stored in template directory '''
    fp = open(_c.appdir + dirname + filename, 'rt', encoding='utf-8')
    txt = fp.read()
    fp.close()
    if getTitle:
        m = re.search('<title[^>]*>(.*?)</titl', txt, re.S)
        title = m.group(1)
    m = re.search('<body[^>]*>(.*)</body', txt, re.S)
    body = m.group(1)
    if getTitle:
        return (body, title)
    else:
        return body

def exitMessage(title, message):
    ''' print message end then exit '''
    sys.stdout.write(head(title))
    sys.stdout.write('<div class="message">\n<h1>{}</h1>\n{}\n</div>\n'.format(title, message))
    sys.stdout.write(foot())
    sys.exit()

def loginCheck():
    # this function can't be in login.py because of circular imports
    if not _l.username:
        exitMessage('Error', 'You are not logged in')

def busy(path='.'):
    try:
        fp = open(path + '/QUEUED', 'rt')
        s = int(fp.read())
        fp.close()
        queue = len([y for y in [int(x) for x in os.listdir(_c.datadir + '.queue') if re.match('[0-9]+$', x)] if y <= s])
    except:
        queue = 'unknown'
    return '''
    Your data is being processed, this may take a few minutes.
    <p>
    Queue size: {}
    <p>
    <img src="{}img/busy.gif" alt="busy">
    <script language="JavaScript"><!--
    setTimeout("location.reload(true);", 5000);
    //--></script>
    '''.format(queue, _c.appurl)

def makeError(path):
    return '''
    Something went wrong.
    View <a href="{}bin/makelog?p={}" target="_blank">logfile</a>.
    '''.format(_c.appurl, path)

def img(path, bw=False, usemap=None, noover=False, idx=0, imgpath=None, pseudoforce=False):
    if usemap:
        xx = os.getpid()
        if noover:
            u = ' usemap="#{}" border="0"'.format(usemap)
        else:
            if not imgpath:
                imgpath = path.split('-')[0]
            if os.access('../map/mapover.png', os.F_OK):
                if not pseudoforce and os.access('../map/PSEUDOMAP', os.F_OK):
                    u = ' usemap="#{}" border="0"'.format(usemap)
                else:
                    u = ''' usemap="#{0}" border="0"
                    style="background-image:url({1}bin/get?p={2}.png&xx={5})"
                    onmouseover="setPoints(this, '{1}bin/get?p={3}-map-mapover.png&xx={5}',{4})"
                    onmouseout="restore(this, '{1}bin/get?p={2}.png&xx={5}')"
                    '''.format(usemap, _c.appurl, path, imgpath, idx, xx)
            else:
                u = ''
    else:
        u = ''
    if bw:
        return '''
        <div class="img">
        <img src="{0}bin/get?p={1}.png" align="left"{2}>
        <div class="imlink">
        <a href="{0}bin/get?p={1}.eps&i=1">eps</a><br>
        <a href="{0}bin/get?p={1}.eps&i=1&b=1">eps-bw</a><br>
        <a href="{0}bin/get?p={1}.pdf&i=1">pdf</a><br>
        <a href="{0}bin/get?p={1}.pdf&i=1&b=1">pdf-bw</a><br>
        <a href="{0}bin/get?p={1}.png&i=1">png</a><br>
        <a href="{0}bin/get?p={1}.png&i=1&b=1">png-bw</a><br clear="all">
        </div>
        </div>
        '''.format(_c.appurl, path, u)
    else:
        return '''
        <div class="img">
        <img src="{0}bin/get?p={1}.png" align="left"{2}>
        <div class="imlink">
        <a href="{0}bin/get?p={1}.eps&i=1">eps</a><br>
        <a href="{0}bin/get?p={1}.pdf&i=1">pdf</a><br>
        <a href="{0}bin/get?p={1}.png&i=1">png</a><br clear="all">
        </div>
        </div>
        '''.format(_c.appurl, path, u)

def html2js(h):
    h = h.replace('&gt;', '>').replace('&lt;', '<').replace('&quot;', '"').replace('&amp;', '&')
    h = h.replace('\\', '\\\\').replace('"', '\\"').replace("'", "\\'")
    return h


def help(s):
    return '<a href="{}bin/help?s={}" class="help" target="_blank">?</a>'.format(_c.appurl, s)

def more(s):
    return '<a href="{}bin/help?s={}" class="more" target="_blank">Read&nbsp;more&nbsp;&rarr;</a>'.format(_c.appurl, s)

#| main


#| if main
if __name__ == "__main__":
    pass
