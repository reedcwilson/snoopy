#!/usr/bin/env python

import time
import random
import base64
import sys
import os
import uuid
import traceback
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
        print(installation_path)
        self.sleep_seconds = sys.maxsize
        self.catcher = catcher
        self.screenshots_directory = screenshots_directory
        config_filename = mail_config
        secret_key_raw = base64.b64decode(secret_key).decode()
        mail_secrets_manager = SecretsManager(secret_key_raw, config_filename)
        self.notifier = Notifier(mail_secrets_manager)
        installation_event_handler = InstallationEventHandler(self.notifier)
        self.observer = Observer()
        self.observer.schedule(
            installation_event_handler,
            installation_path,
            recursive=True)
        self.notifier.send(subject="Starting up")
        self.likelihood = .5  # 50% chance
        self.max_images = 15  # don't keep too many images
        self.images_dir = 'captured_images'

    def should_execute(self):
        return True

    def get_notifier(self):
        return self.notifier

    def setup(self):
        print("perform setup functionality in your subclass")

    def store_images(self, filenames):
        if not os.path.exists(self.images_dir):
            os.makedirs(self.images_dir)
        for filename in filenames:
            new_filename = "{}-{}".format(uuid.uuid4(), filename)
            os.rename(filename, os.path.join(self.images_dir, new_filename))
        return len(os.listdir()) > self.max_images

    def send(self):
        filenames = os.listdir(self.images_dir)
        self.notifier.send_screenshots(filenames)
        for filename in filenames:
            os.remove(filename)

    def run(self):
        self.setup()
        self.observer.start()
        while True:
            if self.should_execute():
                names = []
                # catchers needs to conform to the same interface
                try:
                    names = self.catcher.capture(self.screenshots_directory)
                except Exception:
                    self.notifier.send(
                        'Alert!',
                        'Unable to take screenshot: {}'.format(
                            traceback.format_exc()))
                # limit # of emails by holding onto screenshots
                should_send = self.store_images(names)
                if should_send or random.random() < self.likelihood:
                    self.send()
            self.sleep_seconds = random.randint(120, 1080)  # 2-18 min
            time.sleep(self.sleep_seconds)
