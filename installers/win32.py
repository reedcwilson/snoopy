#!/usr/bin/env python

import os
import time
import subprocess
from common import Helper

# NOTE: this script must be run from the root directory of the repository
_directory           = os.path.dirname(os.path.abspath(__file__))
parentdir            = os.path.dirname(_directory)
snoopy_filename      = 'snoopy_win32.py'
snoopy_spec_filename = 'snoopy_win32.spec'
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
        'python',
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
    helper.replace_tokens(snoopy_filename, snoopy_spec_filename)

    # install python dependencies

    # compile reloader -- needs to happen before we install snoopy
    print("compiling reloader...")
    subprocess.check_output([
        "{}\\installers\\c_compile_windows.bat".format(parentdir)
    ])

    helper.compile(snoopy_spec_filename)
    helper.replace_originals(snoopy_filename, snoopy_spec_filename)

    install()
    time.sleep(2)
    start()
    print("finished!")


if __name__ == '__main__':
    main()
