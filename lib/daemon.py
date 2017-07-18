#!/usr/bin/env python

import time
import random
import base64
from watchdog.observers import Observer
from .install_alert import InstallationEventHandler
from .secrets_manager import SecretsManager
from .notifier import Notifier
from .file_finder import get_embedded_filename


class Daemon():
    def __init__(
            self,
            mail_config,
            secret_key,
            installation_path,
            screenshots_directory,
            catcher):
        self.catcher = catcher
        self.screenshots_directory = screenshots_directory
        config_filename = get_embedded_filename(mail_config)
        secret_key_raw = base64.b64decode(secret_key).decode()
        mail_secrets_manager = SecretsManager(secret_key_raw, config_filename)
        self.notifier = Notifier(mail_secrets_manager)
        installation_event_handler = InstallationEventHandler(self.notifier)
        self.observer = Observer()
        self.observer.schedule(
            installation_event_handler,
            installation_path,
            recursive=False)
        self.notifier.send(subject="Starting up")

    def setup(self):
        print("perform setup functionality in your subclass")

    def run(self):
        self.observer.start()
        while True:
            # catcher needs to conform to the same interface
            filenames = self.catcher.capture(self.screenshots_directory)
            self.notifier.send_screenshots(filenames)
            time.sleep(random.randint(120, 600))
