#!/usr/bin/env python

from linux.runas import runas


def is_available(user):
    return 'false' in runas(user, '/', [
        'gdbus',
        'call',
        '-e',
        '-d',
        'com.canonical.Unity',
        '-o',
        '/com/canonical/Unity/Session',
        '-m',
        'com.canonical.Unity.Session.IsLocked'
    ])


if __name__ == '__main__':
    import time
    while True:
        print(is_available('parallels'))
        time.sleep(1)
