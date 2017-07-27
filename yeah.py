#!/usr/bin/env python

import os
import time
import subprocess

# NOTE: this script must be run from the root directory of the repository
_directory           = os.path.dirname(os.path.abspath(__file__))
# parentdir            = os.path.dirname(_directory)
parentdir            = _directory
snoopy_filename      = 'sample.py'
c_file               = 'burp.c'
nssm_file            = r'{}\win32\nssm.exe'.format(parentdir)
snoopy               = r'{}\win32\sample.py'.format(parentdir)
service              = 'sample'


def nssm(args, wait=True):
    cmd = [nssm_file]
    cmd.extend(args)
    c = subprocess.Popen(cmd)
    if wait:
        c.wait()


def install():
    print("installing service...")
    nssm([
        'install',
        service,
        'python',
        snoopy
    ])
    nssm(['set', service, 'AppStopMethodSkip', '6'])
    nssm(['set', service, 'AppDirectory', '{}'.format(parentdir)])
    nssm(['set', service, 'AppStdout', r'{}\windows.out'.format(parentdir)])
    nssm(['set', service, 'AppStderr', r'{}\windows.err'.format(parentdir)])


def start():
    print("starting service...")
    nssm(['start', service])


def cleanup():
    print("cleaning up...")
    nssm(['stop', service], False)
    cmd = subprocess.Popen(['sc', 'delete', service])
    cmd.wait()
    time.sleep(1)


def remove_file(filename):
    try:
        os.remove('burp.obj')
    except:
        pass


def main():
    cleanup()

    # install python dependencies

    # compile reloader -- needs to happen before we install snoopy
    try:
        remove_file('burp.obj')
        remove_file(r'C:\reload.out')
        remove_file(r'C:\killer.out')
        remove_file('sample.out')
        remove_file('sample.err')
        remove_file('windows.out')
        remove_file('windows.err')
    except:
        pass

    install()
    time.sleep(2)
    start()
    print("finished!")


if __name__ == '__main__':
    main()
