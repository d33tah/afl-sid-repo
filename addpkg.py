#!/usr/bin/env python

"""
Script that can be used to add a package to a Debian repository.

Usage:
    ./addpkg.py /tmp/some-package-pulled-from-docker.deb
    git add pool
    git commit -a -m 'Add some-package-pulled-from-docker'

AUTHOR: Jacek Wielemborek, licensed under WTFPL.
"""

import os
import subprocess
import shutil
import sys
from StringIO import StringIO

def get_file_hash(mode, full_filename):
    args = [mode, full_filename]
    try:
        file_hash = subprocess.check_output(args,
                                            stderr=subprocess.PIPE).split()[0]
    except subprocess.CalledProcessError:
        file_hash = get_file_hash(mode, '/dev/null')
    return file_hash


def update_release():
    """Find all Release files in the dists/*/ and update their checksums."""
    releases = list(os.walk('./dists'))[0][1]
    for release in releases:
        mode = None
        s = StringIO()
        release_filename = './dists/%s/Release' % release
        with open(release_filename) as f:
            for line in f:
                if line.startswith('MD5Sum:'):
                    mode = 'md5sum'
                    s.write(line)
                elif line.startswith('SHA1:'):
                    mode = 'sha1sum'
                    s.write(line)
                elif line.startswith('SHA256:'):
                    mode = 'sha256sum'
                    s.write(line)
                elif mode is not None:
                    filename = line.split()[2]
                    full_filename = './dists/%s/%s' % (release, filename)
                    file_hash = get_file_hash(mode, full_filename)
                    try:
                        file_size = os.stat(full_filename).st_size
                    except OSError:
                        file_size = 0
                    s.write(" %s %d %s\n" % (file_hash, file_size, filename))
                else:
                    s.write(line)
        with open(release_filename, "w") as f:
            f.write(s.getvalue())

def main():
    sys.stderr.write('Copying the pacakges...\n')
    for pkg in sys.argv[1:]:
        bname = os.path.basename(pkg)
        if bname.startswith('lib'):
            dname = bname[:4]
        else:
            dname = bname[0]
        pooldir = 'pool/main/%s/' % dname
        try:
            os.mkdir(pooldir)
        except OSError:
            pass
        shutil.copy(pkg, '%s%s' % (pooldir, bname))
    sys.stderr.write('Rebuilding the package list...\n')
    subprocess.call('dpkg-scanpackages pool >'
                    ' dists/sid/main/binary-amd64/Packages', shell=True)
    subprocess.call('gzip < dists/sid/main/binary-amd64/Packages'
                    ' > dists/sid/main/binary-amd64/Packages.gz', shell=True)
    update_release()

if __name__ == '__main__':
    main()
