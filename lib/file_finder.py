#!/usr/bin/env python

import os
import sys


def get_embedded_filename(filename):
    if hasattr(sys, '_MEIPASS'):
        # PyInstaller >= 1.6
        os.chdir(sys._MEIPASS)
        filename = os.path.join(sys._MEIPASS, filename)
    elif '_MEIPASS2' in os.environ:
        # PyInstaller < 1.6 (tested on 1.5 only)
        os.chdir(os.environ['_MEIPASS2'])
        filename = os.path.join(os.environ['_MEIPASS2'], filename)
    else:
        os.chdir(os.path.dirname(sys.argv[0]))
        filename = os.path.join(os.path.dirname(sys.argv[0]), filename)
    return filename
