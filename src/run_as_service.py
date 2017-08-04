import subprocess
import os
import time

script = 'src/win32/should_execute.py'
_directory            = os.path.dirname(os.path.abspath(__file__))
parentdir             = _directory
nssm_file             = r'{}\src\win32\nssm.exe'.format(parentdir)


def nssm(args, wait=True):
    print(nssm_file)
    cmd = [nssm_file]
    cmd.extend(args)
    c = subprocess.Popen(cmd)
    if wait:
        c.wait()


def cleanup(serv):
    print("cleaning up...")
    nssm(['stop', serv], False)
    cmd = subprocess.Popen(['sc', 'delete', serv])
    cmd.wait()
    time.sleep(1)


def install(serv, exe, path):
    print("installing service...")
    nssm([
        'install',
        serv,
        'python',
        exe
    ])
    # nssm([
    #     'install',
    #     serv,
    #     exe
    # ])
    nssm(['set', serv, 'AppStopMethodSkip', '6'])
    nssm(['set', serv, 'AppDirectory', '{}'.format(path)])
    nssm(['set', serv, 'AppStdout', r'{}\{}.out'.format(path, serv)])
    nssm(['set', serv, 'AppStderr', r'{}\{}.err'.format(path, serv)])


def start(serv):
    print("starting service...")
    nssm(['start', serv])


if __name__ == '__main__':
    service = 'should_execute'
    script = r'{}\src\win32\test.py'.format(parentdir)
    # script = r'{}\dist\should_execute\should_execute.exe'.format(parentdir)
    cleanup(service)
    try:
        os.remove('{}.err'.format(service))
        os.remove('{}.out'.format(service))
    except:
        pass
    install(service, script, parentdir)
    start(service)
