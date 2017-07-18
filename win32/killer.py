#!/usr/local/env python

import signal
import time
import sys
# import os
# import subprocess
import win32api


class GracefulKiller:
    def __init__(self, notifier):
        try:
            win32api.SetConsoleCtrlHandler(self.exit_gracefully, True)
        except ImportError:
            version = ".".join(map(str, sys.version_info[:2]))
            raise Exception("pywin32 not installed for Python " + version)
        signal.signal(signal.SIGHUP, self.exit_gracefully)
        signal.signal(signal.SIGINT, self.exit_gracefully)
        signal.signal(signal.SIGTERM, self.exit_gracefully)
        self.notifier = notifier

    def exit(self):
        time.sleep(1)
        sys.exit(0)

    def exit_gracefully(self, signum, frame):
        # self.notifier.send(subject="Shutting down")
        print("shutting down")
        # pid = os.fork()
        # if pid == 0:
        #     subprocess.call([self.reloader])
        self.exit()
