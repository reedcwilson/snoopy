#!/usr/bin/env python

import shutil
import re
import os
import subprocess
_directory = os.path.dirname(os.path.abspath(__file__))
parentdir = os.path.dirname(_directory)


def replace_tokens(string, tokens, filename):
    '''replaces the tokens and creates a new file'''
    for key, value in tokens.items():
        string = string.replace(key, value)
    original_filename = get_altered_filename(filename)
    shutil.copy(filename, original_filename)
    with open(filename, 'w', newline='\n') as f:
        f.write(string)


def purge(directory, pattern):
    for f in os.listdir(directory):
        if re.search(pattern, f):
            os.remove(os.path.join(directory, f))


def ensure_clean_directory():
    shutil.rmtree("./build", ignore_errors=True)
    shutil.rmtree("./dist", ignore_errors=True)
    shutil.rmtree("./__pycache__", ignore_errors=True)
    shutil.rmtree("./screenshots", ignore_errors=True)
    purge(parentdir, "^ORIGINAL_.*")
    purge(parentdir, ".*png$")
    purge(parentdir, ".*log$")
    purge(parentdir, ".*out$")
    purge(parentdir, ".*err$")
    purge(parentdir, ".*zip$")
    purge(parentdir, "reload_service.exe")
    purge(parentdir, "reload_service.obj")


def get_altered_filename(filename, backup=True):
    parts = filename.split(os.sep)
    if backup:
        parts[-1] = 'ORIGINAL_{}'.format(parts[-1])
    return os.sep.join(parts)


class Helper:
    def __init__(self):
        ensure_clean_directory()

    def prepare_file(self, filename, tokens):
        string = ""
        with open(filename, 'r') as f:
            string = f.read()
        replace_tokens(string, tokens, filename)

    def replace_original(self, filename):
        original = get_altered_filename(filename)
        shutil.copy(original, filename)
        os.remove(original)

    def compile(self, filename):
        # compile snoopy.spec
        print("compiling snoopy...")
        subprocess.check_output(['pyinstaller', '-y', filename])
