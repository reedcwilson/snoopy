#!/usr/bin/env python

import zerorpc
import time
import threading
import subprocess


class ServiceReloader(object):
    def __init__(self, name, reloader, service_file, port, notifier):
        self.name = name
        self.reloader = reloader
        self.service_file = service_file
        self.notifier = notifier
        server = zerorpc.Server(self)
        server.bind('tcp://127.0.0.1:{}'.format(port))
        server.run()

    def load(self):
        process = subprocess.Popen([
            self.reloader,
            self.service_file,
            self.name],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE)
        process.wait()

    def do_cmd(self, args, substr):
        process = subprocess.Popen(
            args,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE)
        stdout, stderr = process.communicate()
        return stderr.decode() == '' and substr in stdout.decode()

    def get_status(self):
        active = self.do_cmd([
            'systemctl',
            'is-active',
            self.name],
            'active')
        enabled = self.do_cmd([
            'systemctl',
            'is-enabled',
            self.name],
            'enabled')
        return active and enabled

    def spawn(self, func):
        t = threading.Thread(target=func)
        t.daemon = True
        t.start()

    def handle(self):
        time.sleep(2)
        status = self.get_status()
        if not status:
            msg = 'service is unloaded - attempting to load'
            self.notifier.send('Alert!', msg)
            self.load()

    def relaunch(self):
        print('received request to relaunch')
        self.spawn(self.handle)
        print('relaunched')
        return 'relaunched'
