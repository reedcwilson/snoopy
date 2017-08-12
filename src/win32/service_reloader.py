import zerorpc
import subprocess
import threading
import time

# from win32.launcher import NssmLauncher


class NssmLauncher(object):
    def __init__(self, nssm_file, service, directory, exe_args):
        self.nssm_file = nssm_file
        self.service = service
        self.directory = directory
        self.exe_args = exe_args

    def nssm(self, args):
        cmd = [self.nssm_file]
        cmd.extend(args)
        return subprocess.check_output(cmd).decode()

    def nssm_set(self, args):
        cmd = ['set', self.service]
        cmd.extend(args)
        self.nssm(cmd)

    def get_status(self):
        try:
            status = self.nssm(['status', self.service])
            return status.replace('\0', '').strip()
        except subprocess.CalledProcessError:
            return 'NOT_LOADED'

    def stop(self):
        self.nssm(['stop', self.service])

    def remove(self):
        subprocess.check_output(['sc', 'delete', self.service])

    def install(self):
        args = [
            'install',
            self.service
        ]
        args.extend(self.exe_args)
        self.nssm(args)
        self.nssm_set(['AppStopMethodSkip', '6'])
        self.nssm_set(['AppDirectory', '{}'.format(self.directory)])
        self.nssm_set(['AppStdout', r'{}\{}.out'.format(
            self.directory, self.service)])
        self.nssm_set(['AppStderr', r'{}\{}.err'.format(
            self.directory, self.service)])

    def start(self):
        self.nssm(['start', self.service])


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
