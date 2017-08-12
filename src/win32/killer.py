#!/usr/local/env python

import sys
import zerorpc
import traceback
import logging

known_errors = [
    "An attempt was made to reference a token that does not exist"
]


def known_error(e):
    message = str(e)
    for err in known_errors:
        if err in message:
            return True
    return False


class GracefulKiller:
    def __init__(self, daemon, port):
        self.daemon = daemon
        self.notifier = daemon.get_notifier()
        self.port = port

    def run(self):
        try:
            self.daemon.run()
        except KeyboardInterrupt as e:
            logging.info("Shutting down...")
            self.notifier.send(subject="Shutting down...")
        except Exception as e:
            if not known_error(e):
                self.notifier.send(
                    subject="Alert!",
                    message="An unexpected error occurred: {}".format(
                        traceback.format_exc()))
        self.exit()

    def exit(self):
        c = zerorpc.Client()
        c.connect("tcp://127.0.0.1:{}".format(self.port))
        logging.info('relaunching')
        c.relaunch()
        sys.exit(0)
