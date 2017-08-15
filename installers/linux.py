#!/usr/bin/env python

import os
import getpass
import subprocess
from common import Helper
from config_helper import ConfigHelper


# NOTE: this script must be run from the root directory of the repository
_directory            = os.path.dirname(os.path.abspath(__file__))
parentdir             = os.path.dirname(_directory)
snoopy_filename       = 'src/snoopy_linux.py'
snoopy_spec_filename  = 'src/snoopy_linux.spec'
sidecar_filename      = 'src/sidecar_linux.py'
sidecar_spec_filename = 'src/sidecar_linux.spec'
snoopy_systemd_file   = 'config/snoopy.service'
sidecar_systemd_file  = 'config/sidecar.service'
snoopy_systemd_name   = 'snoopy.service'
sidecar_systemd_name  = 'sidecar.service'
config_dir            = '{}/config'.format(parentdir)
launchd_path          = '/lib/systemd/system/'
start                 = 'src/linux/start.sh'


def main():
    helper = Helper()
    config_helper = ConfigHelper()
    config_helper.create_config()

    # REPLACE TOKENS IN FILES
    tokens = {
        "SUPER_SECRET_KEY": config_helper.get_encoded_secret(),
        "OPERATING_USER": getpass.getuser(),
        "HOME_DIRECTORY": parentdir
    }
    helper.prepare_file(snoopy_filename, tokens)

    tokens = {
        "HOME_DIRECTORY": parentdir
    }
    helper.prepare_file(sidecar_filename, tokens)

    tokens = {"HOME_DIRECTORY": '{}/src'.format(parentdir)}
    helper.prepare_file(snoopy_spec_filename, tokens)

    tokens = {"HOME_DIRECTORY": '{}/src'.format(parentdir)}
    helper.prepare_file(sidecar_spec_filename, tokens)

    # INSTALL PYTHON DEPENDENCIES

    # COMPILE
    helper.compile(snoopy_spec_filename)
    helper.compile(sidecar_spec_filename)

    # CLEANUP
    helper.replace_original(snoopy_filename)
    helper.replace_original(sidecar_filename)
    helper.replace_original(snoopy_spec_filename)
    helper.replace_original(sidecar_spec_filename)

    # INSTART
    print("starting daemon...")
    subprocess.check_output([
        start,
        snoopy_systemd_file,
        snoopy_systemd_name
    ])
    subprocess.check_output([
        start,
        sidecar_systemd_file,
        sidecar_systemd_name
    ])
    print("finished!")


if __name__ == '__main__':
    main()
