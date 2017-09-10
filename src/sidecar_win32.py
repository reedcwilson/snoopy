from win32.service_reloader import ServiceReloader
from win32.killer import GracefulKiller
import threading
import time

directory         = 'C:\\Users\\Reed\\code\\snoopy'
installation_path = r'{}\dist\snoopy'.format(directory)
service           = 'snoopy'


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


def create_reloader():
    ServiceReloader(
        r'{}\nssm.exe'.format(installation_path),
        service,
        directory,
        [r'{}\{}.exe'.format(installation_path, service)],
        7110
    )


def main():
    t = threading.Thread(target=create_reloader)
    t.daemon = True
    t.start()
    killer = GracefulKiller(
        Daemon(),
        7111)
    killer.run()


if __name__ == '__main__':
    main()
