from service_reloader import ServiceReloader
from killer import GracefulKiller
import threading
import time

directory         = r'C:\Users\rwilson\code\snoopy'
installation_path = r'{}\dist\snoopy'.format(directory)
secret_key        = 'SUPER_SECRET_KEY'
# secret_key        = 'U1VQRVJfU0VDUkVUX0tFWQ=='
service           = 'sidecar'


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
            time.sleep(3)
            print('ping')


def create_reloader():
    ServiceReloader(
        # r'{}\nssm.exe'.format(installation_path),
        r'{}\win32\nssm.exe'.format(directory),
        service,
        directory,
        # [r'{}\{}.exe'.format(installation_path, service)],
        ['python', r'{}\win32\{}.py'.format(directory, service)],
        7111
    )


if __name__ == "__main__":
    t = threading.Thread(target=create_reloader)
    t.daemon = True
    t.start()
    killer = GracefulKiller(
        Daemon(),
        secret_key,
        7110)
    killer.run()
