#!/usr/bin/env python

import os
import subprocess
from common import Helper


# NOTE: this script must be run from the root directory of the repository
_directory           = os.path.dirname(os.path.abspath(__file__))
parentdir            = os.path.dirname(_directory)
filename             = 'collector.py'
spec_filename        = 'collector.spec'


def main():
    helper = Helper()

    # install python dependencies
    # pip install --upgrade google-api-python-client

    tokens = {"HOME_DIRECTORY": '{}/src'.format(parentdir)}
    helper.prepare_file('src/{}'.format(filename), tokens)

    tokens = {"HOME_DIRECTORY": '{}/src'.format(parentdir)}
    helper.prepare_file('src/{}'.format(spec_filename), tokens)

    helper.compile('src/{}'.format(spec_filename))

    subprocess.check_output(['rm', '-rf', 'collector/'])
    subprocess.check_output(['mkdir', 'collector/'])
    subprocess.check_output(['cp', 'installers/collector.sh', 'collector/'])
    subprocess.check_output(['cp', 'config/com.reedcwilson.collector.plist', 'collector/'])
    subprocess.check_output(['cp', '-r', 'dist', 'build', 'collector/'])
    os.chdir('collector/')
    subprocess.check_output(['zip', '-r', 'collector.zip', '.'])
    subprocess.check_output(['cp', 'collector.zip', '..'])
    os.chdir('..')
    subprocess.check_output(['rm', '-rf', 'collector/', 'collector.sh', 'com.reedcwilson.collector.plist'])
    print("finished!")


if __name__ == '__main__':
    main()
