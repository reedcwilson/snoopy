#!/usr/bin/env python

import os
from os.path import join, abspath, dirname
import sys


def get_embedded_filename(filename):
    if hasattr(sys, '_MEIPASS'):
        # PyInstaller >= 1.6
        os.chdir(sys._MEIPASS)
        filename = join(sys._MEIPASS, filename)
    elif '_MEIPASS2' in os.environ:
        # PyInstaller < 1.6 (tested on 1.5 only)
        os.chdir(os.environ['_MEIPASS2'])
        filename = join(os.environ['_MEIPASS2'], filename)
    else:
        filename = join(abspath(dirname(sys.argv[0])), filename)
    return filename
