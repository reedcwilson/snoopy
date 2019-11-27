#!/usr/bin/env python

import time
import random
import base64
import sys
import os
from os.path import join, basename
import uuid
import traceback
import gc
from watchdog.observers import Observer
from .install_alert import InstallationEventHandler
from .secrets_manager import SecretsManager
from .notifier import Notifier


class Daemon():
    def __init__(
            self,
            mail_config,
            secret_key,
            installation_path,
            screenshots_directory,
            catcher):
        self.sleep_seconds = sys.maxsize
        self.catcher = catcher
        self.screenshots_directory = screenshots_directory
        config_filename = mail_config
        secret_key_raw = base64.b64decode(secret_key).decode()
        mail_secrets_manager = SecretsManager(secret_key_raw, config_filename)
        self.notifier = Notifier(mail_secrets_manager, screenshots_directory)
        installation_event_handler = InstallationEventHandler(self.notifier)
        self.observer = Observer()
        self.observer.schedule(
            installation_event_handler,
            installation_path,
            recursive=True)
        # if the messages get too large, you might get a broken pipe exception
        self.likelihood = .35  # 35% chance
        self.max_images = 20  # don't keep too many images
        self.images_dir = join(self.screenshots_directory, 'captured_images')

    def should_execute(self):
        return True

    def execute(self):
        ''' 
        method to be overriden by derived classes for platform specific
        executions
        '''
        pass

    def get_notifier(self):
        return self.notifier

    def setup(self):
        print("perform setup functionality in your subclass")

    def store_images(self, filenames):
        if not os.path.exists(self.images_dir):
            os.makedirs(self.images_dir)
        for filename in filenames:
            new_filename = "{}-{}".format(uuid.uuid4(), basename(filename))
            os.rename(filename, join(self.images_dir, new_filename))
        return len(os.listdir(self.images_dir)) > self.max_images

    def send(self):
        filenames = [
            join(self.images_dir, n)
            for n
            in os.listdir(self.images_dir)
        ]
        if len(filenames) == 0:
            return
        try:
            self.notifier.send_screenshots(filenames)
        except:
            try:
                msg = 'Failed to send {} screenshots'.format(len(filenames))
                self.notifier.send(
                    subject='Warning',
                    message=msg)
            except:
                pass
        for filename in filenames:
            os.remove(filename)

    def sleep(self):
        gc.collect()  # attempt to keep memory low
        self.sleep_seconds = random.randint(120, 2160)  # 2-36 min
        time.sleep(self.sleep_seconds)

    def run(self):
        self.setup()
        self.observer.start()
        while True:
            # if we sleep at the beginning, then multiple restarts won't
            # attempt to send tons of emails
            self.sleep()
            self.execute()
            if self.should_execute():
                names = []
                try:
                    # catchers needs to conform to the same interface
                    names = self.catcher.capture(self.screenshots_directory)
                    if len(names) == 0:
                        continue
                except Exception:
                    self.notifier.send(
                        'Alert!',
                        'Unable to take screenshot: {}'.format(
                            traceback.format_exc()))
                    continue
                # limit # of emails by holding onto screenshots
                should_send = self.store_images(names)
                if should_send or random.random() < self.likelihood:
                    self.send()
            # send a ping email if we haven't sent an email in a while
            self.notifier.ping()
