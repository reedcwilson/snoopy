#!/usr/local/env python

import subprocess
import os
import zipfile


def create_archive(directory, filenames):
    archive = '{}/screens.zip'.format(directory)
    zf = zipfile.ZipFile(archive, 'w', zipfile.ZIP_DEFLATED)
    for filename in filenames:
        zf.write(filename, arcname=os.path.basename(filename))
    zf.close()
    return archive


def capture(directory):
    filename = '{}/screens.png'.format(directory)
    args = ['scrot', filename]
    subprocess.check_output(args)
    return [create_archive(directory, [filename])]


if __name__ == '__main__':
    import time
    import traceback
    try:
        for i in range(10):
            capture('{}/code/snoopy/src/linux'.format(os.path.expanduser('~')))
            time.sleep(3)
    except Exception as e:
        with open('{}/snoopy.log'.format(os.path.expanduser('~')), 'a') as f:
            f.write(traceback.format_exc())
