#!/usr/bin/env python

import subprocess
import os
import zipfile


def get_num_monitors():
    cmd_tuple = ('system_profiler', 'SPDisplaysDataType')
    cmd = subprocess.Popen(cmd_tuple, stdout=subprocess.PIPE)
    output = subprocess.check_output(('grep', 'Resolution'), stdin=cmd.stdout)
    cmd.wait()
    return output.decode("utf-8").count("Resolution")


def create_archive(directory, filenames):
    archive = '{}/screens.zip'.format(directory)
    zf = zipfile.ZipFile(archive, 'w', zipfile.ZIP_DEFLATED)
    for filename in filenames:
        zf.write(filename, arcname=os.path.basename(filename))
    zf.close()
    return archive


def capture(directory):
    num = get_num_monitors()
    args = ['screencapture', '-x']
    filenames = ['{}/{}.png'.format(directory, n) for n in range(num)]
    args.extend(filenames)
    subprocess.check_output(args)
    return [create_archive(directory, filenames)]


if __name__ == '__main__':
    capture('./')
