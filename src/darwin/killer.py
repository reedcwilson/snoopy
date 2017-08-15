#!/usr/local/env python

import signal
import time
import sys
import os
import subprocess


class GracefulKiller:
    def __init__(self, reloader_filename, notifier, critical_files):
        signal.signal(signal.SIGHUP, self.exit)
        signal.signal(signal.SIGINT, self.exit)
        signal.signal(signal.SIGTERM, self.exit)
        self.critical_files = critical_files
        self.reloader = reloader_filename
        self.notifier = notifier

    def install_is_happy(self):
        for filename in self.critical_files:
            if not os.path.isfile(filename):
                return False
        return True

    def exit(self, signum, frame):
        self.notifier.send(subject="Shutting down")
        pid = os.fork()
        if pid == 0:
            subprocess.call([self.reloader])
        time.sleep(1)
        if pid != 0:
            if not self.install_is_happy():
                self.notifier.send(
                    subject="Alert! Installation directory is unhealthy")
        sys.exit(0)
