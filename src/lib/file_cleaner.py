#!/usr/local/env python

import os
import time
from datetime import datetime, timedelta

class Notifier():
    def send(self, subject=None, message=None):
        print(subject, message)


class FileCleaner(object):
    def __init__(self, filename, notifier):
        self.filename = filename
        self.notifier = notifier

    def notify(self, entry):
        self.notifier.send(
            subject='Alert!',
            message='{} has been added to the {} file'.format(
                entry,
                self.filename
            )
        )

    def clean(self, entry, last_check):
        modified_time = datetime.fromtimestamp(os.stat(self.filename).st_mtime)
        if modified_time > last_check:
            lines = []
            with open(self.filename, 'r') as f:
                lines = f.readlines()
            matches = [l for l in lines if entry in l]
            if len(matches) > 0:
                self.notify(entry)
                for m in matches:
                    lines.remove(m)
                with open(self.filename, 'w') as f:
                    f.writelines(lines)


if __name__ == "__main__":
    notifier = Notifier()
    file_cleaner = FileCleaner('/etc/hosts', notifier)
    while True:
        file_cleaner.clean('api.mailgun.net', datetime.today() - timedelta(seconds=10))
        time.sleep(1)
