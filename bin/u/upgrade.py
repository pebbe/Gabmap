#!/usr/bin/env python3


def salt():

    from filelock import FileLock
    import os

    bindir = os.environ['BINDIR']

    lock = FileLock(bindir + 'salt.lock', timeout=0)
    with lock:
        with open(bindir + 'INIT.sh', 'rt', errors='ignore') as fp:
            found = False
            for line in fp:
                a = line.split()
                if len(a) > 0 and a[0].startswith('SALT'):
                    found = True
                if len(a) > 1 and a[0] == 'export' and a[1].startswith('SALT'):
                    found = True
        if found:
            return
        
        import u.config
        from u.crypt import hash

        u.config.salt = os.urandom(16).hex()

        with open(bindir + 'INIT.sh', 'a') as fp:
            fp.write('\n')
            fp.write('# A random string used for hashing of sensitive information\n')
            fp.write('export SALT=' + u.config.salt + '\n')
        
        for item in os.listdir(u.config.datadir):
            filename = u.config.datadir + item
            if not os.path.isdir(filename):
                continue
            if item[0] == '.':
                continue
            for subfile in ('email', 'passwd'):
                name = filename + '/' + subfile
                if os.access(name, os.F_OK):
                    with open(name, 'rt') as fp:
                        txt = fp.read()
                    txt = txt.strip()
                    txt = hash(txt, u.config.salt)
                    with open(name + 'h', 'wt') as fp:
                        fp.write(txt + '\n')
                    os.remove(name)

