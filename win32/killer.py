#!/usr/local/env python

import time
import sys
import subprocess
import traceback


class GracefulKiller:
    def __init__(self, daemon, reloader):
        self.daemon = daemon
        self.notifier = daemon.get_notifier()
        self.reloader = reloader

    def run(self):
        try:
            self.daemon.run()
        except KeyboardInterrupt as e:
            self.notifier.send(subject="Shutting down")
        except Exception as e:
            self.notifier.send(
                subject="Alert!",
                message="An unexpected error occurred: {}".format(
                    traceback.format_exc()))
        self.exit_gracefully()

    def exit(self):
        time.sleep(2)
        sys.exit(0)

    def exit_gracefully(self):
        subprocess.call([self.reloader])
        self.exit()
