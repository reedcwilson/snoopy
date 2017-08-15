#!/usr/local/env python

import signal
import sys
import zerorpc
import logging


class GracefulKiller:
    def __init__(self, notifier, port):
        signal.signal(signal.SIGHUP, self.exit)
        signal.signal(signal.SIGINT, self.exit)
        signal.signal(signal.SIGTERM, self.exit)
        self.notifier = notifier
        self.port = port

    def exit(self, signum, frame):
        self.notifier.send(subject="Shutting down")
        c = zerorpc.Client()
        c.connect("tcp://127.0.0.1:{}".format(self.port))
        logging.info('relaunching')
        c.relaunch()
        sys.exit(0)
