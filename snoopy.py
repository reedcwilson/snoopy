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

# imp.load_source('catcher', './{}/capture.py'.format(sys.platform))
from darwin import capture as catcher

home              = os.getenv("HOME")
directory         = '{}/code/snoopy'.format(home)
installation_path = '{}/dist/snoopy'.format(directory)
debug_file        = '{}/log'.format(directory)
launchd_path      = '{}/Library/LaunchAgents'.format(home)


def get_reloader():
    filename = 'a.out'
    if hasattr(sys, '_MEIPASS'):
        # PyInstaller >= 1.6
        os.chdir(sys._MEIPASS)
        filename = os.path.join(sys._MEIPASS, filename)
    elif '_MEIPASS2' in os.environ:
        # PyInstaller < 1.6 (tested on 1.5 only)
        os.chdir(os.environ['_MEIPASS2'])
        filename = os.path.join(os.environ['_MEIPASS2'], filename)
    else:
        os.chdir(dirname(sys.argv[0]))
        filename = os.path.join(dirname(sys.argv[0]), filename)
    return filename


def debug(message):
    with open(debug_file, 'a') as f:
        f.write('{}\n'.format(message))


def get_plist_filename(s=None):
    suffix = '.{}'.format(s) if s else ""
    return 'com.reedcwilson.snoopy{}.plist'.format(suffix)


class GracefulKiller:
    def __init__(self, reloader_filename):
        signal.signal(signal.SIGHUP, self.exit_gracefully)
        signal.signal(signal.SIGINT, self.exit_gracefully)
        signal.signal(signal.SIGTERM, self.exit_gracefully)
        self.reloader = reloader_filename

    def exit(self):
        time.sleep(2)
        sys.exit(0)

    def exit_gracefully(self, signum, frame):
        notifier.send(subject="Shutting down")
        pid = os.fork()
        if pid == 0:
            subprocess.call([self.reloader])
        self.exit()


class ConfigFileEventHandler(PatternMatchingEventHandler):
    def __init__(self):
        PatternMatchingEventHandler.__init__(
            self,
            patterns=["*com.reedcwilson.snoopy.plist*"],
            ignore_directories=True)

    def on_any_event(self, event):
        message = "The config file has been tampered with: {}".format(event.src_path)
        notifier.send(
                subject="Alert!",
                message=message)
        filename = get_plist_filename()
        shutil.copy(
            '{}/{}'.format(directory, filename),
            '{}/{}'.format(launchd_path, filename))


class InstallationEventHandler(PatternMatchingEventHandler):
    def __init__(self):
        PatternMatchingEventHandler.__init__(
            self,
            patterns=["*"],
            ignore_directories=True)

    def on_any_event(self, event):
        message = "The installation directory has been tampered with. file: {}".format(event.src_path)
        notifier.send(
                subject="Alert!",
                message=message)


class MyDaemon():
    killer = None

    def __init__(self, killer):
        self.killer = killer

    def run(self):
        self.observer = Observer()
        config_event_handler = ConfigFileEventHandler()
        installation_event_handler = InstallationEventHandler()
        self.observer.schedule(config_event_handler, launchd_path, recursive=False)
        self.observer.schedule(installation_event_handler, installation_path, recursive=False)
        self.observer.start()
        while True:
            catcher.capture(directory)
            notifier.send_screenshots()
            time.sleep(random.randint(120, 600))


def main():
    notifier.send(subject="Starting up")
    killer = GracefulKiller(get_reloader())
    daemon = MyDaemon(killer)
    daemon.run()


if __name__ == "__main__":
    main()
