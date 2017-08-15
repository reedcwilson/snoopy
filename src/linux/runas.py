#!/usr/bin/env python

import os
import pwd
import re
import subprocess


class FailedOperationException(Exception):
    pass


def demote(user_uid, user_gid):
    def result():
        os.setgid(user_gid)
        os.setuid(user_uid)
    return result


def run_cmd(user_uid, user_gid, args, cwd, env):
    process = subprocess.Popen(
        args,
        preexec_fn=demote(user_uid, user_gid),
        cwd=cwd,
        env=env,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )
    out, err = process.communicate()
    if err.decode() != '':
        raise FailedOperationException(err.decode())
    return out.decode()


def dictify(string):
    return {parts[0]: parts[1] for parts in
            [line.split('=') for line in string.splitlines() if line]
            }


def get_env(user, cwd="/"):
    record = pwd.getpwnam(user)
    env_res = run_cmd(
        record.pw_uid,
        record.pw_gid,
        ["env"],
        '/',
        os.environ.copy()
    )
    ps = run_cmd(
        record.pw_uid,
        record.pw_gid,
        ["ps", "-fwu", record.pw_name],
        '/',
        os.environ.copy()
    )
    dbus_addr = re.findall(r'.*[d]bus.*--address=(.*)', ps, re.MULTILINE)[0]
    env = dictify(env_res)
    env['HOME'] = record.pw_dir
    env['LOGNAME'] = record.pw_name
    env['PWD'] = cwd
    env['USER'] = record.pw_name
    env['DBUS_SESSION_BUS_ADDRESS'] = dbus_addr
    return env, record


def runas(user, cwd, args=None, getenv=True):
    env, record = get_env(user, cwd)
    return run_cmd(record.pw_uid, record.pw_gid, args, cwd, env)


if __name__ == '__main__':
    runas('parallels', '/', ['echo', 'hello'])
