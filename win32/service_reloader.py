import zerorpc
from launcher import NssmLauncher
import threading
import time


class ServiceReloader(object):
    def __init__(self, service_utility, name, directory, exe_args, port):
        self.launcher = NssmLauncher(
            service_utility,
            name,
            directory,
            exe_args)
        server = zerorpc.Server(self)
        server.bind('tcp://127.0.0.1:{}'.format(port))
        server.run()

    def load(self):
        time.sleep(1)
        self.launcher.install()
        time.sleep(2)
        self.launcher.start()

    def reload(self):
        time.sleep(1)
        self.launcher.remove()
        self.launcher.install()
        time.sleep(2)
        self.launcher.start()

    def spawn(self, func):
        t = threading.Thread(target=func)
        t.daemon = True
        t.start()

    def relaunch(self):
        print('received request to relaunch')
        status = self.launcher.get_status()
        if status == 'SERVICE_STOPPED' or status == 'SERVICE_STOP_PENDING':
            self.spawn(self.reload)
        elif status == 'NOT_LOADED':
            self.spawn(self.load)
        else:
            return "noop"
        print('relaunched')
        return 'relaunched'


if __name__ == '__main__':
    pass
