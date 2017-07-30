#!/usr/bin/env python

import os
import subprocess
from common import Helper


# NOTE: this script must be run from the root directory of the repository
_directory           = os.path.dirname(os.path.abspath(__file__))
parentdir            = os.path.dirname(_directory)
filename             = 'collector.py'
spec_filename        = 'collector.spec'
plist_filename       = "com.reedcwilson.collector.plist"
config_dir           = '{}/config'.format(parentdir)
launchd_path         = '{}/Library/LaunchAgents'.format(os.getenv('HOME'))


def copy_plist(local_config_file, runtime_config_file, config_dir):
    with open(local_config_file, 'r') as f:
        config = f.read().replace("%INSTALL_DIR%", config_dir)
    with open(runtime_config_file, 'w') as f:
        f.write(config)


def load_plist(filename):
    subprocess.check_output(['launchctl', 'load', filename])


def main():
    helper = Helper()

    # install python dependencies
    # pip install --upgrade google-api-python-client

    print("starting daemon...")
    local_config_file = '{}/{}'.format(
        config_dir,
        plist_filename)
    runtime_config_file = '{}/{}'.format(
        launchd_path,
        plist_filename)

    tokens = {"HOME_DIRECTORY": '{}/src'.format(parentdir)}
    helper.prepare_file('src/{}'.format(filename), tokens)

    tokens = {"HOME_DIRECTORY": '{}/src'.format(parentdir)}
    helper.prepare_file('src/{}'.format(spec_filename), tokens)

    helper.compile('src/{}'.format(spec_filename))

    copy_plist(local_config_file, runtime_config_file, parentdir)
    load_plist(runtime_config_file)
    print("finished!")


if __name__ == '__main__':
    main()
