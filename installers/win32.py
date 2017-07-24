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
nssm_file            = '{}\\dist\\snoopy\\nssm.exe'.format(parentdir)
snoopy               = '{}\\dist\\snoopy\\snoopy.exe'.format(parentdir)
service              = 'snoopy'


def nssm(args):
    cmd = [nssm_file]
    cmd.extend(args)
    subprocess.check_output(cmd)


def install():
    print("installing service...")
    nssm([
        'install',
        service,
        snoopy
    ])
    nssm(['set', service, 'AppStopMethodSkip', '6'])
    nssm(['set', service, 'AppStdout', '{}\\out.log'.format(parentdir)])
    nssm(['set', service, 'AppStderr', '{}\\out.log'.format(parentdir)])


def start():
    print("starting service...")
    nssm(['start', service])


def main():
    helper = Helper()
    helper.create_config()
    tokens = {
        "SUPER_SECRET_KEY": helper.get_encoded_secret(),
        "HOME_DIRECTORY": parentdir
    }
    helper.prepare_file(snoopy_filename, tokens)
    tokens = {"HOME_DIRECTORY": parentdir}
    helper.prepare_file(snoopy_spec_filename, tokens)

    tokens = {"HOME_DIRECTORY": parentdir.replace("\\", "\\\\")}
    shutil.copy("win32\\{}".format(c_file), c_file)
    helper.prepare_file(c_file, tokens)

    # install python dependencies

    # compile reloader -- needs to happen before we install snoopy
    print("compiling reloader...")
    subprocess.check_output([
        "{}\\installers\\c_compile_windows.bat".format(parentdir)
    ])

    helper.compile(snoopy_spec_filename)
    helper.replace_original(snoopy_filename)
    helper.replace_original(snoopy_spec_filename)
    helper.replace_original(c_file)
    os.remove(c_file)

    install()
    time.sleep(2)
    start()
    print("finished!")


if __name__ == '__main__':
    main()
