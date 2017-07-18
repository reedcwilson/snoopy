#!/usr/bin/env python

from watchdog.events import PatternMatchingEventHandler


class InstallationEventHandler(PatternMatchingEventHandler):
    def __init__(self, notifier):
        self.notifier = notifier
        PatternMatchingEventHandler.__init__(
            self,
            patterns=["*"],
            ignore_directories=True)

    def on_any_event(self, event):
        message = """The installation directory has been tampered with.
        file: {}""".format(event.src_path)
        self.notifier.send(
            subject="Alert!",
            message=message)
