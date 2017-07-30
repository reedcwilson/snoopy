#!/usr/bin/env python

import os
import time
import subprocess
from common import Helper
from config_helper import ConfigHelper

# NOTE: this script must be run from the root directory of the repository
_directory            = os.path.dirname(os.path.abspath(__file__))
parentdir             = os.path.dirname(_directory)
snoopy_filename       = r'src\snoopy_win32.py'
sidecar_filename      = r'src\win32\sidecar.py'
snoopy_spec_filename  = r'src\snoopy_win32.spec'
sidecar_spec_filename = r'src\win32\sidecar.spec'
nssm_file             = r'{}\src\win32\nssm.exe'.format(parentdir)
snoopy                = r'{}\dist\snoopy\snoopy.exe'.format(parentdir)
sidecar               = r'{}\dist\sidecar\sidecar.exe'.format(parentdir)
snoopy_service        = 'snoopy'
sidecar_service       = 'sidecar'


def nssm(args, wait=True):
    cmd = [nssm_file]
    cmd.extend(args)
    c = subprocess.Popen(cmd)
    if wait:
        c.wait()


def install(serv, exe):
    print("installing service...")
    nssm([
        'install',
        serv,
        exe
    ])
    nssm(['set', serv, 'AppStopMethodSkip', '6'])
    nssm(['set', serv, 'AppDirectory', '{}'.format(parentdir)])
    nssm(['set', serv, 'AppStdout', r'{}\{}.out'.format(parentdir, serv)])
    nssm(['set', serv, 'AppStderr', r'{}\{}.err'.format(parentdir, serv)])


def start(serv):
    print("starting service...")
    nssm(['start', serv])


def cleanup(serv):
    print("cleaning up...")
    nssm(['stop', serv], False)
    cmd = subprocess.Popen(['sc', 'delete', serv])
    cmd.wait()
    time.sleep(1)


def main():
    cleanup(snoopy_service)
    cleanup(sidecar_service)
    home_directory = parentdir.replace('\\', '\\\\')

    helper = Helper()
    config_helper = ConfigHelper()
    config_helper.create_config()

    # REPLACE TOKENS

    tokens = {
        "SUPER_SECRET_KEY": helper.get_encoded_secret(),
        "HOME_DIRECTORY": home_directory
    }
    helper.prepare_file(snoopy_filename, tokens)

    tokens = {
        "SUPER_SECRET_KEY": helper.get_encoded_secret(),
        "HOME_DIRECTORY": home_directory
    }
    helper.prepare_file(sidecar_filename, tokens)

    tokens = {"HOME_DIRECTORY": r'{}\src'.format(home_directory)}
    helper.prepare_file(snoopy_spec_filename, tokens)

    tokens = {"HOME_DIRECTORY": r'{}\win32\src'.format(home_directory)}
    helper.prepare_file(sidecar_spec_filename, tokens)

    # INSTALL PYTHON DEPENDENCIES

    # COMPILE PROGRAMS

    helper.compile(snoopy_spec_filename)
    helper.compile(sidecar_spec_filename)

    # CLEANUP
    helper.replace_original(snoopy_filename)
    helper.replace_original(sidecar_filename)
    helper.replace_original(snoopy_spec_filename)
    helper.replace_original(sidecar_spec_filename)

    # INSTART
    install(snoopy_service, snoopy)
    install(sidecar_service, sidecar)
    time.sleep(2)
    start(snoopy_service)
    start(sidecar_service)

    print("finished!")


if __name__ == '__main__':
    main()
