#!/usr/bin/env python

import os
import time
import subprocess
import shutil
from common import Helper

# NOTE: this script must be run from the root directory of the repository
_directory           = os.path.dirname(os.path.abspath(__file__))
parentdir            = os.path.dirname(_directory)
snoopy_filename      = 'snoopy_win32.py'
snoopy_spec_filename = 'snoopy_win32.spec'
c_file               = 'reload_service.c'
nssm_file            = '{}\\win32\\nssm.exe'.format(parentdir)
snoopy               = '{}\\dist\\snoopy\\snoopy.exe'.format(parentdir)
service              = 'snoopy'


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
        snoopy
    ])
    nssm(['set', service, 'AppStopMethodSkip', '6'])
    nssm(['set', service, 'AppDirectory', '{}'.format(parentdir)])
    nssm(['set', service, 'AppStdout', '{}\\windows.out'.format(parentdir)])
    nssm(['set', service, 'AppStderr', '{}\\windows.err'.format(parentdir)])


def start():
    print("starting service...")
    nssm(['start', service])


def cleanup():
    print("cleaning up...")
    nssm(['stop', service], False)
    cmd = subprocess.Popen(['sc', 'delete', service])
    cmd.wait()
    time.sleep(1)


def main():
    cleanup()
    home_directory = parentdir.replace('\\', '\\\\')

    helper = Helper()
    helper.create_config()

    tokens = {
        "SUPER_SECRET_KEY": helper.get_encoded_secret(),
        "HOME_DIRECTORY": home_directory
    }
    helper.prepare_file(snoopy_filename, tokens)

    tokens = {"HOME_DIRECTORY": home_directory}
    helper.prepare_file(snoopy_spec_filename, tokens)

    tokens = {"HOME_DIRECTORY": home_directory}
    shutil.copy(
        "{}\\win32\\{}".format(home_directory, c_file),
        "{}\\{}".format(home_directory, c_file))
    helper.prepare_file(c_file, tokens)

    # install python dependencies

    # compile reloader -- needs to happen before we install snoopy
    print("compiling reloader...")
    subprocess.check_output([
        "{}\\installers\\c_compile_windows.bat".format(home_directory)
    ])

    helper.compile(snoopy_spec_filename)
    helper.replace_original(snoopy_filename)
    helper.replace_original(snoopy_spec_filename)
    helper.replace_original(c_file)
    os.remove(c_file)
    os.remove('reload_service.exe')
    os.remove('reload_service.obj')

    install()
    time.sleep(2)
    start()
    print("finished!")


if __name__ == '__main__':
    main()
