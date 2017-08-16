#!/usr/bin/env python

import threading
import time

from linux.reloader import ServiceReloader
from linux.killer import GracefulKiller
from lib.file_finder import get_embedded_filename

directory         = 'HOME_DIRECTORY'
service           = 'snoopy.service'
reloader_script   = 'start.sh'
# reloader_script   = '{}/start.sh'.format(directory)


class Notifier():
    def send(self, subject, message=""):
        pass


class Daemon():
    def __init__(self):
        self.notifier = Notifier()

    def get_notifier(self):
        return self.notifier

    def run(self):
        while True:
            time.sleep(10)


def create_reloader(notifier):
    def reloader():
        ServiceReloader(
            service,
            get_embedded_filename(reloader_script),
            # '/home/parallels/code/snoopy/start.sh',
            get_embedded_filename(service),
            # '/home/parallels/code/snoopy/config/snoopy.service',
            7111,
            notifier
        )
    return reloader


def main():
    notifier = Notifier()
    reloader = create_reloader(notifier)
    t = threading.Thread(target=reloader)
    t.daemon = True
    t.start()
    GracefulKiller(
        notifier,
        7110)
    while True:
        time.sleep(10)


if __name__ == '__main__':
    main()
