import psutil
import threading
import time
import random

from linux.runas import get_env


class Enforcer:
    def __init__(self, user, notifier):
        self.notifier = notifier
        self.user = user

    def valid_vars(self, user, env):
        # display variables need to be correct so we can take screenshots using
        # the correct x
        return (env['DISPLAY'] == ':0' and
                env['XAUTHORITY'] == '/home/{}/.Xauthority'.format(
                    user))

    def valid_logins(self, users):
        return (len(users) == 1 and users[0].name == self.user)

    def run(self):
        while True:
            # get local logins (tty instead of pts)
            users = [user for user in psutil.users()
                     if user.terminal.startswith('tty')]
            if not self.valid_logins(users):
                msg = 'found invalid logins: {}'.format(users)
                self.notifier.send(subject="Alert!", message=msg)
            env, record = get_env(self.user)
            if not self.valid_vars(self.user, env):
                msg = 'display vars are incorrect: {}'.format(env)
                self.notifier.send(subject="Alert!", message=msg)
            time.sleep(random.randint(2, 10) * 60)

    def run_async(self):
        t = threading.Thread(target=self.run)
        t.daemon = True
        t.start()
