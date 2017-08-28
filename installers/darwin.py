#!/usr/bin/env python

import os
import subprocess
import shutil
from common import Helper
from config_helper import ConfigHelper


# NOTE: this script must be run from the root directory of the repository
_directory           = os.path.dirname(os.path.abspath(__file__))
parentdir            = os.path.dirname(_directory)
snoopy_filename      = 'src/snoopy_darwin.py'
snoopy_spec_filename = 'src/snoopy_darwin.spec'
plist_filename       = "com.reedcwilson.snoopy.plist"
config_dir           = '{}/config'.format(parentdir)
launchd_path         = '/Library/LaunchAgents'


def copy_plist(local_config_file, runtime_config_file, config_dir):
    temp = '{}.temp'.format(local_config_file)
    with open(local_config_file, 'r') as f:
        config = f.read().replace("%INSTALL_DIR%", config_dir)
    with open(temp, 'w') as f:
        f.write(config)
    subprocess.check_output(['sudo', 'mv', temp, runtime_config_file])


def load_plist(filename):
    subprocess.check_output(['launchctl', 'load', filename])


def main():
    helper = Helper()
    config_helper = ConfigHelper()
    config_helper.create_config()
    # shutil.copy('mail.config', 'src/mail.config')

    # REPLACE TOKENS IN FILES
    tokens = {
        "SUPER_SECRET_KEY": config_helper.get_encoded_secret(),
        "HOME_DIRECTORY": parentdir
    }
    helper.prepare_file(snoopy_filename, tokens)
    tokens = {"HOME_DIRECTORY": '{}/src'.format(parentdir)}
    helper.prepare_file(snoopy_spec_filename, tokens)

    # INSTALL PYTHON DEPENDENCIES

    # COMPILE RELOADER -- needs to happen before we install snoopy
    print("compiling reloader...")
    subprocess.check_output(['gcc', 'src/darwin/create_launchd.c'])
    shutil.copy('a.out', 'src/a.out')

    # COMPILE PYTHON
    helper.compile(snoopy_spec_filename)

    # CLEANUP
    helper.replace_original(snoopy_filename)
    helper.replace_original(snoopy_spec_filename)

    # INSTART
    local_config_file = '{}/{}'.format(
        config_dir,
        plist_filename)
    runtime_config_file = '{}/{}'.format(
        launchd_path,
        plist_filename)
    print("starting daemon...")
    copy_plist(local_config_file, runtime_config_file, parentdir)
    load_plist(runtime_config_file)
    print("finished!")


if __name__ == '__main__':
    main()
