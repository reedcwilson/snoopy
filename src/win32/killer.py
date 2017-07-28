#!/usr/local/env python

import sys
import zerorpc
import traceback


class GracefulKiller:
    def __init__(self, daemon, port):
        self.daemon = daemon
        self.notifier = daemon.get_notifier()
        self.port = port

    def run(self):
        try:
            self.daemon.run()
        except KeyboardInterrupt as e:
            print("Shutting down...")
            self.notifier.send(subject="Shutting down...")
        except Exception as e:
            self.notifier.send(
                subject="Alert!",
                message="An unexpected error occurred: {}".format(
                    traceback.format_exc()))
        self.exit()

    def exit(self):
        c = zerorpc.Client()
        c.connect("tcp://127.0.0.1:{}".format(self.port))
        print('relaunching')
        c.relaunch()
        sys.exit(0)
