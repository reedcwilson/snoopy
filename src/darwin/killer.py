#!/usr/local/env python

import signal
import time
import sys
import os
import subprocess


class GracefulKiller:
    def __init__(self, reloader_filename, notifier):
        signal.signal(signal.SIGHUP, self.exit)
        signal.signal(signal.SIGINT, self.exit)
        signal.signal(signal.SIGTERM, self.exit)
        self.reloader = reloader_filename
        self.notifier = notifier

    def exit(self, signum, frame):
        self.notifier.send(subject="Shutting down")
        pid = os.fork()
        if pid == 0:
            subprocess.call([self.reloader])
        time.sleep(1)
        sys.exit(0)
