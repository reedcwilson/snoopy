import subprocess


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


if __name__ == '__main__':
    pass
