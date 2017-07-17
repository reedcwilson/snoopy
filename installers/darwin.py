#!/usr/bin/env python

import getpass
import subprocess
import base64
import shutil
import sys
import os
import re
_directory = os.path.dirname(os.path.abspath(__file__))
parentdir = os.path.dirname(_directory)
os.sys.path.insert(0, parentdir)
from lib.secrets_manager import SecretsManager


# NOTE: this script must be run from the root directory of the repository
mail_config          = 'mail.config'
snoopy_filename      = 'snoopy.py'
snoopy_spec_filename = 'snoopy.spec'
plist_filename       = "com.reedcwilson.snoopy.plist"
config_dir           = '{}/config'.format(parentdir)
launchd_path         = '{}/Library/LaunchAgents'.format(os.getenv('HOME'))


def replace_tokens(string, tokens, filename):
    '''replaces the tokens and creates a new file'''
    for key, value in tokens.items():
        string = string.replace(key, value)
    original_filename = "ORIGINAL_{}".format(filename)
    shutil.copy(filename, original_filename)
    with open(filename, 'w') as f:
        f.write(string)


def prepare_file(filename, tokens):
    string = ""
    with open(filename, 'r') as f:
        string = f.read()
    replace_tokens(string, tokens, filename)


def copy_plist(local_config_file, runtime_config_file, config_dir):
    with open(local_config_file, 'r') as f:
        config = f.read().replace("%INSTALL_DIR%", config_dir)
    with open(runtime_config_file, 'w') as f:
        f.write(config)


def load_plist(filename):
    subprocess.check_output(['launchctl', 'load', filename])


def purge(directory, pattern):
    for f in os.listdir(directory):
        if re.search(pattern, f):
            os.remove(os.path.join(directory, f))


def ensure_clean_directory():
    shutil.rmtree("./build", ignore_errors=True)
    shutil.rmtree("./dist", ignore_errors=True)
    shutil.rmtree("./__pycache__", ignore_errors=True)
    purge(parentdir, "^ORIGINAL_.*")
    purge(parentdir, ".*log$")
    purge(parentdir, ".*out$")


def extract_value(string):
    return string.split(":")[1].strip()


def load_inputs(filename):
    config = {}
    config_str = ""
    with open(filename, 'r') as f:
        config_str = f.read()
    lines = config_str.split("\n")
    for line in lines:
        if line.startswith('user'):
            config['user'] = extract_value(line)
        elif line.startswith('pwd'):
            config['pwd'] = extract_value(line)
        elif line.startswith('recipient'):
            config['recipient'] = extract_value(line)
        elif line.startswith('device'):
            config['device'] = extract_value(line)
        elif line.startswith('token'):
            config['token'] = extract_value(line)
    return config


def main():
    ensure_clean_directory()
    inputs = {}
    # you can pass a mail.config filename to be faster
    if len(sys.argv) > 1:
        inputs = load_inputs(sys.argv[1])
    else:
        # accept username, password, recipient, device, token
        inputs['user'] = input("gmail username: ")
        inputs['pwd'] = getpass.getpass("gmail password: ")
        inputs['recipient'] = input("recipient of emails: ")
        inputs['device'] = input("name of device: ")
        inputs['token'] = getpass.getpass("secure token: ")

    # create config
    config_str = ""
    for key, value in inputs.items():
        config_str += "{}:{}\n".format(key, value)

    # accept the secret encryption key
    secret_key = getpass.getpass("secret (should be different than token): ")

    print("preparing files...")

    # encrypt the mail config
    secrets_manager = SecretsManager(secret_key, mail_config)
    secrets_manager.put(config_str)

    # embed secret key in copy of snoopy.py and replace installation directory
    encoded_secret = base64.b64encode(secret_key.encode()).decode()
    tokens = {"SUPER_SECRET_KEY": encoded_secret, "HOME_DIRECTORY": parentdir}
    prepare_file(snoopy_filename, tokens)

    # replace tokens in snoopy.spec
    tokens = {"HOME_DIRECTORY": parentdir}
    prepare_file(snoopy_spec_filename, tokens)

    # install python dependencies

    # compile a.out
    print("compiling launchd reloader...")
    subprocess.check_output(['gcc', 'darwin/create_launchd.c'])

    # compile snoopy.spec
    print("compiling snoopy...")
    subprocess.check_output(['pyinstaller', 'snoopy.spec'])

    # replace the new snoopy.py and spec with the originals
    print("replacing originals...")
    snoopy_original = 'ORIGINAL_{}'.format(snoopy_filename)
    spec_original = 'ORIGINAL_{}'.format(snoopy_spec_filename)
    shutil.copy(snoopy_original, snoopy_filename)
    shutil.copy(spec_original, snoopy_spec_filename)
    os.remove(snoopy_original)
    os.remove(spec_original)

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
