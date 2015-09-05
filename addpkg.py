#!/usr/bin/env python

"""
A work-in-progress script that can be used to add a package to a Debian
repository. Not suitable for any use yet.

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

if __name__ == '__main__':
    update_release()
    pkg_controls = {}
    for pkg in sys.argv[1:]:
        shutil.rmtree('./DEBIAN')
        subprocess.call(['dpkg', '-e', pkg])
        with open('./DEBIAN/control') as f:
            pkg_controls[pkg] = StringIO()
            for line in f:
                pkg_controls[pkg].write(line)
                if line.startswith('Section: '):
                    pkg_path = ''
                    pkg_controls[pkg].write('Filename: %s\n' % pkg_path)
        print(pkg_controls[pkg].getvalue())
