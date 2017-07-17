#!/usr/bin/env python

import imp
import sys
import os
import time
import signal
import random
import notifier
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
    def __init__(self, reloader_filename, notifier):
        signal.signal(signal.SIGHUP, self.exit_gracefully)
        signal.signal(signal.SIGINT, self.exit_gracefully)
        signal.signal(signal.SIGTERM, self.exit_gracefully)
        self.reloader = reloader_filename
        self.notifier = notifier

    def exit(self):
        time.sleep(1)
        sys.exit(0)

    def exit_gracefully(self, signum, frame):
        self.notifier.send(subject="Shutting down")
        pid = os.fork()
        if pid == 0:
            subprocess.call([self.reloader])
        self.exit()


class ConfigFileEventHandler(PatternMatchingEventHandler):
    def __init__(self, notifier, install_dir, launchd_dir, plist_filename):
        self.notifier = notifier
        self.install_dir = install_dir
        self.launchd_dir = launchd_dir
        self.plist_filename = plist_filename
        PatternMatchingEventHandler.__init__(
            self,
            patterns=["*com.reedcwilson.snoopy.plist*"],
            ignore_directories=True)

    def on_any_event(self, event):
        message = "The config file has been tampered with: {}".format(event.src_path)
        self.notifier.send(
                subject="Alert!",
                message=message)
        config = ""
        with open('{}/{}'.format(self.install_dir, self.plist_filename), 'r') as f:
            config = f.read().replace("%INSTALL_DIR%", self.install_dir)
        with open('{}/{}'.format(self.launchd_dir, self.plist_filename), 'w') as f:
            f.write(config)


class InstallationEventHandler(PatternMatchingEventHandler):
    def __init__(self, notifier):
        self.notifier = notifier
        PatternMatchingEventHandler.__init__(
            self,
            patterns=["*"],
            ignore_directories=True)

    def on_any_event(self, event):
        message = "The installation directory has been tampered with. file: {}".format(event.src_path)
        self.notifier.send(
                subject="Alert!",
                message=message)


class MyDaemon():
    killer = None

    def __init__(self):
        self.killer = GracefulKiller(get_reloader())
        notifier.send(subject="Starting up")

    def run(self):
        self.observer = Observer()
        config_event_handler = ConfigFileEventHandler(notifier, directory, launchd_path, get_plist_filename())
        installation_event_handler = InstallationEventHandler(notifier)
        self.observer.schedule(config_event_handler, launchd_path, recursive=False)
        self.observer.schedule(installation_event_handler, installation_path, recursive=False)
        self.observer.start()
        while True:
            catcher.capture(directory)
            notifier.send_screenshots()
            time.sleep(random.randint(120, 600))


def main():
    daemon = MyDaemon()
    daemon.run()


if __name__ == "__main__":
    main()
